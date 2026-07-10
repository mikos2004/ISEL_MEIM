import cv2
import mediapipe as mp
import numpy as np
import time
import math
from collections import defaultdict
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions, RunningMode

# --- CONFIG ---
MODELO_LBPH_PATH = "code\\mod_4656_lbph_mpeg7.yml"
DETECTOR_TASK_PATH = 'code\\face_landmarker.task'
THRESHOLD_CONFIANCA = 165
MAX_PESSOAS = 3
TEMPO_ESTABILIZACAO = 5

LABEL_PESSOA = {
        8: "ATT Face 8",
        41: "Miguel",
        42: "Pedro",
}

OCULOS_PESSOA = {
        8: "oculos3.png",
        41: "oculos1.png",
        42: "oculos2.png",
}

def normalizar_face_mpeg7(face_bgr, landmarks, imagem_original_shape):
    """
    Normaliza a face de acordo com o padrão MPEG-7, com algumas alterações
    
    Args:
        face_bgr: Imagem da face recortada em BGR
        landmarks: Landmarks do MediaPipe (pontos faciais)
        imagem_original_shape: Dimensões da imagem original (h, w)
    
    Returns:
        face_normalizada: Imagem normalizada em grayscale com tamanho 46x56
    """
    # 1- converter para grayscale
    if len(face_bgr.shape) == 3:
        face_gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
    else:
        face_gray = face_bgr
    
    # 2- Extrair coordenadas dos olhos
    h, w = imagem_original_shape[:2]
    
    # REF: https://github.com/k-m-irfan/simplified_mediapipe_face_landmarks

    # Olho esquerdo (média entre canto externo e interno)
    
    left_eye_outer = landmarks[33]
    left_eye_inner = landmarks[133]
    left_eye_y = (left_eye_outer.y + left_eye_inner.y) / 2.0
    
    # Olho direito (média entre canto interno e externo)
    right_eye_inner = landmarks[362]
    right_eye_outer = landmarks[263]
    right_eye_y = (right_eye_inner.y + right_eye_outer.y) / 2.0
    
    # Altura média dos olhos
    eye_y = (left_eye_y + right_eye_y) / 2.0
    eye_y_pixel = int(eye_y * h)
    
    # MPEG-7
    #===========

    # 1- Tamanho da imagem
    # 46x56 estava a dar problemas nos niveis de confiança (~= 130)
    TARGET_WIDTH = 46
    TARGET_HEIGHT = 56
    # Posição em y dos olhos na imimggem final
    TARGET_EYE_Y = int(TARGET_HEIGHT * 0.4) # 0.4 pq (56*24)/100 ~= 40
    
    # 2- redimensionar img para 200x200
    resized_face = cv2.resize(face_gray, (TARGET_WIDTH, TARGET_HEIGHT), 
                               interpolation=cv2.INTER_LINEAR)
    
    # Calcula onde os olhos estão na imagem redimensionada
    height_ratio = TARGET_HEIGHT / h
    current_eye_y = eye_y_pixel * height_ratio
    
    # Calcula o deslocamento necessário para alinhar os olhos
    y_shift = TARGET_EYE_Y - current_eye_y
    
    # Cria img e desloca verticalmente
    # Se o deslocamento for pequeno, retorna a img redimensionada
    if abs(y_shift) < 0.5:
        return resized_face.astype(np.uint8)
    
    # Criar matriz de transformação para deslocamento vertical (dx=0)
    # Usamos uma matriz de translação simples no eixo Y
    # [1, 0, dx]  -> deslocamento em X
    # [0, 1, dy]  -> deslocamento em Y
    # -------------------------------------
    # REF: https://www.geeksforgeeks.org/maths/transformation-matrix/

    transform_matrix = np.array([
        [1, 0, 0],
        [0, 1, y_shift]
    ], dtype=np.float32)
    
    # Aplicar o deslocamento vertical
    # REF: https://www.geeksforgeeks.org/python/python-opencv-affine-transformation/
    normalized_face = cv2.warpAffine(resized_face, transform_matrix, 
                                      (TARGET_WIDTH, TARGET_HEIGHT),
                                      flags=cv2.INTER_LINEAR,
                                      # BORDER_REPLICATE evita bordas pretas
                                      borderMode=cv2.BORDER_REPLICATE)
    
    return normalized_face.astype(np.uint8)


