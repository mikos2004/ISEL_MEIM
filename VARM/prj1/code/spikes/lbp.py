from collections import Counter

import cv2
import numpy as np
import matplotlib.pyplot as plt

def img2gray(img_path):
    """
    Carrega uma imagem e converte para escala de cinza
    
    Args:
        img_path (str): Path para a imagem
    
    Returns:
        img_cinza: Imagem em escala de cinza
    """
    # Carregar a imagem
    imagem = cv2.imread(img_path)
    
    if imagem is None:
        raise ValueError(f"Não foi possível carregar a imagem: {img_path}")
    
    # Converter BGR (OpenCV) para RGB e depois para escala de cinza
    # ou diretamente para escala de cinza
    img_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    
    return img_cinza


def div_blocos_3_3(img_cinza):
    """
    Cria blocos 3x3 onde cada pixel da imagem é o centro
    
    Returns:
        list: lista de blocos 3x3
        tuple: dimensões da imagem
    """

    altura, largura = img_cinza.shape

    # padding de 1 pixel à volta da imagem
    img_pad = np.pad(img_cinza, pad_width=1, mode='constant', constant_values=1)
    
    blocos = []

    for i in range(altura):
        for j in range(largura):
            bloco = img_pad[i:i+3, j:j+3]
            blocos.append(bloco)
    """
    print(f"Dimensão imagem: {altura}x{largura}")
    print(f"Nº pixels: {altura*largura}")
    print(f"Nº blocos gerados: {len(blocos)}")
    """

    return blocos, (altura, largura)

def lbp_from_block(bloco_3x3):
    """
    Aplica LBP em um bloco 3x3 comparando pixels vizinhos com o pixel central
    
    Args:
        bloco_3x3 (numpy.ndarray): Bloco de imagem 3x3 em escala de cinza
    
    Returns:
        int: Valor LBP (0-255) calculado para o bloco
    """
    if bloco_3x3.shape != (3, 3):
        raise ValueError(f"Bloco deve ser 3x3, mas tem dimensão {bloco_3x3.shape}")
    
    pixel_central = bloco_3x3[1, 1]
    
    # Inicializar valor LBP
    lbp_value = 0
    
    # Posições dos vizinhos em ordem (sentido horário)
    posicoes_vizinhos = [
        (0, 0), (0, 1), (0, 2),  # Primeira linha
        (1, 2),                   # Meio-direita
        (2, 2), (2, 1), (2, 0),  # Terceira linha
        (1, 0)                    # Meio-esquerda
    ]
    
    # Comparar cada vizinho com o pixel central
    for i, (linha, coluna) in enumerate(posicoes_vizinhos):
        pixel_vizinho = bloco_3x3[linha, coluna]
        
        # Se o pixel vizinho for maior ou igual ao central, bit = 1, senão bit = 0
        if pixel_vizinho >= pixel_central:
            # Adicionar 2^i ao valor LBP
            lbp_value += (1 << (7-i))  # máscara para fazer 2**(7-i)
    
    return lbp_value

def lbp_from_blocks_list(blocos):
    """
    Aplica LBP a uma lista de blocos 3x3
    
    Args:
        blocos: Lista de blocos 3x3
    
    Returns:
        list: Lista de valores LBP para cada bloco
    """
    lbp_values = []
    
    for bloco in blocos:
        try:
            lbp_val = lbp_from_block(bloco)
            lbp_values.append(lbp_val)

            #print(bloco)
            #print(lbp_val, format(lbp_val, 'b'))
        except Exception as e:
            print(f"Erro ao processar bloco: {e}")
            lbp_values.append(None)

    hist = Counter(lbp_values)
    
    return lbp_values, hist

if __name__ == "__main__":

    img_path = "att_faces\\s8\\1.pgm"
    
    try:
        # 1- Converter para grayscale
        img_cinza = img2gray(img_path)
        
        # 2- Dividir em blocos 3x3
        blocos, dimensoes_grade = div_blocos_3_3(img_cinza)
        
        
        """
        print(f"\nNúmero total de blocos: {len(blocos)}")
        print(f"Dimensões de cada bloco: {blocos[0].shape}")
        print(f"Valores do primeiro bloco:\n{blocos[0]}")
        """
         # 3- aplicar LBP nos blocos
        print("\n--- Aplicar LBP ---")
        
        todos_lbp, hist = lbp_from_blocks_list(blocos)
        
        """
        print(f"\nTotal de valores LBP calculados: {len([v for v in todos_lbp if v is not None])}")
        print("Bloco 1:", todos_lbp[0])
        print(hist)
        """
        
    except Exception as e:
        print(f"Erro: {e}")