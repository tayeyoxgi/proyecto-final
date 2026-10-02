import pygame
import random
import os

# --- 1. CONFIGURACIÓN INICIAL DE PYGAME ---
pygame.init()
ancho, alto = 800, 600
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Asteroids Space Simulator - Versión Vectorial Unificada")
reloj = pygame.time.Clock()

# --- 2. CARGA DE IMÁGENES (Con respaldo por si no existen) ---
ruta_carpeta = r"C:\Users\eddyg\Desktop\prollectos p\proyecto_final"
ruta_tierra = os.path.join(ruta_carpeta, "tierra.png")
ruta_halcon = os.path.join(ruta_carpeta, "halcon.png")
ruta_asteroide = os.path.join(ruta_carpeta, "asteroide.png")

# Carga de la Nave
if os.path.exists(ruta_halcon):
    img_halcon_base = pygame.image.load(ruta_halcon).convert_alpha()
    img_halcon = pygame.transform.scale(img_halcon_base, (45, 45))
else:
    img_halcon = pygame.Surface((45, 45), pygame.SRCALPHA)
    pygame.draw.polygon(img_halcon, (0, 255, 255), [(22, 0), (0, 45), (45, 45)], 2)

# Carga de la Tierra
if os.path.exists(ruta_tierra):
    img_tierra_base = pygame.image.load(ruta_tierra).convert_alpha()
    img_tierra = pygame.transform.scale(img_tierra_base, (1200, 350))
    usar_tierra = True
else:
    usar_tierra = False

# Carga del molde del Asteroide
if os.path.exists(ruta_asteroide):
    img_asteroide_original = pygame.image.load(ruta_asteroide).convert_alpha()
    usar_asteroide_img = True
else:
    usar_asteroide_img = False

# --- 3. VARIABLES DE JUEGO SIMPLES ---
estado = "despegando"
puntuacion = 0
nombre_piloto = "Piloto Alfa"

# Físicas automáticas de la nave usando Vector2
posicion_nave = pygame.math.Vector2(400, 590)
velocidad_nave = pygame.math.Vector2(0, 0)
nave_angulo = 0

planeta_y = 725
disparos = []
particulas = []
asteroides = []

# Crear 60 estrellas de fondo fijas
estrellas = [[random.randint(0, ancho), random.randint(0, alto)] for _ in range(60)]

# --- 4. FUNCIÓN PARA CREAR UN ASTEROIDE LENTO (100% SIN FÓRMULAS) ---
def crear_asteroide():
    global asteroides, img_asteroide_original, usar_asteroide_img
    
    # Aparecen en los bordes alejados de la nave
    x = random.choice([random.randint(0, 200), random.randint(600, ancho)])
    y = random.choice([random.randint(0, 150), random.randint(450, alto)])
    
    radio = random.choice([15, 30, 50])
    diametro = radio * 2
    
    if usar_asteroide_img:
        img_escalada = pygame.transform.scale(img_asteroide_original, (diametro, diametro))
        img_render = pygame.transform.rotate(img_escalada, random.randint(0, 360))
    else:
        img_render = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
        pygame.draw.circle(img_render, (160, 160, 165), (radio, radio), radio, 2)
    
    # Dirección y velocidad lenta usando solo las flechas inteligentes (Vector2) de Pygame
    velocidad_lenta = random.uniform(0.3, 0.8)
    vector_velocidad = pygame.math.Vector2(0, -velocidad_lenta).rotate(random.randint(0, 360))
    
    asteroides.append({
        "img": img_render,
        "pos": pygame.math.Vector2(x, y),
        "vel": vector_velocidad,
        "radio": radio
    })