def carregar_todos_oculos():
    """Carrega todas as imagens de óculos.
    
    Assim evita-se lag na câmera, o que acontece 
    se forem lidas em RealTime
    """
    oculos_cache = {}

    for pessoa_id, nome_arquivo in OCULOS_PESSOA.items():
        caminho = f'img\\{nome_arquivo}'
        oculos = cv2.imread(caminho, cv2.IMREAD_UNCHANGED)

        if oculos is None:
            print(f">>> AVISO: Não foi possível carregar {caminho}")
        else:
            oculos_cache[pessoa_id] = oculos
            print(f">>> Óculos carregado para {LABEL_PESSOA.get(pessoa_id, 'Desconhecido')}")
    return oculos_cache

def rodar_img(imagem, angulo):
    """Roda uma imagem e mantém as dimensões e canal alpha."""
    if angulo == 0:
        return imagem
    
    h, w = imagem.shape[:2]
    centro = (w // 2, h // 2)
    
    # Matriz de rotação
    matriz_rotacao = cv2.getRotationMatrix2D(centro, angulo, 1.0)
    # matriz_rotacao = [ [cos(ang),  -sin(ang),  tx],
    #                    [sin(ang),   cos(ang),  ty] ]
    
    # Calcular novo tamanho para não cortar a imagem
    # REF: https://www.geeksforgeeks.org/maths/rotation-matrix/
    cos = abs(matriz_rotacao[0, 0])
    sin = abs(matriz_rotacao[0, 1])

    # Cria-se um novo "canvas" para que a fota não seja cortada
    # cosseno e seno são guardados para levar em conta a rotação
    # -----------------------
    # Projeção horizontal
    novo_w = int((h * sin) + (w * cos))
    # Projeção vertical
    novo_h = int((h * cos) + (w * sin))
    
    # Ajustar matriz para centralizar (ex: width)
    # (novo_w / 2) -> é o centro do novo canvas
    # centro[0] -> centro da imagem original
    # Diferença é a deslocação a ser feita
    matriz_rotacao[0, 2] += (novo_w / 2) - centro[0]
    matriz_rotacao[1, 2] += (novo_h / 2) - centro[1]
    
    # Rotacionar imagem
    imagem_rotacionada = cv2.warpAffine(imagem, matriz_rotacao, (novo_w, novo_h), 
                                        flags=cv2.INTER_LINEAR, 
                                        borderMode=cv2.BORDER_CONSTANT, 
                                        borderValue=(0, 0, 0, 0))
    
    return imagem_rotacionada

def sobrepor_imagem_com_transparencia(fundo, overlay, pos_x, pos_y, largura, altura, angulo=0):
    """Sobrepõe uma img com transparência sobre o fundo.

    Args:
        fundo: Imagem de fundo (frame da webcam)
        overlay: Imagem PNG com canal alpha
        pos_x: Posição X onde colocar o overlay
        pos_y: Posição Y onde colocar o overlay
        largura: Largura desejada para o overlay
        altura: Altura desejada para o overlay
        angulo: Ângulo de rotação para o overlay (em graus)

    Returns:
        fundo: Imagem de fundo com o overlay sobreposto (modificada in-place).
    """
    # Resize dos óculos para o tamanho desejado
    overlay_resized = cv2.resize(overlay, (largura, altura))
    
    # Aplicar rotação se necessário
    if angulo != 0:
        overlay_resized = rodar_img(overlay_resized, angulo)
    
    # Separar os canais BGR e Alpha
    if overlay_resized.shape[2] == 4:
        bgr = overlay_resized[:, :, :3]
        alpha = overlay_resized[:, :, 3] / 255.0
        
        # Região de interesse no fundo
        h, w = bgr.shape[:2]
        
        # Ajustar posição para centralizar após rotação
        pos_x_ajustado = pos_x - (w - largura) // 2
        pos_y_ajustado = pos_y - (h - altura) // 2
        
        # Garantir que não saia do frame
        # --------------------------------
        # max(0, v) -> Garante que não pelas bordas esq e superior ao ser negativo
        # min(v, limite) -> Garante que não pelas bordas dir e inferior
        # fundo.shape[1] - w -> Última posição X onde a img ainda cabe inteira
        pos_x_ajustado = max(0, min(pos_x_ajustado, fundo.shape[1] - w))
        pos_y_ajustado = max(0, min(pos_y_ajustado, fundo.shape[0] - h))
        
        # Região de interesse no fundo, onde os oculos são postos
        roi = fundo[pos_y_ajustado:pos_y_ajustado+h, pos_x_ajustado:pos_x_ajustado+w]
        
        # Combinar as imagens usando o canal alpha
        # REF: https://en.wikipedia.org/wiki/Alpha_compositing#History
        for c in range(3):
            roi[:, :, c] = (1 - alpha) * roi[:, :, c] + alpha * bgr[:, :, c]
        
        fundo[pos_y_ajustado:pos_y_ajustado+h, pos_x_ajustado:pos_x_ajustado+w] = roi
    
    return fundo

def calcular_rotacao_olhos(landmarks, frame_shape):
    """Calcula o ângulo de rotação dos olhos baseado nos landmarks."""
    h, w = frame_shape[:2]
    
    # Landmarks dos olhos (iris)
    olho_esq_centro = landmarks[468]
    olho_dir_centro = landmarks[473]
    
    # Calcular posição média dos olhos
    x_olhos = (olho_esq_centro.x + olho_dir_centro.x) / 2
    y_olhos = (olho_esq_centro.y + olho_dir_centro.y) / 2
    
    # Calcular inclinação da cabeça
    dx = olho_dir_centro.x - olho_esq_centro.x
    dy = olho_dir_centro.y - olho_esq_centro.y
    angulo_cabeca = math.degrees(math.atan2(dy, dx))
    
    # Calcular movimento vertical dos olhos
    # 10 -> ponto + alto
    # 152 -> ponto + baixo
    # olhos - P+alto / altura_rosto
    y_olhos_normalizado = (y_olhos - landmarks[10].y) / (landmarks[152].y - landmarks[10].y)
    
    # Olhos com o MPEG devem estar a 0.4
    if y_olhos_normalizado < 0.35:  # Cabeça inclinada para cima
        fator_vertical = -0.2
    elif y_olhos_normalizado > 0.45: # // // para baixo
        fator_vertical = 0.2
    else:
        fator_vertical = 0

    # 15 graus para suavização
    angulo_oculos = -angulo_cabeca + (fator_vertical * 15) 
    
    return angulo_oculos

def calcular_posicao_oculos(landmarks, frame_shape):
    """Calcula a posição dos óculos baseado nos landmarks."""
    h, w = frame_shape[:2]
    
    # Landmarks idxs
    olho_esq_ext = landmarks[33]   # Canto externo do olho esquerdo
    olho_esq_int = landmarks[133]  # Canto interno do olho esquerdo
    olho_dir_int = landmarks[362]  # Canto interno do olho direito
    olho_dir_ext = landmarks[263]  # Canto externo do olho direito

    olho_esq_sup = landmarks[159]  # Pálpebra superior esquerda
    olho_dir_sup = landmarks[386]  # Pálpebra superior direita
    
    # Converter coordenadas normalizadas das lm para pixels
    x1 = int(olho_esq_ext.x * w)
    x2 = int(olho_dir_ext.x * w)
    
    # Calcular altura baseada na abertura dos olhos
    altura_olho_esq = abs((olho_esq_sup.y - olho_esq_ext.y) * h)
    altura_olho_dir = abs((olho_dir_sup.y - olho_dir_ext.y) * h)
    altura_media_olhos = (altura_olho_esq + altura_olho_dir) / 2
    
    # Posição Y baseada nos olhos
    y_olhos = int((olho_esq_ext.y + olho_esq_int.y + olho_dir_ext.y + olho_dir_int.y) / 4 * h)
    
    # Ajustar Y baseado na abertura dos olhos
    # Para qd piscamos os olhos, os óculos não subirem)
    if altura_media_olhos < 15:
        y_olhos = y_olhos - 5
    
    # Calcular largura dos óculos com ligeiro aumento
    largura_oculos = int((x2 - x1) * 1.5)
    # Calcular altura dos óculos
    altura_oculos = int(largura_oculos * 0.4)
    
    # Centraliza os óculos horizont. sobre os olhos.
    pos_x = x1 - int((largura_oculos - (x2 - x1)) / 2)
    # Centraliza verticalmente
    pos_y = y_olhos - int(altura_oculos * 0.5)
    
    # Garantir que não saia do frame
    # borda esq
    pos_x = max(0, min(pos_x, w - largura_oculos))
    # borda dirt
    pos_y = max(0, min(pos_y, h - altura_oculos))
    
    return pos_x, pos_y, largura_oculos, altura_oculos

def extrair_rosto_normalizado(frame, landmarks):
    """
    Extrai a região do rosto e aplica a normalização MPEG-7.
    
    Args:
        frame: Frame BGR da webcam
        landmarks: Landmarks do MediaPipe
    
    Returns:
        face_normalizada: Imagem normalizada em grayscale com tamanho 200x200
        (x_min, y_min, x_max, y_max): Coordenadas do bounding box original
    """
    h, w, _ = frame.shape
    
    # Extrair coordenadas da face
    x_coords = [lm.x * w for lm in landmarks]
    y_coords = [lm.y * h for lm in landmarks]
    
    x_min, x_max = int(min(x_coords)), int(max(x_coords))
    y_min, y_max = int(min(y_coords)), int(max(y_coords))
    
    # Adicionar padding
    padding = 10
    x_min = max(0, x_min - padding)
    y_min = max(0, y_min - padding)
    x_max = min(w, x_max + padding)
    y_max = min(h, y_max + padding)
    
    # Recortar a face
    face_bgr = frame[y_min:y_max, x_min:x_max]
    
    if face_bgr.size == 0:
        return None, None
    
    # Aplicar normalização MPEG-7
    face_normalizada = normalizar_face_mpeg7(face_bgr, landmarks, frame.shape)
    
    return face_normalizada, (x_min, y_min, x_max, y_max)

class FaceTracker:
    """Faz tracking e estabiliza o reconhecimento da face

    O tracker guarda as classificações durante 3s e depois fixa a identidade. 
    Desta forma, evita-se que mudanças rápidas ou falsos positivos afetem 
    o reconhecimento no começo.

    Attributes:
        tempo_estabilizacao: Número de segundos para guardar amostras.
        face_data: Dicionário com a relação de face_id e os dados de tracking.
        next_face_id: Próximo ID disponível para novas faces.
    """
    def __init__(self, tempo_estabilizacao=3):
        self.tempo_estabilizacao = tempo_estabilizacao
        self.face_data = {} 
        self.next_face_id = 0
    
    def get_face_id(self, bbox, landmarks):
        """Gera um ID único para a face baseado na posição"""

        # Usa o centro do bounding box como id
        x_center = (bbox[0] + bbox[2]) / 2
        y_center = (bbox[1] + bbox[3]) / 2
        
        # Procura face existente próxima
        for face_id, data in self.face_data.items():
            if 'last_position' in data:
                last_x, last_y = data['last_position']
                # Se a face se moveu menos de 100 pixels, 
                # é considerada a mesma face
                if abs(last_x - x_center) < 100 and abs(last_y - y_center) < 100:
                    return face_id
        
        # Face nova
        new_id = self.next_face_id
        self.next_face_id += 1
        return new_id
    
    def update_face(self, face_id, label_id, confianca, bbox, current_time):
        """Atualiza os dados de uma face"""
        if face_id not in self.face_data:
            self.face_data[face_id] = {
                'start_time': current_time,
                'predictions': [],
                'finalized': False,
                'final_label': None,
                'final_confidence': None,
                'last_position': ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
            }
        
        data = self.face_data[face_id]
        
        # Se já finalizou, retorna os valores
        if data['finalized']:
            return data['final_label'], data['final_confidence'], None
        
        elapsed = current_time - data['start_time']
        
        # Adiciona a classificação
        data['predictions'].append((label_id, confianca))
        
        # Atualiza posição
        data['last_position'] = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
        
        # Se passou o tempo de estabilização, calcula a média
        if elapsed >= self.tempo_estabilizacao and data['predictions']:
            from collections import Counter
            labels = [p[0] for p in data['predictions']]

            print(">>AQUI:", np.unique(labels))
            
            # Encontra label mais frequente
            label_counts = Counter(labels)
            most_common_label = label_counts.most_common(1)[0][0]
            
            # Calcula confiança média para essa label
            confs_filtered = [conf for label, conf in data['predictions'] if label == most_common_label]
            media_confianca = sum(confs_filtered) / len(confs_filtered) if confs_filtered else 100
            
            data['finalized'] = True
            data['final_label'] = most_common_label
            data['final_confidence'] = media_confianca
            
            # Determinaa se é desconhecido ou não
            if media_confianca < THRESHOLD_CONFIANCA:
                nome = LABEL_PESSOA.get(most_common_label, 'Desconhecido')
                print(f">>> Face {face_id} estabilizada: {nome} (conf: {media_confianca:.1f})")
            else:
                print(f">>> Face {face_id} estabilizada: DESCONHECIDO (conf: {media_confianca:.1f})")
                data['final_label'] = 8
                data['final_confidence'] = media_confianca
            
            return data['final_label'], data['final_confidence'], None
        
        # Ainda estabilizando
        return None, None, elapsed
    
    def remove_inactive_faces(self, active_face_ids, current_time):
        """Remove faces que não estão mais ativas"""
        to_remove = []
        for face_id, data in self.face_data.items():
            if face_id not in active_face_ids:
                to_remove.append(face_id)
        
        for face_id in to_remove:
            print(f">>> Face {face_id} removida (desapareceu)")
            del self.face_data[face_id]
    
    def get_face_status(self, face_id):
        """Retorna o status da face"""
        if face_id in self.face_data:
            data = self.face_data[face_id]
            if data['finalized']:
                return 'finalized', data['final_label'], data['final_confidence']
            else:
                elapsed = time.time() - data['start_time']
                return 'stabilizing', None, elapsed
        return 'new', None, None

# INICIALIZAÇÃO DO MODELO LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create()
try:
    recognizer.read(MODELO_LBPH_PATH)
    print(f">>> Modelo LBPH carregado com sucesso!")
    print(f">>> Usando normalização MPEG-7 (200x200 com alinhamento de olhos)")
except Exception as e:
    print(f">>> ERRO: Não foi possível carregar {MODELO_LBPH_PATH}. Treine o modelo primeiro.")
    print(f">>> Erro: {e}")
    exit()

# CARREGAR IMGS ÓCULOS
oculos_cache = carregar_todos_oculos()
if not oculos_cache:
    print(">>> AVISO: Nenhum óculo foi carregado. Continuando sem filtros.")

# CONFIG MEDIAPIPE
BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=DETECTOR_TASK_PATH),
    running_mode=VisionRunningMode.VIDEO,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=MAX_PESSOAS,  # Deteta até MAX_PESSOAS faces
    result_callback=None)

