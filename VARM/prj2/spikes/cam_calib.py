import numpy as np
import cv2
import os
import glob

class CameraCalibrator:
    def __init__(self, chessboard_size=(9, 6), square_size=25.0):
        """
        Construtor
        
        Args:
            chessboard_size: tuple (número de cantos internos horizontal, vertical)
            square_size: Tamanho do quadrado do chessboard em mm (opcional)
        """
        self.chessboard_size = chessboard_size
        self.square_size = square_size
        
        # Critérios para encontrar cantos do chessboard
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
    def prepare_object_points(self):
        """Prepara os pontos 3D do mundo real para o chessboard"""

        # cria-se um array com o tamanho do tabuleiro
        object_points_3d = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)

        # coordenadas (X,Y, Z=0)
        object_points_3d[:, :2] = np.mgrid[0:self.chessboard_size[0], 
                                            0:self.chessboard_size[1]].T.reshape(-1, 2)
        
        # mult pelo lado do quadrado do padrão
        object_points_3d *= self.square_size
        
        return object_points_3d
    
    def find_chessboard_corners(self, image):
        """Encontra os cantos do chessboard na imagem"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)
        
        if ret:
            corners_subpix = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
            return True, corners_subpix, gray
        else:
            return False, None, gray
    
    def calibrate_from_images(self, image_paths):
        """
        Calibra a câmera com uma lista de imagens
        
        Args:
            image_paths: Lista de paths para imagens do chessboard
            
        Returns:
            ret: Parâmetro de reprojeção
            camera_matrix: Matriz da câmera
            dist_coeffs: Coeficientes de distorção
            rvecs: Vetores de rotação
            tvecs: Vetores de translação
            image_points: Pontos 2D encontrados
        """
        object_points_3d = self.prepare_object_points()
        
        object_points = []  # Pontos 3D do mundo real
        image_points = []   # Pontos 2D na imagem
        
        valid_images = 0
        
        for image_path in image_paths:
            print(f"Processando: {os.path.basename(image_path)}")
            image = cv2.imread(image_path)
            
            if image is None:
                print(f"Erro ao carregar imagem: {image_path}")
                continue
            
            ret, corners, gray = self.find_chessboard_corners(image)
            
            if ret:
                object_points.append(object_points_3d)
                image_points.append(corners)
                valid_images += 1
                
                # Visualizar os cantos encontrados
                self.visualize_corners(image, corners, f"Chessboard encontrado - {valid_images}")
            else:
                print(f"Não foi possível encontrar chessboard em {os.path.basename(image_path)}")
        
        print(f"Imagens válidas para calibração: {valid_images}/{len(image_paths)}")
        
        if valid_images < 10:
            print("Aviso: Recomenda-se pelo menos 10 imagens para uma boa calibração")
        
        if valid_images < 3:
            raise ValueError("Precisa de pelo menos 3 imagens válidas para calibrar")
        
        # Calibrar a câmera
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            object_points, image_points, gray.shape[::-1], None, None
        )
        
        # Calcular erro de reprojeção
        total_error = 0
        for i in range(len(object_points)):
            img_points_proj, _ = cv2.projectPoints(
                object_points[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs
            )
            error = cv2.norm(image_points[i], img_points_proj, cv2.NORM_L2) / len(img_points_proj)
            total_error += error
        
        reprojection_error = total_error / len(object_points)
        
        return ret, camera_matrix, dist_coeffs, rvecs, tvecs, reprojection_error, image_points
    
    def visualize_corners(self, image, corners, title="Chessboard Corners"):
        """Visualiza os cantos encontrados do chessboard"""
        img_copy = image.copy()
        cv2.drawChessboardCorners(img_copy, self.chessboard_size, corners, True)
        
        # Redimensionar se a imagem for muito grande
        height, width = img_copy.shape[:2]
        if width > 1200:
            scale = 1200 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            img_copy = cv2.resize(img_copy, (new_width, new_height))
        
        cv2.imshow(title, img_copy)
        cv2.waitKey(300)  # Mostrar por 300ms
        cv2.destroyWindow(title)
    
    def save_calibration(self, camera_matrix, dist_coeffs, filename="camera_calibration.xml"):
        """
        Guarda os parâmetros da calibração em formato XML usando FileStorage do OpenCV
        
        Args:
            camera_matrix: Matriz da câmera
            dist_coeffs: Coeficientes de distorção
            filename: Nome do arquivo XML para guardar
        """
        # Usar FileStorage do OpenCV para guardar em XML
        fs = cv2.FileStorage(filename, cv2.FILE_STORAGE_WRITE)
        
        # guardar a matriz da câmera
        fs.write("camera_matrix", camera_matrix)
        
        # guardar os coeficientes de distorção
        fs.write("distortion_coefficients", dist_coeffs)
        
        # guardar informações adicionais
        fs.write("chessboard_size_x", self.chessboard_size[0])
        fs.write("chessboard_size_y", self.chessboard_size[1])
        fs.write("square_size_mm", self.square_size)
        
        fs.release()
        print(f"Parâmetros salvos em {filename} (formato XML)")
    
    def load_calibration(self, filename="camera_calibration.xml"):
        """
        Carrega os parâmetros da calibração de um arquivo XML
        
        Args:
            filename: Nome do arquivo XML para carregar
            
        Returns:
            camera_matrix: Matriz da câmera
            dist_coeffs: Coeficientes de distorção
        """
        # Verificar se o arquivo existe
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Arquivo {filename} não encontrado!")
        
        # Usar FileStorage do OpenCV para carregar do XML
        fs = cv2.FileStorage(filename, cv2.FILE_STORAGE_READ)
        
        if not fs.isOpened():
            raise IOError(f"Não foi possível abrir o arquivo {filename}")
        
        # Carregar a matriz da câmera
        camera_matrix = fs.getNode("camera_matrix").mat()
        
        # Carregar os coeficientes de distorção
        dist_coeffs = fs.getNode("distortion_coefficients").mat()
        
        # Opcional: carregar informações adicionais
        chessboard_size_x = int(fs.getNode("chessboard_size_x").real())
        chessboard_size_y = int(fs.getNode("chessboard_size_y").real())
        square_size = fs.getNode("square_size_mm").real()
        
        fs.release()
        
        print(f"Parâmetros carregados de {filename}")
        print(f"Configuração do chessboard: {chessboard_size_x}x{chessboard_size_y}, quadrado={square_size}mm")
        
        return camera_matrix, dist_coeffs
    
    def undistort_image(self, image, camera_matrix, dist_coeffs):
        """Remove distorção de uma imagem com os parâmetros calibrados"""
        h, w = image.shape[:2]
        
        # Otimizar a matriz da câmera para a imagem
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
            camera_matrix, dist_coeffs, (w, h), 1, (w, h)
        )
        
        # Remover distorção
        undistorted = cv2.undistort(image, camera_matrix, dist_coeffs, None, new_camera_matrix)
        
        return undistorted, new_camera_matrix
    
    def save_images_with_corners(self, image_paths, output_dir="images_with_corners"):
        """guarda imagens com os cantos do chessboard desenhados"""
        os.makedirs(output_dir, exist_ok=True)
        
        for image_path in image_paths:
            image = cv2.imread(image_path)
            if image is None:
                continue
            
            ret, corners, _ = self.find_chessboard_corners(image)
            if ret:
                img_copy = image.copy()
                cv2.drawChessboardCorners(img_copy, self.chessboard_size, corners, True)
                
                # guardar imagem
                output_path = os.path.join(output_dir, os.path.basename(image_path))
                cv2.imwrite(output_path, img_copy)
                print(f"Salvo: {output_path}")
        
        print(f"Imagens com cantos salvos em {output_dir}")

def capture_calibration_images(num_images=20, chessboard_size=(9, 6), save_dir="calibration_images"):
    """
    Captura imagens ao vivo da webcam para calibração
    
    Args:
        num_images: Número de imagens a serem capturadas
        chessboard_size: Tamanho do chessboard
        save_dir: Diretório para guardar as imagens
    """
    import time
    
    # Criar diretório para guardar imagens
    os.makedirs(save_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    
    # Ajustar resolução para melhor performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    calibrator = CameraCalibrator(chessboard_size=chessboard_size)
    
    images_captured = 0
    print("\nInstruções:")
    print("- Mova o chessboard em diferentes posições e orientações")
    print("- Pressione 'espaço' para capturar imagem quando o chessboard for detectado")
    print("- Pressione 'q' para sair")
    print("- Pressione 'd' para debug (mostrar imagem processada)\n")
    
    while images_captured < num_images:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar frame")
            break
        
        display_frame = frame.copy()
        
        # Tentar encontrar chessboard em tempo real
        ret_corners, corners, gray = calibrator.find_chessboard_corners(frame)
        
        if ret_corners:
            cv2.drawChessboardCorners(display_frame, chessboard_size, corners, True)
            status_text = "[pass] Chessboard detectado - Pressione ESPACO"
            color = (0, 255, 0)
        else:
            status_text = "✗ Chessboard NAO detectado"
            color = (0, 0, 255)
        
        # Mostrar informações na tela
        cv2.putText(display_frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(display_frame, f"Imagens capturadas: {images_captured}/{num_images}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(display_frame, "Q - Sair | D - Debug", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        cv2.imshow('Captura para Calibracao', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' ') and ret_corners:  # Espaço para capturar
            image_path = os.path.join(save_dir, f"calibration_{images_captured+1:03d}.jpg")
            cv2.imwrite(image_path, frame)
            print(f"[pass] Imagem {images_captured+1} guarda: {image_path}")
            images_captured += 1
            time.sleep(0.3)  # Pequena pausa após capturar
        elif key == ord('d'):  # Modo debug
            debug_frame = frame.copy()
            if ret_corners:
                cv2.drawChessboardCorners(debug_frame, chessboard_size, corners, True)
            
            # Mostrar imagem em escala de cinza também
            gray_debug = cv2.cvtColor(debug_frame, cv2.COLOR_BGR2GRAY)
            gray_debug = cv2.cvtColor(gray_debug, cv2.COLOR_GRAY2BGR)
            debug_combined = np.hstack((debug_frame, gray_debug))
            
            # Redimensionar se necessário
            height, width = debug_combined.shape[:2]
            if width > 1600:
                scale = 1600 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                debug_combined = cv2.resize(debug_combined, (new_width, new_height))
            
            cv2.imshow("Debug - Original vs Gray", debug_combined)
            cv2.waitKey(1)
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[pass] Capturadas {images_captured} imagens em '{save_dir}'")
    return save_dir

def test_calibration(camera_matrix, dist_coeffs, image_path):
    """Testa a calibração em uma imagem"""
    calibrator = CameraCalibrator()
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Erro: Não foi possível carregar {image_path}")
        return
    
    undistorted, new_camera_matrix = calibrator.undistort_image(image, camera_matrix, dist_coeffs)
    
    # Mostrar resultados
    cv2.imshow("Original", image)
    cv2.imshow("Corrigida (sem distorcao)", undistorted)
    
    print("\nTeste visual: Compare as duas imagens")
    print("Pressione qualquer tecla para fechar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    """Função principal para executar a calibração completa"""
    
    # Configurações
    print("=== CALIBRAÇÃO DE CÂMERA COM CHESSBOARD ===")
    print("\nConfiguração padrão: chessboard 9x6 cantos internos")
    print("Se seu chessboard for diferente, ajuste no código\n")
    
    chessboard_size = (9, 6)  # Ajustar conforme seu chessboard
    square_size = 25.0  # Tamanho do quadrado em mm (ajustar conforme necessário)
    
    print("1. Capturar novas imagens para calibração")
    print("2. Usar imagens existentes")
    print("3. Apenas testar calibração existente")
    print("4. Sair")
    
    choice = input("\nEscolha uma opção: ")
    
    if choice == '1':
        try:
            num_images = int(input("Número de imagens a capturar (recomendado 15-20): "))
            image_dir = capture_calibration_images(num_images, chessboard_size)
            image_paths = glob.glob(os.path.join(image_dir, "*.jpg"))
            
            if not image_paths:
                print("Erro: Nenhuma imagem encontrada!")
                return
                
        except Exception as e:
            print(f"Erro na captura: {e}")
            return
            
    elif choice == '2':
        image_dir = input("Diretório com as imagens: ")
        if not os.path.exists(image_dir):
            print(f"Diretório {image_dir} não existe!")
            return
        image_paths = glob.glob(os.path.join(image_dir, "*.jpg"))
        if not image_paths:
            image_paths = glob.glob(os.path.join(image_dir, "*.png"))
        if not image_paths:
            print(f"Nenhuma imagem .jpg ou .png encontrada em {image_dir}")
            return
            
    elif choice == '3':
        try:
            calibrator = CameraCalibrator()
            camera_matrix, dist_coeffs = calibrator.load_calibration("camera_calibration.xml")
            print("Calibração carregada com sucesso!")
            print(f"Matriz da câmera:\n{camera_matrix}")
            print(f"Coeficientes de distorção:\n{dist_coeffs}")
            
            test_img = input("Caminho para imagem de teste (ou Enter para pular): ")
            if test_img and os.path.exists(test_img):
                test_calibration(camera_matrix, dist_coeffs, test_img)
            return
        except Exception as e:
            print(f"Nenhuma calibração encontrada ou erro ao carregar: {e}")
            print("Execute uma calibração primeiro.")
            return
            
    else:
        return
    
    if len(image_paths) < 3:
        print("Precisa de pelo menos 3 imagens para calibração!")
        return
    
    # Inicializar calibrador
    calibrator = CameraCalibrator(chessboard_size=chessboard_size, square_size=square_size)
    
    # Opção: guardar imagens com cantos desenhados para verificação
    save_corners = input("\nDeseja guardar imagens com os cantos desenhados? (s/n): ").lower()
    if save_corners == 's':
        calibrator.save_images_with_corners(image_paths)
    
    try:
        # Calibrar câmera
        print("\nIniciando calibração...")
        ret, camera_matrix, dist_coeffs, rvecs, tvecs, reprojection_error, image_points = calibrator.calibrate_from_images(image_paths)
        
        # Exibir resultados
        print("\n" + "="*50)
        print("RESULTADOS DA CALIBRAÇÃO")
        print("="*50)
        print(f"Parâmetro de calibração (ret): {ret:.6f}")
        print(f"[pass] Erro médio de reprojeção: {reprojection_error:.4f} pixels")
        
        if reprojection_error < 0.5:
            print("  Excelente! Erro muito baixo.")
        elif reprojection_error < 1.0:
            print("  Bom! Erro aceitável.")
        else:
            print("  Aviso: Erro alto. Considere capturar mais imagens ou verificar o chessboard.")
        
        print("\nMatriz da Câmera (intrínsecos):")
        print(f"[{camera_matrix[0,0]:.2f}, 0, {camera_matrix[0,2]:.2f}]")
        print(f"[0, {camera_matrix[1,1]:.2f}, {camera_matrix[1,2]:.2f}]")
        print(f"[0, 0, 1]")
        
        print("\nCoeficientes de Distorção (k1, k2, p1, p2, k3):")
        print(f"[{dist_coeffs[0,0]:.6f}, {dist_coeffs[0,1]:.6f}, {dist_coeffs[0,2]:.6f}, {dist_coeffs[0,3]:.6f}, {dist_coeffs[0,4]:.6f}]")
        
        # Distância focal em pixels
        fx = camera_matrix[0,0]
        fy = camera_matrix[1,1]
        print(f"\nDistância focal: fx={fx:.2f}, fy={fy:.2f} pixels")
        print(f"Ponto principal (cx, cy): ({camera_matrix[0,2]:.2f}, {camera_matrix[1,2]:.2f}) pixels")
        
        # guardar parâmetros em XML
        calibrator.save_calibration(camera_matrix, dist_coeffs, "camera_calibration.xml")
        
        # Testar com uma imagem de exemplo
        test_choice = input("\nDeseja testar a calibração em uma imagem? (s/n): ").lower()
        if test_choice == 's':
            test_image_path = image_paths[0]
            test_calibration(camera_matrix, dist_coeffs, test_image_path)
        
    except Exception as e:
        print(f"\nErro durante a calibração: {e}")
        print("\nPossíveis soluções:")
        print("1. Verifique se o chessboard é visível em todas as imagens")
        print("2. Confirme o tamanho do chessboard (9x6 cantos internos)")
        print("3. Capture imagens com diferentes ângulos e distâncias")
        print("4. Evite imagens muito desfocadas ou com pouca iluminação")

if __name__ == "__main__":
    main()