# --- 5. BUCLE PRINCIPAL DE JUEGO (60 FPS) ---
ejecutando = True
while ejecutando:
    reloj.tick(60)
    
    # Detectar eventos independientes
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and estado == "jugando":
                # Disparo vectorial sin trigonometría manual
                flecha_disparo = pygame.math.Vector2(0, -10).rotate(-nave_angulo)
                disparos.append({"pos": pygame.math.Vector2(posicion_nave), "vel": flecha_disparo})

    teclas = pygame.key.get_pressed()
    
    # Fase A: Control automático de despegue cinemático lento
    if estado == "despegando":
        posicion_nave.y -= 1  
        planeta_y += 0.5
        
        # Chispas del motor en el despegue cayendo hacia abajo
        particulas.append({
            "pos": pygame.math.Vector2(posicion_nave.x + random.uniform(-4, 4), posicion_nave.y + 20), 
            "vel": pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(2, 4)),
            "radio": random.uniform(5.0, 7.0),
            "color": random.choice([(255, 68, 0), (255, 136, 0), (255, 204, 0)])
        })
        
        if posicion_nave.y <= 300:
            estado = "jugando"
            # Al llegar al espacio exterior, nacen los 8 asteroides en el mapa
            for _ in range(8):
                crear_asteroide()
            
    # Fase B: Vuelo libre y suave en el espacio
    elif estado == "jugando":
        if teclas[pygame.K_LEFT]:  nave_angulo += 5
        if teclas[pygame.K_RIGHT]: nave_angulo -= 5
        
        if teclas[pygame.K_UP]:
            flecha_empuje = pygame.math.Vector2(0, -0.15).rotate(-nave_angulo)
            velocidad_nave += flecha_empuje
            
            # Estela de propulsión manual realista
            flecha_escape = pygame.math.Vector2(0, 3).rotate(-nave_angulo)
            particulas.append({
                "pos": pygame.math.Vector2(posicion_nave), 
                "vel": flecha_escape + pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)),
                "radio": random.uniform(4.0, 6.0),
                "color": random.choice([(255, 68, 0), (255, 136, 0), (255, 204, 0)])
            })
            
        if teclas[pygame.K_DOWN]:
            flecha_freno = pygame.math.Vector2(0, 0.1).rotate(-nave_angulo)
            velocidad_nave += flecha_freno

        # Fricción y limitador de velocidad máxima automática
        velocidad_nave *= 0.98
        if velocidad_nave.length() > 5.0:
            velocidad_nave.scale_to_length(5.0)
            
        posicion_nave += velocidad_nave

        # Efecto espejo en los bordes para la nave
        if posicion_nave.x < -20: posicion_nave.x = ancho + 20
        elif posicion_nave.x > ancho + 20: posicion_nave.x = -20
        if posicion_nave.y < -20: posicion_nave.y = alto + 20
        elif posicion_nave.y > alto + 20: posicion_nave.y = -20

        # Mover los asteroides lentos
        for ast in asteroides:
            ast["pos"] += ast["vel"]
            
            # Estela cósmica brillante azul/cian detrás de los asteroides
            if random.random() < 0.2:
                particulas.append({
                    "pos": ast["pos"] + pygame.math.Vector2(random.uniform(-8, 8), random.uniform(-8, 8)),
                    "vel": pygame.math.Vector2(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3)),
                    "radio": random.uniform(2.0, 4.0),
                    "color": random.choice([(0, 255, 255), (0, 170, 204), (68, 136, 255)])
                })
            
            # Límite de pantalla infinita para los asteroides
            if ast["pos"].x < -50: ast["pos"].x = ancho + 50
            elif ast["pos"].x > ancho + 50: ast["pos"].x = -50
            if ast["pos"].y < -50: ast["pos"].y = alto + 50
            elif ast["pos"].y > alto + 50: ast["pos"].y = -50

    # --- 6. ACTUALIZACIÓN DE PROYECTILES Y DESVANECIMIENTO ---
    for d in disparos: 
        d["pos"] += d["vel"]
    for p in particulas: 
        if estado == "despegando": p["pos"] += p["vel"]
        p["radio"] -= 0.1        
    
    # Filtros de limpieza para liberar memoria
    disparos = [d for d in disparos if 0 <= d["pos"].x <= ancho and 0 <= d["pos"].y <= alto]
    particulas = [p for p in particulas if p["radio"] > 0]

    # --- 7. VERIFICACIÓN DE IMPACTOS DE LÁSER (SCORE) ---
    for d in disparos[:]:
        for ast in asteroides[:]:
            # Pygame calcula la distancia de forma nativa e inteligente entre el láser y el asteroide
            distancia = d["pos"].distance_to(ast["pos"])
            if distancia < ast["radio"]:
                if d in disparos: disparos.remove(d)
                if ast in asteroides: asteroides.remove(ast)
                puntuacion += 10  # Ganas puntos
                crear_asteroide() # Regenera un enemigo de reemplazo
                break

    # --- 8. RENDERIZADO GRÁFICO (DIBUJO) ---
    pantalla.fill((8, 8, 16))

    # Dibujar Estrellas
    for est in estrellas:
        pygame.draw.circle(pantalla, (255, 255, 255), est, 1)

    # Dibujar Planeta Tierra en despegue
    if estado == "despegando":
        if usar_tierra:
            pantalla.blit(img_tierra, img_tierra.get_rect(center=(400, planeta_y)))
        else:
            pygame.draw.circle(pantalla, (51, 17, 85), (400, int(planeta_y)), 300)

    # Dibujar todas las partículas (Fuego de motor y estelas de asteroides)
    for p in particulas:
        pygame.draw.circle(pantalla, p["color"], (int(p["pos"].x), int(p["pos"].y)), int(p["radio"]))

    # Dibujar Láseres activos
    for d in disparos:
        pygame.draw.circle(pantalla, (0, 255, 255), (int(d["pos"].x), int(d["pos"].y)), 3)

    # Dibujar Asteroides activos
    for ast in asteroides:
        rect_ast = ast["img"].get_rect(center=(int(ast["pos"].x), int(ast["pos"].y)))
        pantalla.blit(ast["img"], rect_ast.topleft)

    # Rotar y dibujar el Halcón Milenario de forma nativa en una línea
    halcon_rotado = pygame.transform.rotate(img_halcon, nave_angulo)
    pantalla.blit(halcon_rotado, halcon_rotado.get_rect(center=(int(posicion_nave.x), int(posicion_nave.y))))

    # Marcador de Score
    fuente = pygame.font.SysFont("Courier New", 14, bold=True)
    txt = fuente.render(f"PILOTO: {nombre_piloto}   |   SCORE: {puntuacion}", True, (0, 255, 102))
    pantalla.blit(txt, (20, 20))

    pygame.display.flip()

pygame.quit()