cap = cv2.VideoCapture(0)

# Dicionário para guardar ângulos anteriores por face (para suavização)
angulos_anteriores = {}

# Lista de cores para diferentes pessoas (RGB)
"""cores_pessoas = [
    (0, 255, 0),    # Verde
    (255, 0, 0),    # Azul
    (0, 255, 255),  # Amarelo
    (255, 0, 255),  # Magenta
    (255, 255, 0),  # Ciano
]
"""
# Inicializar o face tracker
face_tracker = FaceTracker(tempo_estabilizacao=TEMPO_ESTABILIZACAO)

with FaceLandmarker.create_from_options(options) as landmarker:
    print(f"\nWebcam iniciada. Detetando até {MAX_PESSOAS} pessoas simultaneamente.")
    print(f"Tempo de estabilização: {TEMPO_ESTABILIZACAO} segundos")
    print("Pressione 'q' para sair.")
    print("-" * 50)
    
    frame_count = 0
    total_frames = 0
    frames_com_face = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: 
            break
        
        total_frames += 1
        # Cria cópia para desenhar as deteções
        frame_copy = frame.copy()
        current_time = time.time()
        
        active_face_ids = set()

        # Prepara img para mediapipe
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        timestamp = int(time.time() * 5000)
        
        result = landmarker.detect_for_video(mp_image, timestamp)
        
        if result.face_landmarks:
            frames_com_face += 1
            num_faces_detectadas = len(result.face_landmarks)
            
            # mostra num de faces detectadas
            cv2.putText(frame_copy, f"Faces: {num_faces_detectadas}/{MAX_PESSOAS}", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # processar cada face detectada
            for idx, landmarks in enumerate(result.face_landmarks[:MAX_PESSOAS]):
                # Extrai e normaliza o rosto
                face_normalizada, bbox = extrair_rosto_normalizado(frame, landmarks)
                
                if face_normalizada is not None:
                    # Obter ID da face baseado na pos
                    face_id = face_tracker.get_face_id(bbox, landmarks)
                    active_face_ids.add(face_id)
                    
                    # Classificação
                    label_id, confianca = recognizer.predict(face_normalizada)
                    
                    if confianca >= THRESHOLD_CONFIANCA:
                        label_id = 8
                    
                    # Atualizar o tracker com esta classificação
                    finalized_label, finalized_confidence, elapsed = face_tracker.update_face(
                        face_id, label_id, confianca, bbox, current_time
                    )
                    
                    # Determina qual label usa durante a estabilização
                    status, temp_label, temp_info = face_tracker.get_face_status(face_id)
                    
                    if status == 'finalized':
                        # Face estabilizada
                        label_to_use = finalized_label
                        confidence_to_use = finalized_confidence
                        
                        # Garantir que desconhecido use label 8
                        if label_to_use == 8 or (confidence_to_use is not None and confidence_to_use >= THRESHOLD_CONFIANCA):
                            label_name = "Desconhecido"
                            color_box = (0, 165, 255)  # Laranja para desconhecido
                        else:
                            label_name = LABEL_PESSOA.get(label_to_use, "Desconhecido")
                            color_box = (0, 255, 0)  # Verde para conhecido
                        
                        status_text = f"FACE: {label_name} {confidence_to_use}"
                        
                    elif status == 'stabilizing':
                        # durante a estabilização - usa classificação atual temporariamente
                        label_to_use = label_id
                        confidence_to_use = confianca

                        if label_id == 8 or confianca >= THRESHOLD_CONFIANCA:
                            label_name = "Desconhecido"
                        else:
                            label_name = LABEL_PESSOA.get(label_id, "Desconhecido")
                        
                        color_box = (255, 255, 0)
                        status_text = f"A ESTABILIZAR ({elapsed:.1f}s/{TEMPO_ESTABILIZACAO}s)"
                        
                        # Mostrar barra de progresso
                        progress = min(1.0, elapsed / TEMPO_ESTABILIZACAO)
                        bar_width = 100
                        filled_width = int(bar_width * progress)
                        cv2.rectangle(frame_copy, (bbox[0], bbox[1] - 45), 
                                     (bbox[0] + bar_width, bbox[1] - 40), (100, 100, 100), -1)
                        cv2.rectangle(frame_copy, (bbox[0], bbox[1] - 45), 
                                     (bbox[0] + filled_width, bbox[1] - 40), (0, 255, 255), -1)
                    else:
                        # Face nova
                        label_name = "NOVA FACE"
                        color_box = (255, 255, 255)
                        status_text = "A RECONHECER..."
                    
                    # Para faces não finalizadas, mostrar classificação temporária
                    if status != 'finalized':
                        # Mostrar classificação atual temporária
                        if label_id == 8 or confianca >= THRESHOLD_CONFIANCA:
                            current_prediction = "Desconhecido"
                        else:
                            current_prediction = LABEL_PESSOA.get(label_id, "Desconhecido")
                        
                        confidence_label = f"Conf: {confianca:.1f}"
                        cv2.putText(frame_copy, confidence_label, (bbox[0], bbox[2] + 20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                    
                    # Desenhar retângulo com a cor correspondente
                    cv2.rectangle(frame_copy, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color_box, 2)
                    
                    # Status da face
                    cv2.putText(frame_copy, status_text, (bbox[0], bbox[1] - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_box, 1)
                    
                    # COLOCAR ÓCULOS
                    if status == 'finalized':
                        current_label = finalized_label
                        # Garantir que desconhecido usa label 8
                        if finalized_confidence is not None and finalized_confidence >= THRESHOLD_CONFIANCA:
                            current_label = 8
                    else:
                        # Durante estabilização, se a confiança for alta, usar óculos 8
                        if confianca >= THRESHOLD_CONFIANCA or label_id == 8:
                            current_label = 8
                        else:
                            current_label = label_id
                    
                    # Determinar óculos a usar
                    if current_label in oculos_cache:
                        oculos_img = oculos_cache[current_label]
                    else:
                        # Se não tem óculos específico, usa 8
                        oculos_img = oculos_cache.get(8, None)
                    
                    if oculos_img is not None:
                        # Calcular posição dos óculos baseado nos landmarks
                        pos_x, pos_y, largura, altura = calcular_posicao_oculos(landmarks, frame.shape)
                        
                        # Calcular ângulo de rotação dos óculos
                        angulo_atual = calcular_rotacao_olhos(landmarks, frame.shape)
                        
                        # Suavizar o ângulo para evitar tremores (manter ângulo por face)
                        if face_id not in angulos_anteriores:
                            angulos_anteriores[face_id] = 0
                        
                        suavizacao = 0.3
                        angulo_suavizado = (angulos_anteriores[face_id] * suavizacao) + (angulo_atual * (1 - suavizacao))
                        angulos_anteriores[face_id] = angulo_suavizado
                        
                        # Sobrepor os óculos no frame com rotação
                        frame_copy = sobrepor_imagem_com_transparencia(
                            frame_copy, oculos_img, pos_x, pos_y, largura, altura, angulo_suavizado
                        )
        
        # Remover faces inativas
        face_tracker.remove_inactive_faces(active_face_ids, current_time)
        
        cv2.imshow('Reconhecimento Multi-Face LBPH + MediaPipe (MPEG-7)', frame_copy)
        
        frame_count += 1
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    

    print(f">>> Fim da sessão:")

cap.release()
cv2.destroyAllWindows()