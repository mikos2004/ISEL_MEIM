import numpy as np
import cv2
import cv2.aruco as aruco
import os
from collections import deque


# --------------------------------
# aux de oclusão
# --------------------------------

def project_points(vertices, rvec, tvec, camera_matrix, dist_coeffs):
    """Projecta vértices 3D e devolve coordenadas 2D + profundidade média."""
    pts2d, _ = cv2.projectPoints(vertices, rvec, tvec, camera_matrix, dist_coeffs)
    pts2d = pts2d.reshape(-1, 2)
    # Profundidade de cada vértice no referencial da câmara
    rmat, _ = cv2.Rodrigues(rvec)
    pts_cam = (rmat @ vertices.T).T + tvec.flatten()          # (N,3)
    depths  = pts_cam[:, 2]                                   # eixo Z da câmara
    return pts2d, depths


def apply_tvec_offset(rvec, tvec, offset):
    """Desloca tvec no referencial do marcador."""
    if not np.any(offset):
        return tvec
    rmat, _ = cv2.Rodrigues(rvec)
    return tvec + (rmat @ offset.reshape(3, 1))


# ---------------------------------------------------------------------------
# Classe base
# ---------------------------------------------------------------------------

class VirtualObject:
    def __init__(self, marker_id, position_offset=(0, 0, 0)):
        self.marker_id       = marker_id
        self.position_offset = np.array(position_offset, dtype=np.float32)

    def get_depth(self, rvec, tvec):
        """Get Depth

        Args:
            rvec: Vetor de rotação (3D).
            tvec: Vetor de translação (3D).

        Returns:
            float: Profundidade (coordenada Z) do objeto no sistema da câmera.
        """
        tvec_obj = apply_tvec_offset(rvec, tvec, self.position_offset)
        return float(tvec_obj[2])

    def draw(self, frame, depth_buffer, camera_matrix, dist_coeffs, rvec, tvec):
        """Desenha o obj"""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Auxiliares: renderizar um polígono com depth-test pixel-a-pixel
# ---------------------------------------------------------------------------

def _draw_poly_with_depth(frame, depth_buffer, pts2d, face_idx,
                          depths_v, fill_color, alpha=0.35, edge_color=(255, 255, 255)):
    """
    Trata da oclusão dos objetos ao desenhá-los.
    
    Args:
        frame : Imagem de destino (shape: H x W x 3) onde o objeto será desenhado.
        
        depth_buffer : Buffer de profundidade (shape: H x W) com os valores Z (distância à câmara)
            de cada pixel. Valores mais baixos estão mais próximos da câmara.
            
        pts2d : Lista de pontos 2D projectados que representam os vértices do polígono no 
                espaço da imagem.
        
        face_idx : Índices dos vértices que compõem a face (recoree aos pontos em pts2d).
                   Define a ordem dos pontos para formar o polígono.
        
        depths_v : Valores de profundidade (Z) para cada vértice em pts2d. 
                   A profundidade da face é calculada como a média destes valores.
        
        fill_color : Cor do polígono no formato (B, G, R)
        
        alpha : Factor de transparência
        
        edge_color : Cor das arestas do polígono no formato (B, G, R).
    
    """
    h, w = frame.shape[:2]  # Obtém altura e largura da imagem
    
    # Cria array com os pontos 2D do polígono na ordem correcta
    poly = np.array([pts2d[i] for i in face_idx], dtype=np.int32)

    # Calcula profundidade média da face (média das profundidades dos vértices)
    face_z = float(np.mean([depths_v[i] for i in face_idx]))

    # Cria uma máscara binária do polígono preenchido
    # 255 = dentro do polígono, 0 = fora
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [poly], 255)

    # Depth-test: identifica pixels onde:
    # 1. A face está mais próxima que o valor actual no buffer (face_z < depth_buffer)
    # 2. O pixel está dentro do polígono (mask == 255)
    depth_test = (depth_buffer > face_z) & (mask == 255)

    # Aplica a transparência
    overlay = frame.copy()
    cv2.fillPoly(overlay, [poly], fill_color)  # Preenche o polígono na cópia
    
    # Cria máscara de blending (0=transparente, 1=opaco) expandida para 3 canais
    blend_mask = depth_test.astype(np.float32)[..., np.newaxis]
    
    # Combina a imagem original com o overlay usando alpha blending
    # Apenas os pixels com blend_mask > 0 são afectados
    frame[:] = (overlay * (alpha * blend_mask) +
                frame   * (1 - alpha * blend_mask)).astype(np.uint8)

    # Actualiza o depth buffer nos pixels onde esta face foi desenhada
    # Define a profundidade da face para evitar que faces atrás dela sejam desenhadas
    depth_buffer[depth_test] = face_z

    # Desenha as arestas do polígono
    n = len(face_idx)  # Número de vértices da face
    for k in range(n):
        # Obtém os dois vértices consecutivos da aresta
        p1 = tuple(pts2d[face_idx[k]].astype(int))
        p2 = tuple(pts2d[face_idx[(k + 1) % n]].astype(int))  # (k+1)%n fecha o polígono
        cv2.line(frame, p1, p2, edge_color, 1)  # Desenha a aresta


