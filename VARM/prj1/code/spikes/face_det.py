import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision import drawing_styles
import cv2
import numpy as np
import time

# Config
USE_IMG = False 
CAMINHO_IMAGEM = "att_faces\\s1\\4.pgm"
model_path = 'code\\face_landmarker.task'

# ========================

# Componentes mediapipe
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


def draw_landmarks_on_image(rgb_image, detection_result):
    """Desenha as landmarks na imagem com o Mediapipe

    Args:
        rgb_image: Imagem RGB
        Objeto FaceLandmarkerResult que tem as landmarks da cara detetada

    Returns:
        Copia da imagem com as landmarks desenhadas
    """
    # landmarks
    face_landmarks_list = detection_result.face_landmarks
    # copia da img original
    annotated_image = np.copy(rgb_image)

    # Percorre-se todas as landmarks e desenha-se essa marca na imagem
    for idx in range(len(face_landmarks_list)):
        face_landmarks = face_landmarks_list[idx]

        # TESSELATION (mesh completa)
        drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks,
            connections=vision.FaceLandmarksConnections.FACE_LANDMARKS_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=drawing_styles.get_default_face_mesh_tesselation_style())
        
        # Contornos do rosto
        drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks,
            connections=vision.FaceLandmarksConnections.FACE_LANDMARKS_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=drawing_styles.get_default_face_mesh_contours_style())
        
        # Iris esquerda
        drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks,
            connections=vision.FaceLandmarksConnections.FACE_LANDMARKS_LEFT_IRIS,
            landmark_drawing_spec=None,
            connection_drawing_spec=drawing_styles.get_default_face_mesh_iris_connections_style())
        
        # Iris direita
        drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks,
            connections=vision.FaceLandmarksConnections.FACE_LANDMARKS_RIGHT_IRIS,
            landmark_drawing_spec=None,
            connection_drawing_spec=drawing_styles.get_default_face_mesh_iris_connections_style())

    return annotated_image

# Criar uma instância do face landmarker
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO if not USE_IMG else VisionRunningMode.IMAGE,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    # Número de faces a detetar
    num_faces=4,
    result_callback=None)

if USE_IMG:
    print(f"Modo imagem. Imagem: {CAMINHO_IMAGEM}")
    
    # Carregar imagem
    frame = cv2.imread(CAMINHO_IMAGEM)
    if frame is None:
        print(f"Erro: Não foi possível carregar a imagem {CAMINHO_IMAGEM}")
        exit()
    
    # Converter para RGB
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    
    # Processar com o landmarker
    with FaceLandmarker.create_from_options(options) as landmarker:
        detection_result = landmarker.detect(mp_image)
        
        if detection_result.face_landmarks:
            print(f"Detectados {len(detection_result.face_landmarks)} rosto(s)")
            annotated_image = draw_landmarks_on_image(rgb_image, detection_result)
            result_frame = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
        else:
            print("Nenhum rosto detectado")
            result_frame = frame
            cv2.putText(result_frame, "Nenhum rosto detectado", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Mostrar resultado
        cv2.imshow('MediaPipe Face Landmarker - Imagem Estática', result_frame)
        print("Pressione qualquer tecla para sair...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

else:
    print("A iniciar webcam... Pressione 'q' para sair")
    cap = cv2.VideoCapture(0)

    # Verificar se a webcam abriu bem
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a webcam")
        exit()

    # Config resolução da webcam
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Criar o landmarker
    with FaceLandmarker.create_from_options(options) as landmarker:
        # Variável para controle de FPS
        fps_start_time = time.time()
        fps_frame_count = 0
        fps = 0
        
        while True:
            # Ler frame da webcam
            ret, frame = cap.read()
            if not ret:
                print("Erro: Não foi possível capturar frame")
                break
            
            # Converter bgr (opencv) para rgb (mediapipe)
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Obter timestamp atual em milissegundos
            timestamp_ms = int(time.time() * 1000)
            
            # Criar Image do mediapipe
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            
            # Detectar landmarks no modo VIDEO
            detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)
            
            # Verificar se detectou algum rosto
            if detection_result.face_landmarks:
                # Desenha landmarks na imagem
                annotated_image = draw_landmarks_on_image(rgb_image, detection_result)
                
                # Converte bgr outra vez para o opencv
                annotated_frame = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
            else:
                # Se não detectou rosto, usa o frame normal
                annotated_frame = frame
                cv2.putText(annotated_frame, "Nenhum rosto detectado", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            if detection_result.face_landmarks:
                cv2.putText(annotated_frame, f"Rosto detectado!", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('MediaPipe Face Landmarker - Webcam', annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("A fechar...")
                break

    cap.release()
    cv2.destroyAllWindows()

print("Programa encerrado.")