import pygame
import random
import os

# --- 1. CONFIGURACIÓN INICIAL DE PYGAME ---
pygame.init()
ancho, alto = 800, 600
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Simulador de Asteroides Lentos con Pygame")
reloj = pygame.time.Clock()

# --- 2. CARGA DE LA IMAGEN (Con respaldo geométrico si no existe) ---
ruta_carpeta = r"C:\Users\eddyg\Desktop\prollectos p\proyecto_final"
ruta_asteroide = os.path.join(ruta_carpeta, "asteroide.png")

if os.path.exists(ruta_asteroide):
    img_asteroide_original = pygame.image.load(ruta_asteroide).convert_alpha()
    usar_asteroide_img = True
else:
    usar_asteroide_img = False

# --- 3. VARIABLES DEL SIMULADOR ---
puntuacion = 0
nombre_piloto = "Piloto Alfa"

asteroides = []
particulas = []

# Crear 60 estrellas de fondo fijas
estrellas = [[random.randint(0, ancho), random.randint(0, alto)] for _ in range(60)]

# --- 4. FUNCIÓN PARA CREAR UN ASTEROIDE LENTO ---
def crear_asteroide():
    global asteroides, img_asteroide_original, usar_asteroide_img
    
    # Aparecen distribuidos aleatoriamente por la pantalla
    x = random.randint(50, ancho - 50)
    y = random.randint(50, alto - 50)
    
    # Tamaños variados aleatorios (Radios de 15, 30 o 50)
    radio = random.choice([15, 30, 50])
    diametro = radio * 2
    
    if usar_asteroide_img:
        # Redimensionar y rotar visualmente el asteroide de forma nativa en una línea
        img_escalada = pygame.transform.scale(img_asteroide_original, (diametro, diametro))
        img_render = pygame.transform.rotate(img_escalada, random.randint(0, 360))
    else:
        # Respaldo geométrico si la imagen no está en la carpeta
        img_render = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
        pygame.draw.circle(img_render, (160, 160, 165), (radio, radio), radio, 2)
    
    # ¡CORREGIDO!: Velocidad base reducida para un movimiento lento y controlado
    velocidad_lenta = random.uniform(0.3, 0.8)
    vector_velocidad = pygame.math.Vector2(0, -velocidad_lenta).rotate(random.randint(0, 360))
    
    asteroides.append({
        "img": img_render,
        "pos": pygame.math.Vector2(x, y),
        "vel": vector_velocidad,
        "radio": radio
    })

# Creamos los 8 asteroides iniciales del simulador
for _ in range(8):
    crear_asteroide()

# --- 5. BUCLE PRINCIPAL DE JUEGO (60 FPS) ---
ejecutando = True
while ejecutando:
    reloj.tick(60)
    
    # Cerrar la ventana de forma segura si le das a la X
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # --- MOVIMIENTO Y LÓGICA DE LOS ASTEROIDES ---
    for ast in asteroides:
        # Sumamos la flecha de velocidad a la posición (Física automática)
        ast["pos"] += ast["vel"]
        
        # Generar estela cósmica brillante detrás de los asteroides en movimiento
        if random.random() < 0.2:
            particulas.append({
                "pos": ast["pos"] + pygame.math.Vector2(random.uniform(-8, 8), random.uniform(-8, 8)),
                "vel": pygame.math.Vector2(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3)),
                "radio": random.uniform(2.0, 4.0),
                "color": random.choice([(0, 255, 255), (0, 170, 204), (68, 136, 255)])
            })
        
        # Límite de pantalla infinita (Efecto espejo) usando condicionales limpios
        if ast["pos"].x < -50: ast["pos"].x = ancho + 50
        elif ast["pos"].x > ancho + 50: ast["pos"].x = -50
        if ast["pos"].y < -50: ast["pos"].y = alto + 50
        elif ast["pos"].y > alto + 50: ast["pos"].y = -50

    # Actualizar partículas de polvo cósmico (Hacerlas más pequeñas)
    for p in particulas:
        p["pos"] += p["vel"]
        p["radio"] -= 0.1        
    
    # Limpiar de la memoria las partículas que se desvanecen
    particulas = [p for p in particulas if p["radio"] > 0]

    # --- 6. RENDERIZADO GRÁFICO (DIBUJO) ---
    pantalla.fill((8, 8, 16)) # Fondo del espacio profundo

    # Dibujar Estrellas de fondo fijas
    for est in estrellas:
        pygame.draw.circle(pantalla, (255, 255, 255), est, 1)

    # Dibujar todas las partículas activas de las estelas
    for p in particulas:
        pygame.draw.circle(pantalla, p["color"], (int(p["pos"].x), int(p["pos"].y)), int(p["radio"]))

    # Dibujar Asteroides activos con sus imágenes rotadas
    for ast in asteroides:
        rect_ast = ast["img"].get_rect(center=(int(ast["pos"].x), int(ast["pos"].y)))
        pantalla.blit(ast["img"], rect_ast.topleft)

    # Dibujar Marcador Superior de Score
    fuente = pygame.font.SysFont("Courier New", 14, bold=True)
    txt = fuente.render(f"PILOTO: {nombre_piloto}   |   SCORE: {puntuacion}", True, (0, 255, 102))
    pantalla.blit(txt, (20, 20))

    pygame.display.flip() # Actualiza los gráficos en tu monitor

pygame.quit()