# ---------------------------------------------------------------------------
# Cube
# ---------------------------------------------------------------------------

class Cube3D(VirtualObject):
    """Desenha um Cubo"""
    def __init__(self, marker_id, size=0.03, color=(0, 255, 255), position_offset=(0, 0, 0)):
        super().__init__(marker_id, position_offset)
        self.size  = size
        self.color = color
        s = size / 2
        self.vertices = np.array([
            [-s, -s, -s], [ s, -s, -s], [ s, -s,  s], [-s, -s,  s],
            [-s,  s, -s], [ s,  s, -s], [ s,  s,  s], [-s,  s,  s],
        ], dtype=np.float32)
        # Cada face tem os vértices em ordem CCW quando vista de fora
        self.faces = [
            (3, 2, 1, 0),  # inferior  (normal -Y)
            (4, 5, 6, 7),  # superior  (normal +Y)
            (0, 1, 5, 4),  # traseira  (normal -Z)
            (2, 3, 7, 6),  # frontal   (normal +Z)
            (3, 0, 4, 7),  # esquerda  (normal -X)
            (1, 2, 6, 5),  # direita   (normal +X)
        ]

    def draw(self, frame, depth_buffer, camera_matrix, dist_coeffs, rvec, tvec):
        tvec_obj = apply_tvec_offset(rvec, tvec, self.position_offset)
        pts2d, depths = project_points(self.vertices, rvec, tvec_obj, camera_matrix, dist_coeffs)

        # Ordenar faces por profundidade média (painter's algorithm: longe→perto)
        face_depths = [np.mean([depths[i] for i in f]) for f in self.faces]
        sorted_faces = [f for _, f in sorted(zip(face_depths, self.faces), reverse=True)]

        for face in sorted_faces:
            _draw_poly_with_depth(frame, depth_buffer, pts2d, face,
                                  depths, self.color, alpha=0.45)


# ---------------------------------------------------------------------------
# Pyramid
# ---------------------------------------------------------------------------

class Pyramid3D(VirtualObject):
    """Desenha uma Piramide"""
    def __init__(self, marker_id, size=0.035, color=(255, 0, 255), position_offset=(0, 0, 0)):
        super().__init__(marker_id, position_offset)
        self.size  = size
        self.color = color
        s = size / 2
        h = size
        self.vertices = np.array([
            [-s, -s, 0], [ s, -s, 0], [ s,  s, 0], [-s,  s, 0],
            [ 0,  0, h],
        ], dtype=np.float32)
        self.faces = [
            (3, 2, 1, 0),  # base
            (0, 1, 4),
            (1, 2, 4),
            (2, 3, 4),
            (3, 0, 4),
        ]

    def draw(self, frame, depth_buffer, camera_matrix, dist_coeffs, rvec, tvec):
        tvec_obj = apply_tvec_offset(rvec, tvec, self.position_offset)
        pts2d, depths = project_points(self.vertices, rvec, tvec_obj, camera_matrix, dist_coeffs)

        face_depths = [np.mean([depths[i] for i in f]) for f in self.faces]
        sorted_faces = [f for _, f in sorted(zip(face_depths, self.faces), reverse=True)]

        for face in sorted_faces:
            _draw_poly_with_depth(frame, depth_buffer, pts2d, face,
                                  depths, self.color, alpha=0.45)


