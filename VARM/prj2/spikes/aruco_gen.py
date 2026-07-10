"""
Gera um board 3x2 de marcas ArUco (DICT_6X6_250)
Fundo preto, marcas brancas, bem separadas entre si.

IDs usados: 0, 1, 2, 3, 4, 5  (podes alterar em MARKER_IDS)
"""

import numpy as np
import cv2
import cv2.aruco as aruco

# ── Configuração ──────────────────────────────────────────────────────────────
COLS          = 3          # colunas do board
ROWS          = 2          # linhas do board
MARKER_IDS    = [0, 1, 2, 3, 4, 5]   # IDs a usar (tem de ter COLS*ROWS elementos)

MARKER_SIZE_PX  = 180      # tamanho de cada marca em píxeis
MARGIN_PX       = 60       # margem exterior (borda preta à volta do board)
GAP_PX          = 60       # espaço entre marcas (separador preto)

SHOW_IDS        = True     # mostrar número do ID por baixo de cada marca
FONT_SCALE      = 1.0
FONT_THICKNESS  = 2
OUTPUT_FILE     = "board_aruco_3x2.png"
# ─────────────────────────────────────────────────────────────────────────────

def generate_board():
    assert len(MARKER_IDS) == COLS * ROWS, \
        f"MARKER_IDS deve ter {COLS*ROWS} elementos, tem {len(MARKER_IDS)}."

    # Dicionário ArUco igual ao do detector
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)

    # Calcular tamanho total da imagem
    label_h = 30 if SHOW_IDS else 0          # altura reservada para o ID
    cell_h  = MARKER_SIZE_PX + label_h       # altura de cada célula
    cell_w  = MARKER_SIZE_PX

    board_w = 2 * MARGIN_PX + COLS * cell_w  + (COLS - 1) * GAP_PX
    board_h = 2 * MARGIN_PX + ROWS * cell_h  + (ROWS - 1) * GAP_PX

    # Canvas todo branco (folha A4 / papel normal)
    board = np.ones((board_h, board_w), dtype=np.uint8) * 255

    for idx, marker_id in enumerate(MARKER_IDS):
        row = idx // COLS
        col = idx  % COLS

        # Canto superior-esquerdo da célula
        x0 = MARGIN_PX + col * (cell_w + GAP_PX)
        y0 = MARGIN_PX + row * (cell_h + GAP_PX)

        # Gerar imagem da marca (fundo branco, marca preta — standard ArUco)
        marker_img = np.zeros((MARKER_SIZE_PX, MARKER_SIZE_PX), dtype=np.uint8)
        aruco.generateImageMarker(aruco_dict, marker_id, MARKER_SIZE_PX, marker_img, 1)

        # Colar a marca no canvas (sem inversão)
        board[y0:y0 + MARKER_SIZE_PX, x0:x0 + MARKER_SIZE_PX] = marker_img

        # Etiqueta com o ID (texto preto)
        if SHOW_IDS:
            label   = f"ID {marker_id}"
            font    = cv2.FONT_HERSHEY_SIMPLEX
            (tw, th), _ = cv2.getTextSize(label, font, FONT_SCALE, FONT_THICKNESS)
            tx = x0 + (cell_w - tw) // 2
            ty = y0 + MARKER_SIZE_PX + th + 6
            cv2.putText(board, label, (tx, ty),
                        font, FONT_SCALE, 0, FONT_THICKNESS, cv2.LINE_AA)

    # Guardar ficheiro
    cv2.imwrite(OUTPUT_FILE, board)
    print(f"Board guardado em: {OUTPUT_FILE}")
    print(f"Tamanho: {board_w} x {board_h} px")
    print(f"IDs incluídos: {MARKER_IDS}")

    # Mostrar preview (fecha com qualquer tecla)
    cv2.imshow("Board ArUco 3x2 — DICT_6X6_250", board)
    print("Prima qualquer tecla para fechar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    generate_board()