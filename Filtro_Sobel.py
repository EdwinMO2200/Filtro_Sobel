from PIL import Image
import math
import os

RUTA_BASE = r"rute donde tienes la imagen"   
NOMBRE_ARCHIVO = "Nombre del archivo.jpg"
RUTA_ENTRADA = os.path.join(RUTA_BASE, NOMBRE_ARCHIVO)

SOBEL_3X3_X = [
    [-1,  0,  1],
    [-2,  0,  2],
    [-1,  0,  1]
]

SOBEL_3X3_Y = [
    [-1, -2, -1],
    [ 0,  0,  0],
    [ 1,  2,  1]
]

SOBEL_7X7_X = [
    [-1, -2, -3,  0,  3,  2,  1],
    [-2, -4, -6,  0,  6,  4,  2],
    [-3, -6, -9,  0,  9,  6,  3],
    [-4, -8,-12,  0, 12,  8,  4],
    [-3, -6, -9,  0,  9,  6,  3],
    [-2, -4, -6,  0,  6,  4,  2],
    [-1, -2, -3,  0,  3,  2,  1]
]

SOBEL_7X7_Y = [
    [-1, -2, -3, -4, -3, -2, -1],
    [-2, -4, -6, -8, -6, -4, -2],
    [-3, -6, -9,-12, -9, -6, -3],
    [ 0,  0,  0,  0,  0,  0,  0],
    [ 3,  6,  9, 12,  9,  6,  3],
    [ 2,  4,  6,  8,  6,  4,  2],
    [ 1,  2,  3,  4,  3,  2,  1]
]


def convertir_a_grises_promedio(imagen_rgb):
    """
    Convierte una imagen RGB a escala de grises calculando
    la media aritmética: Y = (R + G + B) / 3
    """
    ancho, alto = imagen_rgb.size
    pixeles = imagen_rgb.load()
    
    # Crear matriz vacía 2D con ceros
    matriz_gris = [[0 for _ in range(ancho)] for _ in range(alto)]
    
    for y in range(alto):
        for x in range(ancho):
            r, g, b = pixeles[x, y][:3]
            promedio = int((r + g + b) / 3)
            matriz_gris[y][x] = promedio
            
    return matriz_gris, ancho, alto


def aplicar_padding_cero(matriz, alto, ancho, pad_size):
   
    alto_pad = alto + 2 * pad_size
    ancho_pad = ancho + 2 * pad_size
    matriz_pad = [[0 for _ in range(ancho_pad)] for _ in range(alto_pad)]
    
    for y in range(alto):
        for x in range(ancho):
            matriz_pad[y + pad_size][x + pad_size] = matriz[y][x]
            
    return matriz_pad


def aplicar_convolucion_sobel(matriz_gris, alto, ancho, kernel_x, kernel_y, tam_k):
    """
    Aplica la convolución calcula la magnitud
    del gradiente y normaliza los resultados.
    """
    pad_size = tam_k // 2
    matriz_pad = aplicar_padding_cero(matriz_gris, alto, ancho, pad_size)
    
    magnitudes = [[0.0 for _ in range(ancho)] for _ in range(alto)]
    
    divisor_escala = 1.0 if tam_k == 3 else 12.0
    
    max_mag = 0.0
    
    for y in range(alto):
        for x in range(ancho):
            gx = 0.0
            gy = 0.0
            
            for ky in range(tam_k):
                for kx in range(tam_k):
                    val_pixel = matriz_pad[y + ky][x + kx]
                    gx += val_pixel * kernel_x[ky][kx]
                    gy += val_pixel * kernel_y[ky][kx]
            
            gx /= divisor_escala
            gy /= divisor_escala
            
            mag = math.sqrt(gx**2 + gy**2)
            magnitudes[y][x] = mag
            
            if mag > max_mag:
                max_mag = mag
                
    matriz_bordes = [[0 for _ in range(ancho)] for _ in range(alto)]
    for y in range(alto):
        for x in range(ancho):
            if max_mag > 0:
                val_norm = int((magnitudes[y][x] / max_mag) * 255)
            else:
                val_norm = 0
            matriz_bordes[y][x] = val_norm
            
    return matriz_bordes


def guardar_matriz_como_imagen(matriz, alto, ancho, nombre_salida):
    """
    Convierte la matriz procesada de nuevo a una imagen y la guarda.
    """
    img_salida = Image.new("L", (ancho, alto))
    pixeles = img_salida.load()
    
    for y in range(alto):
        for x in range(ancho):
            pixeles[x, y] = matriz[y][x]
            
    ruta_salida = os.path.join(RUTA_BASE, nombre_salida)
    img_salida.save(ruta_salida)
    print(f"[✔] Imagen guardada exitosamente en: {ruta_salida}")

if __name__ == "__main__":
    print(f"Buscando archivo de imagen en: '{RUTA_ENTRADA}'...")
    
    try:
        img_original = Image.open(RUTA_ENTRADA)
        print(f"¡Imagen '{NOMBRE_ARCHIVO}' cargada con éxito!")
        
        print("\n1. Convirtiendo a escala de grises mediante promedio...")
        matriz_gris, ancho, alto = convertir_a_grises_promedio(img_original)
        guardar_matriz_como_imagen(matriz_gris, alto, ancho, "1_grises.jpeg")
        
        print("\n2. Aplicando filtro Sobel 3x3...")
        bordes_3x3 = aplicar_convolucion_sobel(matriz_gris, alto, ancho, SOBEL_3X3_X, SOBEL_3X3_Y, 3)
        guardar_matriz_como_imagen(bordes_3x3, alto, ancho, "2_sobel_3x3.jpeg")
        
        print("\n3. Aplicando filtro Sobel 7x7...")
        bordes_7x7 = aplicar_convolucion_sobel(matriz_gris, alto, ancho, SOBEL_7X7_X, SOBEL_7X7_Y, 7)
        guardar_matriz_como_imagen(bordes_7x7, alto, ancho, "3_sobel_7x7.jpeg")
        
        print("PROCESO COMPLETADO")
        
    except FileNotFoundError:
        print(f"\n[ERROR CRÍTICO] No se encontró la imagen en la ruta:")
        print(f" -> {RUTA_ENTRADA}")
        print("Por favor verifica que la carpeta exista y el archivo se llame 'Nombre de tu archivo.jpeg'.")