# ---------------------------------------------------------------------------
# Cylinder
# ---------------------------------------------------------------------------

class Cylinder3D(VirtualObject):
    """Desenha um Cilindro"""
    def __init__(self, marker_id, radius=0.02, height=0.05,
                 color=(255, 165, 0), position_offset=(0, 0, 0)):
        super().__init__(marker_id, position_offset)
        self.radius = radius
        self.height = height
        self.color  = color
        N = 16
        self.N = N
        angles = [2 * np.pi * i / N for i in range(N)]
        bottom = [[radius * np.cos(a), radius * np.sin(a), 0.0] for a in angles]
        top    = [[radius * np.cos(a), radius * np.sin(a), height] for a in angles]
        self.vertices = np.array(bottom + top, dtype=np.float32)
        # Faces laterais + bases
        self.side_faces = [(i, (i+1)%N, N+(i+1)%N, N+i) for i in range(N)]
        self.bottom_face = list(range(N-1, -1, -1))
        self.top_face    = list(range(N, 2*N))

    def draw(self, frame, depth_buffer, camera_matrix, dist_coeffs, rvec, tvec):
        tvec_obj = apply_tvec_offset(rvec, tvec, self.position_offset)
        pts2d, depths = project_points(self.vertices, rvec, tvec_obj, camera_matrix, dist_coeffs)

        all_faces = self.side_faces + [self.bottom_face, self.top_face]
        face_depths = [np.mean([depths[i] for i in f]) for f in all_faces]
        sorted_faces = [f for _, f in sorted(zip(face_depths, all_faces), reverse=True)]

        for face in sorted_faces:
            _draw_poly_with_depth(frame, depth_buffer, pts2d, face,
                                  depths, self.color, alpha=0.45)


# ---------------------------------------------------------------------------
# House
# ---------------------------------------------------------------------------

class House(VirtualObject):
    """
    Classe para desenhar uma casa 3D no canto do marcador ArUco.
    A casa é composta por um cubo (base) e um telhado piramidal.
    """
    def __init__(self, marker_id, size=0.05, position_offset=(0, 0, 0)):
        super().__init__(marker_id, position_offset)
        self.size = size  # tamanho da base do cubo
        
        # Definir os vértices do cubo (base da casa)
        # Sistema de coordenadas: X para a direita, Y para cima, Z para fora do marcador
        half = size / 2
        self.cube_vertices = np.array([
            [-half, -half, 0],  # 0: frente inferior esquerda
            [ half, -half, 0],  # 1: frente inferior direita
            [ half,  half, 0],  # 2: frente superior direita
            [-half,  half, 0],  # 3: frente superior esquerda
            [-half, -half, size],  # 4: trás inferior esquerda
            [ half, -half, size],  # 5: trás inferior direita
            [ half,  half, size],  # 6: trás superior direita
            [-half,  half, size],  # 7: trás superior esquerda
        ], dtype=np.float32)
        
        # Definir as faces do cubo (cada face é um quadrado)
        self.cube_faces = [
            ([0, 1, 2, 3], (200, 180, 100)),  # face frontal (castanho/claro)
            ([4, 5, 6, 7], (150, 130, 80)),   # face traseira (castanho escuro)
            ([0, 1, 5, 4], (180, 160, 90)),   # face inferior
            ([2, 3, 7, 6], (220, 200, 120)),  # face superior (onde o telhado assenta)
            ([0, 3, 7, 4], (170, 150, 85)),   # face esquerda
            ([1, 2, 6, 5], (190, 170, 95)),   # face direita
        ]
        
        # Vértices do telhado (pirâmide)
        # O telhado fica em cima do cubo (a partir de z = size até z = size + roof_height)
        roof_height = size * 0.8  # altura do telhado
        self.roof_vertices = np.array([
            [-half, -half, size],  # 0: base frente esquerda
            [ half, -half, size],  # 1: base frente direita
            [ half,  half, size],  # 2: base trás direita
            [-half,  half, size],  # 3: base trás esquerda
            [0, 0, size + roof_height],  # 4: topo do telhado
        ], dtype=np.float32)
        
        # Faces do telhado (triângulos)
        self.roof_faces = [
            ([0, 1, 4], (180, 100, 50)),   # frente
            ([1, 2, 4], (200, 120, 60)),   # direita
            ([2, 3, 4], (190, 110, 55)),   # trás
            ([3, 0, 4], (170, 90, 45)),    # esquerda
        ]
        
        # Combinar todos os vértices para o depth buffer
        all_vertices = np.vstack([self.cube_vertices, self.roof_vertices])
        
        # Combinar todas as faces
        offset = len(self.cube_vertices)
        self.all_faces = []
        self.all_colors = []
        
        # Adicionar faces do cubo
        for indices, color in self.cube_faces:
            self.all_faces.append(indices)
            self.all_colors.append(color)
        
        # Adicionar faces do telhado (com offset nos índices)
        for indices, color in self.roof_faces:
            self.all_faces.append([i + offset for i in indices])
            self.all_colors.append(color)
        
        self.all_vertices = all_vertices
        self.vertices = all_vertices  # Para compatibilidade com project_points
    
    def draw(self, frame, depth_buffer, camera_matrix, dist_coeffs, rvec, tvec):
        """
        Desenha a casa 3D na imagem com depth testing.
        """
        tvec_obj = apply_tvec_offset(rvec, tvec, self.position_offset)
        pts2d, depths = project_points(self.all_vertices, rvec, tvec_obj, camera_matrix, dist_coeffs)
        
        # Calcular profundidade média de cada face
        face_depths = [np.mean([depths[i] for i in face]) for face in self.all_faces]
        
        # Ordenar faces por profundidade (mais longe primeiro)
        sorted_faces = sorted(zip(face_depths, self.all_faces, self.all_colors), reverse=True)
        
        # Renderizar cada face com depth testing
        for depth, face, color in sorted_faces:
            
            # Desenhar a face com depth buffer
            _draw_poly_with_depth(frame, depth_buffer, pts2d, face, 
                                  depths, color, alpha=0.7)


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------

