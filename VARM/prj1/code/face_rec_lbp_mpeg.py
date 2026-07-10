import cv2
import os
import numpy as np
import random
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions, RunningMode
import shutil

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
    
    # REF: a média ajuda ao movimento da iris não comprometer o filtro
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
    
    # 2- redimensionar img para 46x56
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


def detectar_face_mediapipe(img_path, landmarker, norm_mpeg7=True):
    """
    Deteta e extrai a face com o mediapipe
    
    Args:
        img_path: path da imagem
        landmarker: Instância do FaceLandmarker
        norm_mpeg7: True -> usa normalização MPEG-7 | False -> resize
    
    Returns:
        face_normalizada: Imagem da face normalizada ou None se não detectar
    """
    # Carregar imagem
    imagem_bgr = cv2.imread(img_path)
    if imagem_bgr is None:
        print(f"   >>> Não foi possível carregar: {img_path}")
        return None
    
    # Converter para rgb (mediapipe)
    imagem_rgb = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imagem_rgb)
    
    # Detetar faces
    detection_result = landmarker.detect(mp_image)
    
    if not detection_result.face_landmarks:
        print(f"   >>> Nenhuma face detectada em: {os.path.basename(img_path)}")
        return None
    
    # Guardar o primeiro rosto detetado
    landmarks = detection_result.face_landmarks[0]
    
    # Extrair coordenadas da face
    h, w, _ = imagem_bgr.shape
    # passa da normalização para pixeis
    x_coords = [lm.x * w for lm in landmarks]
    y_coords = [lm.y * h for lm in landmarks]
    
    # guarda coord min e max
    x_min, x_max = int(min(x_coords)), int(max(x_coords))
    y_min, y_max = int(min(y_coords)), int(max(y_coords))
    
    # adicionar padding
    padding = 10
    x_min = max(0, x_min - padding)
    y_min = max(0, y_min - padding)
    x_max = min(w, x_max + padding)
    y_max = min(h, y_max + padding)
    
    # recorta a face
    face_bgr = imagem_bgr[y_min:y_max, x_min:x_max]
    
    if face_bgr.size == 0:
        print(f"   >>> Região da face vazia em: {os.path.basename(img_path)}")
        return None
    
    # aplica normalização
    if norm_mpeg7:
        # normalização MPEG-7
        face_normalizada = normalizar_face_mpeg7(face_bgr, landmarks, imagem_bgr.shape)
    else:
        # resize
        face_gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
        face_normalizada = cv2.resize(face_gray, (200, 200))
        face_normalizada = face_normalizada.astype(np.uint8)
    
    return face_normalizada


