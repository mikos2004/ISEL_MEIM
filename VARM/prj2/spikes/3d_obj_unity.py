import numpy as np
import cv2
import cv2.aruco as aruco
import os
from collections import deque
import socket
import json
import time

UNITY_IP = '127.0.0.1'
PORT_FRAME = 5000
PORT_POSE = 5001
MAX_UDP = 60000

sock_frame = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_pose = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


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
    depths = pts_cam[:, 2]                                   # eixo Z da câmara
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
        self.marker_id = marker_id
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
                          depths_v, fill_color, alpha=0.45, edge_color=(255, 255, 255)):
    """
    Trata da oclusão dos objetos ao desenhá-los.
    """
    h, w = frame.shape[:2]

    # Cria array com os pontos 2D do polígono na ordem correcta
    poly = np.array([pts2d[i] for i in face_idx], dtype=np.int32)

    # Calcula profundidade média da face
    face_z = float(np.mean([depths_v[i] for i in face_idx]))

    # Cria uma máscara binária do polígono preenchido
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [poly], 255)

    # Depth-test: identifica pixels onde:
    depth_test = (depth_buffer > face_z) & (mask == 255)

    # Aplica a transparência
    overlay = frame.copy()
    cv2.fillPoly(overlay, [poly], fill_color)

    # Cria máscara de blending
    blend_mask = depth_test.astype(np.float32)[..., np.newaxis]

    # Combina a imagem original com o overlay
    frame[:] = (overlay * (alpha * blend_mask) +
                frame * (1 - alpha * blend_mask)).astype(np.uint8)

    # Actualiza o depth buffer
    depth_buffer[depth_test] = face_z

    # Desenha as arestas do polígono
    n = len(face_idx)
    for k in range(n):
        p1 = tuple(pts2d[face_idx[k]].astype(int))
        p2 = tuple(pts2d[face_idx[(k + 1) % n]].astype(int))
        cv2.line(frame, p1, p2, edge_color, 1)


# ---------------------------------------------------------------------------
# Cube
# ---------------------------------------------------------------------------