class ArucoDetectorWithVirtualObjects:
    def __init__(self, calibration_file="camera_calibration.xml"):
        self.calibration_file = calibration_file
        self.load_calibration()

        self.aruco_dict   = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.aruco_params = aruco.DetectorParameters()
        self.detector     = aruco.ArucoDetector(self.aruco_dict, self.aruco_params)

        self.virtual_objects = {}
        self.setup_virtual_objects()

        self._pose_history = {}
        self._smooth_n     = 5
        self.marker_length = 0.05

    def setup_virtual_objects(self):
        self.virtual_objects[0] = Cube3D(0,    size=0.04,   color=(0, 100, 255),  position_offset=(0, 0, 0.02))
        self.virtual_objects[1] = House(1, 0.035, position_offset=(0, 0, 0))
        self.virtual_objects[2] = Pyramid3D(2, size=0.045,  color=(255, 50, 255), position_offset=(0, 0, 0))
        self.virtual_objects[3] = Cylinder3D(3,radius=0.02, height=0.05, color=(178, 75, 255), position_offset=(0, 0, 0))
        self.virtual_objects[4] = Cube3D(4,    size=0.035,  color=(0, 100, 255),  position_offset=(0, 0, 0.02))
        self.virtual_objects[5] = House(5, 0.035, position_offset=(0, 0, 0))

    def load_calibration(self):
        if os.path.exists(self.calibration_file):
            try:
                fs = cv2.FileStorage(self.calibration_file, cv2.FILE_STORAGE_READ)
                if fs.isOpened():
                    self.camera_matrix = fs.getNode("camera_matrix").mat()
                    self.dist_coeffs   = fs.getNode("distortion_coefficients").mat()
                    fs.release()
                    print(f"[ok] Calibração carregada: {self.calibration_file}")
                    return
            except Exception as e:
                print(f"[erro] {e}")
        print("[aviso] Usando parâmetros de câmara padrão.")
        self.camera_matrix = np.array([[600,0,320],[0,600,240],[0,0,1]], dtype=np.float32)
        self.dist_coeffs   = np.zeros((1,5), dtype=np.float32)

    def _get_marker_corners_3d(self):
        L = self.marker_length / 2
        return np.array([[-L,L,0],[L,L,0],[L,-L,0],[-L,-L,0]], dtype=np.float32)

    def _get_marker_center(self, pts_2d):
        return tuple(np.mean(pts_2d, axis=0).astype(int))

    def _smooth_pose(self, marker_id, rvec, tvec):
        """Mediana móvel com deque de tamanho 5"""
        if marker_id not in self._pose_history:
            self._pose_history[marker_id] = {
                'rvecs': deque(maxlen=self._smooth_n),
                'tvecs': deque(maxlen=self._smooth_n)
            }
        self._pose_history[marker_id]['rvecs'].append(rvec.flatten())
        self._pose_history[marker_id]['tvecs'].append(tvec.flatten())

    def _get_smoothed_pose(self, marker_id):
        hist = self._pose_history.get(marker_id)
        if not hist or len(hist['rvecs']) == 0:
            return None, None
        rv = np.median(np.array(hist['rvecs']), axis=0).reshape(3, 1)
        tv = np.median(np.array(hist['tvecs']), axis=0).reshape(3, 1)
        return rv, tv

    def detect_and_draw(self, frame):
        gray   = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)

        frame_out = frame.copy()

        # Depth buffer inicializado a infinito
        h, w = frame.shape[:2]
        depth_buffer = np.full((h, w), np.inf, dtype=np.float32)

        if ids is not None and len(ids) > 0:
            aruco.drawDetectedMarkers(frame_out, corners, ids)

            # Recolher todos os objectos detectados com a sua profundidade
            detected = []
            for i, corner in enumerate(corners):
                marker_id = int(ids[i][0])
                obj_pts   = self._get_marker_corners_3d()
                pts_2d    = corner[0].astype(np.float32)
                ret, rvec, tvec = cv2.solvePnP(
                    obj_pts, pts_2d,
                    self.camera_matrix, self.dist_coeffs,
                    flags=cv2.SOLVEPNP_ITERATIVE
                )
                if not ret:
                    continue
                self._smooth_pose(marker_id, rvec, tvec)
                rv, tv = self._get_smoothed_pose(marker_id)
                if rv is None:
                    continue

                obj = self.virtual_objects.get(marker_id) or \
                      Cube3D(marker_id, size=0.03, color=(128,128,128), position_offset=(0,0,0.015))
                depth = obj.get_depth(rv, tv)
                detected.append((depth, marker_id, rv, tv, obj, pts_2d))

            # Renderizar do mais longe para o mais perto (painter's algorithm)
            detected.sort(key=lambda x: x[0], reverse=True)

            for depth, marker_id, rv, tv, obj, pts_2d in detected:
                # Objecto virtual com depth buffer
                obj.draw(frame_out, depth_buffer, self.camera_matrix, self.dist_coeffs, rv, tv)
        else:
            self._pose_history.clear()

        self._draw_info_overlay(frame_out, ids)
        return frame_out, ids

    def _draw_info_overlay(self, frame, ids):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (5,5), (w-5,45), (0,0,0), -1)
        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)
        if ids is not None and len(ids) > 0:
            cv2.putText(frame,
                        f"Detected: {len(ids)} marker(s)",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0,255,0), 1)
        else:
            cv2.putText(frame, "No markers detected",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0,0,255), 1)

    def run_live(self, camera_id=0):
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"[erro] Não foi possível abrir a câmara {camera_id}")
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        print("\n" + "="*60)
        print("   ARUCO AR — OCLUSÃO COM DEPTH BUFFER")
        print("="*60)
        for mid, obj in self.virtual_objects.items():
            print(f"  ID {mid}: {obj.__class__.__name__}")
        print("\n  'q' → Sair\n" + "-"*60)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame     = cv2.flip(frame, 1)
            frame_out, _ = self.detect_and_draw(frame)
            cv2.imshow("ArUco AR — Occlusion", frame_out)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "="*60)
    print("   ARUCO AR — OCLUSÃO 3D (depth buffer + back-face culling)")

    choice = '1'

    if choice == '1':
        if not os.path.exists("camera_calibration.xml"):
            print("\n[aviso] Sem calibração — usando valores padrão.")
            if input("Continuar? (s/n): ").lower() != 's':
                return
        ArucoDetectorWithVirtualObjects("camera_calibration.xml").run_live()


if __name__ == "__main__":
    main()