def carregar_dados(pasta_raiz, fotos_por_pessoa=10, fotos_treino=7, tamanho_imagem=(46, 56), norm_mpeg7=True):
    """
    Carrega as imagens das pastas sX da att_faces e 
    prepara os dados para o treino e deteta as faces com o mediapipe
    
    Returns:
        faces_treino, labels_treino, faces_teste, labels_teste, nomes_teste, pessoas_info
    """
    
    # Inicializar mediapipe
    print("\n>>> Inicializar mediapipe...")
    model_path = 'code\\face_landmarker.task'
    
    try:
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=RunningMode.IMAGE,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            num_faces=1,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False
        )

        landmarker = FaceLandmarker.create_from_options(options)
        print(">>> mediapipe inicializado com sucesso!")
    except Exception as e:
        print(f">>> ERRO ao inicializar mediapipe: {e}")
        return [], [], [], [], [], {}
    
    faces_treino = []
    labels_treino = []
    faces_teste = []
    labels_teste = []
    nomes_teste = []
    pessoas_info = {}
    
    # Stats da detecção
    stats = {
        'total_imagens': 0,
        'faces_detectadas': 0,
        'falhas': 0,
        'imagens_sem_face': []
    }
    
    # Informa qual normalização está sendo usada
    if norm_mpeg7:
        print("\n>>> A usar: normalização MPEG-7")
    else:
        print(f"\n>>> A usar: normalização simples ({tamanho_imagem[0]}x{tamanho_imagem[1]})")
    
    # Percorre todas as pastas na pasta raiz
    for pasta in sorted(os.listdir(pasta_raiz)):
        caminho_pasta = os.path.join(pasta_raiz, pasta)
        
        # Verifica se é que começa com 's'
        if os.path.isdir(caminho_pasta) and pasta.startswith('s'):
            try:
                # Extrai o número da pasta
                label = int(pasta[1:])
                
                print(f"\n>>> A processar {pasta} (label: {label})...")
                
                # Lista todas as imagens na pasta
                imagens = [f for f in os.listdir(caminho_pasta) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.pgm', '.bmp'))]
                
                # Verifica se tem pelo menos x fotos por pessoa
                if len(imagens) < fotos_por_pessoa:
                    print(f"   >>> Apenas {len(imagens)} imagens disponíveis")
                    fotos_disponiveis = len(imagens)
                else:
                    fotos_disponiveis = fotos_por_pessoa
                
                # Baralha as imagens
                random.shuffle(imagens)
                
                # Separa imgs para treino e teste
                imagens_treino = imagens[:fotos_treino]
                imagens_teste = imagens[fotos_treino:fotos_disponiveis]
                
                faces_treino_pessoa = []
                nomes_treino_pessoa = []
                faces_teste_pessoa = []
                nomes_teste_pessoa = []
                
                # Processar imagens de treino
                for img_nome in imagens_treino:
                    caminho_img = os.path.join(caminho_pasta, img_nome)
                    stats['total_imagens'] += 1
                    
                    face = detectar_face_mediapipe(caminho_img, landmarker, norm_mpeg7)
                    
                    if face is not None:
                        # Se não usar MPEG-7, faz resize
                        if not norm_mpeg7:
                            face = cv2.resize(face, tamanho_imagem)
                            face = face.astype(np.uint8)
                        
                        faces_treino_pessoa.append(face)
                        nomes_treino_pessoa.append(caminho_img)
                        stats['faces_detectadas'] += 1
                    else:
                        stats['falhas'] += 1
                        stats['imagens_sem_face'].append(caminho_img)
                
                # Processa imgs de teste
                for img_nome in imagens_teste:
                    caminho_img = os.path.join(caminho_pasta, img_nome)
                    stats['total_imagens'] += 1
                    
                    face = detectar_face_mediapipe(caminho_img, landmarker, norm_mpeg7)
                    
                    if face is not None:
                        if not norm_mpeg7:
                            face = cv2.resize(face, tamanho_imagem)
                            face = face.astype(np.uint8)
                        
                        faces_teste_pessoa.append(face)
                        nomes_teste_pessoa.append(caminho_img)
                        stats['faces_detectadas'] += 1
                    else:
                        stats['falhas'] += 1
                        stats['imagens_sem_face'].append(caminho_img)
                
                # Adiciona aos conjuntos principais
                faces_treino.extend(faces_treino_pessoa)
                labels_treino.extend([label] * len(faces_treino_pessoa))
                faces_teste.extend(faces_teste_pessoa)
                labels_teste.extend([label] * len(faces_teste_pessoa))
                nomes_teste.extend(nomes_teste_pessoa)
                
                pessoas_info[label] = {
                    'pasta': pasta,
                    'total_imagens': len(imagens),
                    'treino': len(faces_treino_pessoa),
                    'teste': len(faces_teste_pessoa),
                    'falhas': len(imagens) - (len(faces_treino_pessoa) + len(faces_teste_pessoa))
                }
                
                print(f"   [pass] {len(faces_treino_pessoa)} treino, {len(faces_teste_pessoa)} teste, "
                      f"{pessoas_info[label]['falhas']} falhas")
                
            except ValueError:
                print(f"   >>> Pasta {pasta} ignorada (formato inválido)")
            except Exception as e:
                print(f"   >>> Erro ao processar {pasta}: {e}")
    
    landmarker.close()
    
    # Mostrar estatísticas gerais
    print("\n" + "=" * 60)
    print("ESTATÍSTICAS DE DETECÇÃO:")
    print(f"Total de imagens processadas: {stats['total_imagens']}")
    print(f"Faces detectadas com sucesso: {stats['faces_detectadas']}")
    print(f"Falhas na detecção: {stats['falhas']}")

    if stats['total_imagens'] > 0:
        print(f"Taxa de sucesso: {(stats['faces_detectadas']/stats['total_imagens']*100):.1f}%")
    
    if stats['imagens_sem_face']:
        print("\n>>> Imagens sem face detectada:")
        # Mostra 10 imgs
        for img in stats['imagens_sem_face'][:10]:  
            print(f"   - {img}")
        if len(stats['imagens_sem_face']) > 10:
            print(f"   ... e mais {len(stats['imagens_sem_face']) - 10}")
    
    print("=" * 60)
    
    return faces_treino, labels_treino, faces_teste, labels_teste, nomes_teste, pessoas_info


def treinar_modelo(faces_treino, labels_treino):
    """Treina o modelo LBPH com os dados de treino

    Args:
        faces_treino: lista das faces para treino
        labels_treino: lista das labels para treino

    Returns:
        recognizer: recognizer treinado
    """
    print("\n>>> Treino modelo LBPH...")
    
    if len(faces_treino) == 0:
        print(">>> ERRO: Nenhuma imagem para treino!")
        return None
    
    try:
        # Cria um array para as cara e as labels
        faces_array = np.array(faces_treino, dtype=np.uint8)
        labels_array = np.array(labels_treino, dtype=np.int32)
        
        print(f".:: Formato dos dados: {faces_array.shape}")
        print(f".:: Pessoas diferentes: {len(set(labels_treino))}")
        
        # Cria e treina o recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces_array, labels_array)
        
        print(f"[pass] Modelo treinado com {len(faces_treino)} imagens")
        
        return recognizer
        
    except Exception as e:
        print(f"[error] Erro ao treinar modelo: {e}")
        return None


def testar_modelo(recognizer, faces_teste, labels_teste, nomes_arquivos_teste=None):
    """
    Testa o modelo com os dados de teste
    
    Args:
        recognizer: Modelo LBPH treinado
        faces_teste: Lista de imagens de teste
        labels_teste: Lista de labels do teste
        nomes_arquivos_teste: Lista com os paths das imagens de teste
    
    Returns:
        prob_acertos: probabilidade de acerto
        imagens_fracas: Dicionários com info das imagens com confiança FRACA
    """
    if recognizer is None:
        print(">>> Modelo não foi treinado corretamente!")
        return 0, []
    
    print("\n>>> Testar modelo...")
    print("-" * 70)
    
    acertos = 0
    total = len(faces_teste)
    confianca_media = 0
    imagens_fracas = []
    
    if total == 0:
        print(" >>> Nenhuma imagem de teste disponível!")
        return 0, []
    
    for i, (face, label_real) in enumerate(zip(faces_teste, labels_teste)):
        # Garantir que a imagem está em grayscale
        if len(face.shape) == 3:  # Se tiver 3 canais (RGB)
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            print(f">>> Imagem {i+1} convertida para grayscale")
        
        # Garantir que é uint8
        face = face.astype(np.uint8)
        
        # Verificar se tem (altura, largura)
        if len(face.shape) != 2:
            print(f"  >>> Imagem {i+1} com formato inválido: {face.shape}")
            continue
        
        # Teste
        try:
            # REF: https://github.com/opencv/opencv_contrib/blob/master/modules/face/src/lbph_faces.cpp
            label_predito, confianca = recognizer.predict(face)
            confianca_media += confianca
            
            # Verifica se acertou
            if label_predito == label_real:
                acertos += 1
                status = "V"
            else:
                status = "F"
            
            # Interpreta a confiança
            if confianca < 50:
                nivel = "EXCELENTE"
            elif confianca < 80:
                nivel = "BOA"
            elif confianca < 100:
                nivel = "NORMAL"
            else:
                nivel = "FRACA"
            
            # Se for FRACA, guarda informação
            if nivel == "FRACA":
                nome_arquivo = nomes_arquivos_teste[i] if nomes_arquivos_teste else f"Imagem {i+1} (sem nome)"
                imagens_fracas.append({
                    'indice': i+1,
                    'caminho': nome_arquivo,
                    'label_real': label_real,
                    'label_predito': label_predito,
                    'confianca': confianca,
                    'acertou': (label_predito == label_real)
                })
            
            print(f"  {status} Teste {i+1:2d}: Real={label_real:2d} | Resultado={label_predito:2d} | "
                  f"Confiança={confianca:6.2f} ({nivel})" + 
                  (f" - {nomes_arquivos_teste[i]}" if nomes_arquivos_teste and nivel == "FRACA" else ""))
            
        except Exception as e:
            print(f"  >>> Erro na classificação da imagem {i+1}: {e}")
    
    # Calcula estatísticas
    if total > 0:
        prob_acertos = (acertos / total) * 100
        confianca_media = confianca_media / total
        
        print("-" * 70)
        print(f"\n>>> RESULTADOS FINAIS:")
        print(f"   - Total de testes: {total}")
        print(f"   - Acertos: {acertos}")
        print(f"   - Erros: {total - acertos}")
        print(f"   - Probabilidade de acerto/Exatidão (acc): {prob_acertos:.2f}%")
        print(f"   - Confiança média: {confianca_media:.2f}")
        
        # Mostra imagens com classificação FRACA
        if imagens_fracas:
            print(f"\n>>> IMAGENS COM CLASSIFICAÇÃO FRACA (confiança >= 100):")
            print("-" * 70)
            for img in imagens_fracas:
                print(f"  >>> {img['caminho']}")
                print(f"     → Real: {img['label_real']}, Predito: {img['label_predito']}")
                print(f"     → Confiança: {img['confianca']:.2f}")
                print(f"     → Acertou: {'[pass]' if img['acertou'] else '✗'}")
                print()
            
            # Estatísticas das imagens fracas
            total_fracas = len(imagens_fracas)
            acertos_fracas = sum(1 for img in imagens_fracas if img['acertou'])
            print(f"   Total de imagens FRACAS: {total_fracas}")
            print(f"   Acertos entre FRACAS: {acertos_fracas}/{total_fracas} ({acertos_fracas/total_fracas*100:.1f}%)")
            
            # Opção de guardar relatório
            save_relatorio = input("\n>>> Deseja guardar relatório das imagens FRACAS? (s/n): ").lower()
            if save_relatorio == 's':
                with open('imagens_fracas_relatorio.txt', 'w', encoding='utf-8') as f:
                    f.write("RELATÓRIO DE IMAGENS COM CLASSIFICAÇÃO FRACA\n")
                    f.write("=" * 50 + "\n\n")
                    for img in imagens_fracas:
                        f.write(f"Arquivo: {img['caminho']}\n")
                        f.write(f"  Real: {img['label_real']}, Predito: {img['label_predito']}\n")
                        f.write(f"  Confiança: {img['confianca']:.2f}\n")
                        f.write(f"  Acertou: {'Sim' if img['acertou'] else 'Não'}\n")
                        f.write("-" * 30 + "\n")
                print(f"[pass] Relatório guardado como 'imagens_fracas_relatorio.txt'")
    else:
        prob_acertos = 0
    
    return prob_acertos, imagens_fracas


def save_faces_normalizadas(faces_treino, labels_treino, pasta_destino="faces_normalizadas", prefixo="treino"):
    """
    Guarda as faces normalizadas em disco, caso seja necessário analisar
    
    Args:
        faces_treino: Lista de imagens normalizadas
        labels_treino: Lista de labels correspondentes
        pasta_destino: Pasta onde guardar as imagens
        prefixo: Prefixo para nomear os arquivos ('treino' ou 'teste')
    """
    import os
    
    # Criar pasta de destino se não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f">>> Pasta criada: {pasta_destino}")
    
    # Dicionário para contar imagens por pessoa
    contador_por_label = {}
    
    for i, (face, label) in enumerate(zip(faces_treino, labels_treino)):
        # Criar pasta para cada pessoa se não existir
        pasta_pessoa = os.path.join(pasta_destino, f"pessoa_{label}")
        if not os.path.exists(pasta_pessoa):
            os.makedirs(pasta_pessoa)
        
        # Conta quantas imagens já guardamos para esta pessoa
        if label not in contador_por_label:
            contador_por_label[label] = 0
        contador_por_label[label] += 1
        
        nome_arquivo = f"{prefixo}_pessoa{label}_{contador_por_label[label]:03d}.png"
        caminho_completo = os.path.join(pasta_pessoa, nome_arquivo)
        
        # Guarda img
        cv2.imwrite(caminho_completo, face)
    
    print(f"\n[pass] {len(faces_treino)} imagens guardas em '{pasta_destino}'")
    
    # Mostrar resumo por pessoa
    print("\n>>> Resumo por pessoa:")
    for label in sorted(contador_por_label.keys()):
        print(f"   - Pessoa {label}: {contador_por_label[label]} imagens")


def save_imagens_fracas(imagens_fracas, pasta_destino="imagens_fracas"):
    """
    Guarda as imagens classificadas como FRACAS para análise
    
    Args:
        imagens_fracas: Lista de dicionários com informações das imagens fracas
        pasta_destino: Pasta onde guardar as imagens
    """
    
    if not imagens_fracas:
        print(">>> Nenhuma imagem FRACA para guardar")
        return
    
    # Criar pasta de destino
    if os.path.exists(pasta_destino):
        resposta = input(f"Pasta '{pasta_destino}' já existe. Substituir? (s/n): ").lower()
        if resposta != 's':
            print(">>> Operação cancelada")
            return
        shutil.rmtree(pasta_destino)
    
    os.makedirs(pasta_destino)
    
    # Criar subpastas
    pasta_acertos = os.path.join(pasta_destino, "acertou_mas_confianca_fraca")
    pasta_erros = os.path.join(pasta_destino, "errou_confianca_fraca")
    os.makedirs(pasta_acertos)
    os.makedirs(pasta_erros)
    
    # Copiar as imagens
    for img_info in imagens_fracas:
        caminho_original = img_info['caminho']
        if os.path.exists(caminho_original):
            if img_info['acertou']:
                destino = pasta_acertos
            else:
                destino = pasta_erros
            
            nome_base = os.path.basename(caminho_original)
            nome_novo = f"real{img_info['label_real']}_pred{img_info['label_predito']}_conf{img_info['confianca']:.0f}_{nome_base}"
            shutil.copy2(caminho_original, os.path.join(destino, nome_novo))
    
    print(f"\n[pass] {len(imagens_fracas)} imagens FRACAS copiadas para '{pasta_destino}'")
    print(f"   - Acertou: {len([i for i in imagens_fracas if i['acertou']])} imagens em '{pasta_acertos}'")
    print(f"   - Errou: {len([i for i in imagens_fracas if not i['acertou']])} imagens em '{pasta_erros}'")


def main():
    # Configurações
    PASTA_RAIZ = "att_faces"
    FOTOS_POR_PESSOA = 11
    FOTOS_TREINO = 11  # 11 para treino, 0 para teste (todas para treino)
    TAMANHO_IMAGEM = (46, 56)
    
    # Opt para usar MPEG-7
    norm_mpeg7 = True  

    # Opt para guardar faces norm
    SAVE_FACES_NORMALIZADAS = True  
    
    print("=" * 60)
    print(">>> TREINO LBPH COM DETECÇÃO MEDIAPIPE")
    if norm_mpeg7:
        print(">>> NORMALIZAÇÃO: MPEG-7")
    else:
        print(f">>> NORMALIZAÇÃO: SIMPLES ({TAMANHO_IMAGEM[0]}x{TAMANHO_IMAGEM[1]})")
    print("=" * 60)
    
    # Verifica se a pasta existe
    if not os.path.exists(PASTA_RAIZ):
        print(f"\n[error] ERRO: Pasta '{PASTA_RAIZ}' não encontrada!")
        return
    
    # 1. Carregar dados com detecção de faces
    print(f"\n>>> A processar imagens de: {PASTA_RAIZ}")
    faces_treino, labels_treino, faces_teste, labels_teste, nomes_teste, pessoas_info = carregar_dados(
        PASTA_RAIZ, FOTOS_POR_PESSOA, FOTOS_TREINO, TAMANHO_IMAGEM, norm_mpeg7
    )

    #for i, (face, label) in enumerate(zip(faces_treino, labels_treino)):
    #    cv2.imshow(f"Treino {i} - Label {label}", face)
    #    cv2.waitKey(0)  # espera tecla para passar à próxima
    #    cv2.destroyAllWindows()
        
    # 2. Verificar se há dados suficientes
    if len(faces_treino) == 0:
        print("\n[error] ERRO: Nenhuma face detectada para treino!")
        return
    
    print(f"\n.:: Total para treino: {len(faces_treino)} imagens")
    print(f".:: Total para teste: {len(faces_teste)} imagens")
    
    # Mostra formato das imgs após normalização
    if len(faces_treino) > 0:
        print(f".:: Formato das imagens: {faces_treino[0].shape}")
    
    # 3. guardar faces norm
    if SAVE_FACES_NORMALIZADAS:
        print("\n>>> A guardar faces normalizadas...")
        
        # Gudar faces de treino
        pasta_treino = "faces_normalizadas_treino"
        if norm_mpeg7:
            pasta_treino += "_mpeg7"
        else:
            pasta_treino += "_simples"
        
        save_faces_normalizadas(faces_treino, labels_treino, pasta_treino, "treino")
        
        # Guarda faces de teste se houver
        if len(faces_teste) > 0:
            pasta_teste = "faces_normalizadas_teste"
            if norm_mpeg7:
                pasta_teste += "_mpeg7"
            else:
                pasta_teste += "_simples"
            
            save_faces_normalizadas(faces_teste, labels_teste, pasta_teste, "teste")
    
    # 4. Treinar modelo
    recognizer = treinar_modelo(faces_treino, labels_treino)
    
    if recognizer is not None:
        # 5. Testar modelo
        if len(faces_teste) > 0:
            prob_acertos, imagens_fracas = testar_modelo(recognizer, faces_teste, labels_teste, nomes_teste)
            
            # 6. Guarar imagens FRACAS se houver
            if imagens_fracas:
                save_imagens_fracas(imagens_fracas)
        
        # 7. Guardar modelo
        guardar = input("\n[save] Deseja guardar o modelo treinado? (s/n): ").lower()
        if guardar == 's':
            nome_arquivo = "modelo_lbph_mpeg7.yml" if norm_mpeg7 else "modelo_lbph_norm.yml"
            # REF: https://docs.opencv.org/4.x/dd/d65/classcv_1_1face_1_1FaceRecognizer.html
            recognizer.write(nome_arquivo)
            print(f"[pass] Modelo salvo como '{nome_arquivo}'")
    
    print("\n[done] Processo concluído!")


if __name__ == "__main__":
    main()