class Cube3D(VirtualObject):
    """Desenha um Cubo"""
    def __init__(self, marker_id, size=0.03, color=(0, 255, 255), position_offset=(0, 0, 0)):
        super().__init__(marker_id, position_offset)
        self.size = size
        self.color = color
        s = size / 2
        self.vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, -s, s], [-s, -s, s],
            [-s, s, -s], [s, s, -s], [s, s, s], [-s, s, s],
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
        self.size = size
        self.color = color
        s = size / 2
        h = size
        self.vertices = np.array([
            [-s, -s, 0], [s, -s, 0], [s, s, 0], [-s, s, 0],
            [0, 0, h],
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
        self.color = color
        N = 16
        self.N = N
        angles = [2 * np.pi * i / N for i in range(N)]
        bottom = [[radius * np.cos(a), radius * np.sin(a), 0.0] for a in angles]
        top = [[radius * np.cos(a), radius * np.sin(a), height] for a in angles]
        self.vertices = np.array(bottom + top, dtype=np.float32)
        # Faces laterais + bases
        self.side_faces = [(i, (i+1) % N, N + (i+1) % N, N + i) for i in range(N)]
        self.bottom_face = list(range(N-1, -1, -1))
        self.top_face = list(range(N, 2*N))

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
        self.size = size

        # Definir os vértices do cubo (base da casa)
        half = size / 2
        self.cube_vertices = np.array([
            [-half, -half, 0],  # 0: frente inferior esquerda
            [half, -half, 0],   # 1: frente inferior direita
            [half, half, 0],    # 2: frente superior direita
            [-half, half, 0],   # 3: frente superior esquerda
            [-half, -half, size],  # 4: trás inferior esquerda
            [half, -half, size],   # 5: trás inferior direita
            [half, half, size],    # 6: trás superior direita
            [-half, half, size],   # 7: trás superior esquerda
        ], dtype=np.float32)

        # Definir as faces do cubo
        self.cube_faces = [
            ([0, 1, 2, 3], (200, 180, 100)),  # face frontal
            ([4, 5, 6, 7], (150, 130, 80)),   # face traseira
            ([0, 1, 5, 4], (180, 160, 90)),   # face inferior
            ([2, 3, 7, 6], (220, 200, 120)),  # face superior
            ([0, 3, 7, 4], (170, 150, 85)),   # face esquerda
            ([1, 2, 6, 5], (190, 170, 95)),   # face direita
        ]

        # Vértices do telhado (pirâmide)
        roof_height = size * 0.8
        self.roof_vertices = np.array([
            [-half, -half, size],  # 0: base frente esquerda
            [half, -half, size],   # 1: base frente direita
            [half, half, size],    # 2: base trás direita
            [-half, half, size],   # 3: base trás esquerda
            [0, 0, size + roof_height],  # 4: topo do telhado
        ], dtype=np.float32)

        # Faces do telhado
        self.roof_faces = [
            ([0, 1, 4], (180, 100, 50)),   # frente
            ([1, 2, 4], (200, 120, 60)),   # direita
            ([2, 3, 4], (190, 110, 55)),   # trás
            ([3, 0, 4], (170, 90, 45)),    # esquerda
        ]

        # Combinar todos os vértices
        all_vertices = np.vstack([self.cube_vertices, self.roof_vertices])

        # Combinar todas as faces
        offset = len(self.cube_vertices)
        self.all_faces = []
        self.all_colors = []

        for indices, color in self.cube_faces:
            self.all_faces.append(indices)
            self.all_colors.append(color)

        for indices, color in self.roof_faces:
            self.all_faces.append([i + offset for i in indices])
            self.all_colors.append(color)

        self.all_vertices = all_vertices
        self.vertices = all_vertices

    def draw(self, frame, depth_buffer, camera_matrix, dist_coeffs, rvec, tvec):
        tvec_obj = apply_tvec_offset(rvec, tvec, self.position_offset)
        pts2d, depths = project_points(self.all_vertices, rvec, tvec_obj, camera_matrix, dist_coeffs)

        face_depths = [np.mean([depths[i] for i in face]) for face in self.all_faces]
        sorted_faces = sorted(zip(face_depths, self.all_faces, self.all_colors), reverse=True)

        for depth, face, color in sorted_faces:
            _draw_poly_with_depth(frame, depth_buffer, pts2d, face,
                                  depths, color, alpha=0.7)


# ---------------------------------------------------------------------------
# Sphere (adicionado para compatibilidade com o antigo 3d_obj_unity)
# ---------------------------------------------------------------------------

class Sphere3D(VirtualObject):
    """Desenha uma esfera 3D usando um círculo com gradiente"""
    def __init__(self, marker_id, radius=0.025, color=(0, 255, 0), position_offset=(0, 0.02, 0)):
        super().__init__(marker_id, position_offset)
        self.radius = radius
        self.color = color

    def draw(self, frame, depth_buffer, camera_matrix, dist_coeffs, rvec, tvec):
        """Desenha a esfera como um círculo projetado"""
        tvec_obj = apply_tvec_offset(rvec, tvec, self.position_offset)

        # Centro da esfera
        center_3d = np.array([[0, 0, 0]], dtype=np.float32)
        center_2d, _ = cv2.projectPoints(
            center_3d, rvec, tvec_obj, camera_matrix, dist_coeffs
        )
        center = tuple(center_2d[0][0].astype(int))

        # Calcular o raio projetado
        edge_3d = np.array([[self.radius, 0, 0]], dtype=np.float32)
        edge_2d, _ = cv2.projectPoints(
            edge_3d, rvec, tvec_obj, camera_matrix, dist_coeffs
        )
        edge = edge_2d[0][0]
        radius_px = int(np.linalg.norm(edge - center))
        radius_px = max(5, min(radius_px, 100))

        # Obter profundidade para depth buffer
        face_z = float(tvec_obj[2])

        # Criar máscara do círculo
        h, w = frame.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, center, radius_px, 255, -1)

        # Depth test
        depth_test = (depth_buffer > face_z) & (mask == 255)

        # Desenhar círculo com gradiente
        overlay = frame.copy()
        for r in range(radius_px, 0, -5):
            intensity = int(255 * (1 - r / radius_px))
            color_variant = (
                min(255, self.color[0] + intensity // 3),
                min(255, self.color[1] + intensity // 3),
                min(255, self.color[2] + intensity // 3)
            )
            cv2.circle(overlay, center, r, color_variant, -1)

        # Aplicar blending
        blend_mask = depth_test.astype(np.float32)[..., np.newaxis]
        frame[:] = (overlay * (0.6 * blend_mask) +
                    frame * (1 - 0.6 * blend_mask)).astype(np.uint8)

        depth_buffer[depth_test] = face_z

        # Adicionar brilho
        cv2.circle(frame, (center[0] - radius_px // 3, center[1] - radius_px // 3),
                   radius_px // 4, (255, 255, 255), -1)


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------

class ArucoDetectorWithVirtualObjects:
    def __init__(self, calibration_file="camera_calibration.xml"):
        self.calibration_file = calibration_file
        self.load_calibration()

        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.aruco_params = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(self.aruco_dict, self.aruco_params)

        self.virtual_objects = {}
        self.setup_virtual_objects()

        self._pose_history = {}
        self._smooth_n = 5
        self.marker_length = 0.05

    def setup_virtual_objects(self):
        """Configura objetos virtuais para cada ID (formato do 3d_obj)"""
        self.virtual_objects[0] = Cube3D(0, size=0.04, color=(0, 100, 255), position_offset=(0, 0, 0.02))
        self.virtual_objects[1] = House(1, 0.035, position_offset=(0, 0, 0))
        self.virtual_objects[2] = Pyramid3D(2, size=0.045, color=(255, 50, 255), position_offset=(0, 0, 0))
        self.virtual_objects[3] = Cylinder3D(3, radius=0.02, height=0.05, color=(178, 75, 255), position_offset=(0, 0, 0))
        self.virtual_objects[4] = Cube3D(4, size=0.035, color=(0, 100, 255), position_offset=(0, 0, 0.02))
        self.virtual_objects[5] = House(5, 0.035, position_offset=(0, 0, 0))

        # Adicionar também esferas para alguns IDs (opcional)
        self.virtual_objects[1] = Sphere3D(1, radius=0.025, color=(0, 255, 100), position_offset=(0, 0, 0.02))
        self.virtual_objects[5] = Sphere3D(5, radius=0.022, color=(0, 0, 255), position_offset=(0, 0, 0.02))

    def load_calibration(self):
        if os.path.exists(self.calibration_file):
            try:
                fs = cv2.FileStorage(self.calibration_file, cv2.FILE_STORAGE_READ)
                if fs.isOpened():
                    self.camera_matrix = fs.getNode("camera_matrix").mat()
                    self.dist_coeffs = fs.getNode("distortion_coefficients").mat()
                    fs.release()
                    print(f"[ok] Calibração carregada: {self.calibration_file}")
                    return
            except Exception as e:
                print(f"[erro] {e}")
        print("[aviso] Usando parâmetros de câmara padrão.")
        self.camera_matrix = np.array([[600, 0, 320], [0, 600, 240], [0, 0, 1]], dtype=np.float32)
        self.dist_coeffs = np.zeros((1, 5), dtype=np.float32)

    def _get_marker_corners_3d(self):
        L = self.marker_length / 2
        return np.array([[-L, L, 0], [L, L, 0], [L, -L, 0], [-L, -L, 0]], dtype=np.float32)

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
        """Detecta e desenha no frame (com depth buffer para oclusão)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
                obj_pts = self._get_marker_corners_3d()
                pts_2d = corner[0].astype(np.float32)
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
                      Cube3D(marker_id, size=0.03, color=(128, 128, 128), position_offset=(0, 0, 0.015))
                depth = obj.get_depth(rv, tv)
                detected.append((depth, marker_id, rv, tv, obj, pts_2d))

            # Renderizar do mais longe para o mais perto
            detected.sort(key=lambda x: x[0], reverse=True)

            for depth, marker_id, rv, tv, obj, pts_2d in detected:
                # Objecto virtual com depth buffer
                obj.draw(frame_out, depth_buffer, self.camera_matrix, self.dist_coeffs, rv, tv)
        else:
            self._pose_history.clear()

        self._draw_info_overlay(frame_out, ids)
        return frame_out, ids

    def detect_and_draw_poses_only(self, frame, draw_objects=False):
        """
        Detecta marcadores, estima poses e opcionalmente desenha objetos locais.
        Retorna também as poses para envio ao Unity.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)

        frame_out = frame.copy()

        # Depth buffer para oclusão
        h, w = frame.shape[:2]
        depth_buffer = np.full((h, w), np.inf, dtype=np.float32)

        rvecs_list = []
        tvecs_list = []

        if ids is not None and len(ids) > 0:
            aruco.drawDetectedMarkers(frame_out, corners, ids)

            # Recolher todos os objectos detectados
            detected = []
            for i, corner in enumerate(corners):
                marker_id = int(ids[i][0])
                obj_pts = self._get_marker_corners_3d()
                pts_2d = corner[0].astype(np.float32)
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

                # Guardar poses para envio
                rvecs_list.append(rv)
                tvecs_list.append(tv)

                obj = self.virtual_objects.get(marker_id) or \
                      Cube3D(marker_id, size=0.03, color=(128, 128, 128), position_offset=(0, 0, 0.015))
                depth = obj.get_depth(rv, tv)
                detected.append((depth, marker_id, rv, tv, obj))

            if draw_objects:
                # Renderizar do mais longe para o mais perto
                detected.sort(key=lambda x: x[0], reverse=True)
                for depth, marker_id, rv, tv, obj in detected:
                    obj.draw(frame_out, depth_buffer, self.camera_matrix, self.dist_coeffs, rv, tv)

        self._draw_info_overlay(frame_out, ids)

        # Adicionar indicador de envio UDP
        cv2.putText(frame_out, "SENDING TO UNITY | Port 5000/5001",
                    (10, frame.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 255), 1)

        return frame_out, ids, rvecs_list, tvecs_list

    def _draw_info_overlay(self, frame, ids):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (5, 5), (w - 5, 45), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)
        if ids is not None and len(ids) > 0:
            cv2.putText(frame,
                        f"Detected: {len(ids)} marker(s)",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 0), 1)
        else:
            cv2.putText(frame, "No markers detected",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 255), 1)

    def run_live(self, camera_id=0):
        """Executa detecção ao vivo e envia dados para Unity"""
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"[erro] Não foi possível abrir a câmara {camera_id}")
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        print("\n" + "=" * 60)
        print("   ARUCO AR — OCLUSÃO COM DEPTH BUFFER + UNITY UDP")
        print("=" * 60)
        print(f"\nEnviando dados UDP para {UNITY_IP}:")
        print(f"  Video Frames -> Porta {PORT_FRAME}")
        print(f"  Pose Data    -> Porta {PORT_POSE}")
        print("\nObjetos Virtuais configurados:")
        for marker_id, obj in self.virtual_objects.items():
            print(f"  ID {marker_id}: {obj.__class__.__name__}")
        print("\nComandos:")
        print("  'q' → Sair")
        print("  'd' → Alternar desenho local dos objetos")
        print("-" * 60)

        draw_locally = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)

            # Detectar marcadores e obter poses
            frame_out, ids, rvecs_list, tvecs_list = self.detect_and_draw_poses_only(frame, draw_locally)

            # ===== ENVIAR PARA UNITY =====
            # 1. Enviar frame comprimido
            send_frame_fragmented(sock_frame, frame_out, UNITY_IP, PORT_FRAME)

            # 2. Enviar poses de cada marcador detectado
            if ids is not None and len(ids) > 0:
                for i in range(len(ids)):
                    marker_id = int(ids[i][0])
                    if i < len(rvecs_list) and i < len(tvecs_list):
                        rvec = rvecs_list[i]
                        tvec = tvecs_list[i]

                        pose_data = {
                            'id': marker_id,
                            'rvec': rvec.flatten().tolist(),
                            'tvec': tvec.flatten().tolist()
                        }
                        msg = json.dumps(pose_data, separators=(',', ':')).encode()
                        sock_pose.sendto(msg, (UNITY_IP, PORT_POSE))

            cv2.imshow("ArUco AR — Occlusion + Unity", frame_out)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('d'):
                draw_locally = not draw_locally
                print(f"[info] Desenho local: {'ON' if draw_locally else 'OFF'}")

        cap.release()
        cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def send_frame_fragmented(sock, frame, ip, port):
    """Envia frame fragmentado via UDP"""
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
    data = buffer.tobytes()
    num_chunks = (len(data) + MAX_UDP - 1) // MAX_UDP
    for i in range(num_chunks):
        chunk = data[i * MAX_UDP:(i + 1) * MAX_UDP]
        header = i.to_bytes(2, 'big') + num_chunks.to_bytes(2, 'big')
        sock.sendto(header + chunk, (ip, port))


def generate_markers():
    """Função auxiliar para gerar imagens de marcadores ArUco"""
    output_dir = "aruco_markers"
    os.makedirs(output_dir, exist_ok=True)

    dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)

    for marker_id in [0, 1, 2, 3, 4, 5]:
        marker_img = aruco.generateImageMarker(dictionary, marker_id, 200)
        marker_path = os.path.join(output_dir, f"aruco_marker_{marker_id}.png")
        cv2.imwrite(marker_path, marker_img)
        print(f"[pass] Marcador {marker_id} salvo: {marker_path}")

    print(f"\nMarcadores salvos em '{output_dir}'")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 60)
    print("   ARUCO AR — OCLUSÃO 3D + UNITY UDP")
    print("=" * 60)

    print("\n1. Executar tracking com objetos virtuais (envio para Unity)")
    print("2. Gerar marcadores ArUco para imprimir")
    print("3. Sair")

    choice = '1'

    if choice == '1':
        if not os.path.exists("camera_calibration.xml"):
            print("\n[aviso] Sem calibração — usando valores padrão.")
            proceed = input("Continuar? (s/n): ").lower()
            if proceed != 's':
                return
        ArucoDetectorWithVirtualObjects("camera_calibration.xml").run_live()
    else:
        print("Saindo...")


if __name__ == "__main__":
    main()