import pygame
import random
import os
import math

# --- 1. CONFIGURACIÓN INICIAL DE PYGAME ---
pygame.init()
ancho, alto = 800, 600
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Simulador Espacial - Control Suave")
reloj = pygame.time.Clock()

# --- 2. CARGA DE IMÁGENES (Con respaldo por si no existen) ---
ruta_carpeta = r"C:\Users\eddyg\Desktop\prollectos p\proyecto_final"
ruta_tierra = os.path.join(ruta_carpeta, "tierra.png")
ruta_halcon = os.path.join(ruta_carpeta, "halcon.png")

if os.path.exists(ruta_halcon):
    img_halcon_base = pygame.image.load(ruta_halcon).convert_alpha()
    img_halcon = pygame.transform.scale(img_halcon_base, (45, 45))
else:
    img_halcon = pygame.Surface((45, 45), pygame.SRCALPHA)
    pygame.draw.polygon(img_halcon, (0, 255, 255), [(22, 0), (0, 45), (45, 45)], 2)

if os.path.exists(ruta_tierra):
    img_tierra_base = pygame.image.load(ruta_tierra).convert_alpha()
    img_tierra = pygame.transform.scale(img_tierra_base, (1200, 350))
    usar_tierra = True
else:
    usar_tierra = False

# --- 3. VARIABLES DE JUEGO SIMPLES ---
estado = "despegando"
puntuacion = 0
nombre_piloto = "Piloto Alfa"

# Usamos Vector2 para la posición y velocidad (físicas automáticas)
posicion_nave = pygame.math.Vector2(400, 590)
velocidad_nave = pygame.math.Vector2(0, 0)
nave_angulo = 0

planeta_y = 725
disparos = []
particulas = []
estrellas = [[random.randint(0, ancho), random.randint(0, alto)] for _ in range(60)]

# --- 4. BUCLE PRINCIPAL DE JUEGO (60 FPS) ---
ejecutando = True
while ejecutando:
    reloj.tick(60)
    
    # Detectar eventos (Cerrar ventana y disparos)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and estado == "jugando":
                # El disparo sale hacia donde apunte la nave
                flecha_disparo = pygame.math.Vector2(0, -10).rotate(-nave_angulo)
                disparos.append({"pos": pygame.math.Vector2(posicion_nave), "vel": flecha_disparo})

    # Detectar controles continuos
    teclas = pygame.key.get_pressed()
    
    if estado == "despegando":
        # Despegue lento y cinemático
        posicion_nave.y -= 1  
        planeta_y += 0.5
        
        # Partículas de propulsión constantes durante el despegue hacia abajo
        particulas.append({
            "pos": pygame.math.Vector2(posicion_nave.x + random.uniform(-4, 4), posicion_nave.y + 20), 
            "vel": pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(2, 4)),
            "radio": random.uniform(5.0, 7.0)
        })
        
        if posicion_nave.y <= 300:
            estado = "jugando"
            
    elif estado == "jugando":
        # Girar la nave de forma fluida
        if teclas[pygame.K_LEFT]:  nave_angulo += 5
        if teclas[pygame.K_RIGHT]: nave_angulo -= 5
        
        # ¡CORREGIDO!: Empuje más suave para que no acelere tan bruscamente
        if teclas[pygame.K_UP]:
            flecha_empuje = pygame.math.Vector2(0, -0.15).rotate(-nave_angulo)
            velocidad_nave += flecha_empuje
            
            # Estela de propulsión manual realista
            flecha_escape = pygame.math.Vector2(0, 3).rotate(-nave_angulo)
            particulas.append({
                "pos": pygame.math.Vector2(posicion_nave), 
                "vel": flecha_escape + pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)),
                "radio": random.uniform(4.0, 6.0)
            })
            
        if teclas[pygame.K_DOWN]:
            flecha_freno = pygame.math.Vector2(0, 0.1).rotate(-nave_angulo)
            velocidad_nave += flecha_freno

        # Fricción del espacio (inercia automática)
        velocidad_nave *= 0.98
        
        # ¡NUEVO!: Limitador electrónico para que la nave no supere una velocidad incontrolable
        if velocidad_nave.length() > 5.0:
            velocidad_nave.scale_to_length(5.0)
            
        posicion_nave += velocidad_nave

        # Efecto espejo en los bordes
        if posicion_nave.x < -20: posicion_nave.x = ancho + 20
        elif posicion_nave.x > ancho + 20: posicion_nave.x = -20
        if posicion_nave.y < -20: posicion_nave.y = alto + 20
        elif posicion_nave.y > alto + 20: posicion_nave.y = -20

    # Actualizar posiciones de proyectiles y desvanecer partículas
    for d in disparos:   d["pos"] += d["vel"]
    for p in particulas: 
        if estado == "despegando":
            p["pos"] += p["vel"] 
        p["radio"] -= 0.1        
    
    # Limpiar lo que sale de pantalla o se apaga
    disparos = [d for d in disparos if 0 <= d["pos"].x <= ancho and 0 <= d["pos"].y <= alto]
    particulas = [p for p in particulas if p["radio"] > 0]

    # --- 5. DIBUJAR TODO EN PANTALLA ---
    pantalla.fill((8, 8, 16))

    # Dibujar Estrellas
    for est in estrellas:
        pygame.draw.circle(pantalla, (255, 255, 255), est, 1)

    # Dibujar Planeta Tierra
    if estado == "despegando":
        if usar_tierra:
            pantalla.blit(img_tierra, img_tierra.get_rect(center=(400, planeta_y)))
        else:
            pygame.draw.circle(pantalla, (51, 17, 85), (400, int(planeta_y)), 300)

    # Dibujar Partículas de Fuego y Estelas
    for p in particulas:
        color_fuego = random.choice([(255, 68, 0), (255, 136, 0), (255, 204, 0)])
        pygame.draw.circle(pantalla, color_fuego, (int(p["pos"].x), int(p["pos"].y)), int(p["radio"]))

    # Dibujar Láseres
    for d in disparos:
        pygame.draw.circle(pantalla, (0, 255, 255), (int(d["pos"].x), int(d["pos"].y)), 3)

    # Rotar y dibujar el Halcón Milenario
    halcon_rotado = pygame.transform.rotate(img_halcon, nave_angulo)
    pantalla.blit(halcon_rotado, halcon_rotado.get_rect(center=(int(posicion_nave.x), int(posicion_nave.y))))

    # Marcador de Score
    fuente = pygame.font.SysFont("Courier New", 14, bold=True)
    txt = fuente.render(f"PILOTO: {nombre_piloto}   |   SCORE: {puntuacion}", True, (0, 255, 102))
    pantalla.blit(txt, (20, 20))

    pygame.display.flip()

pygame.quit()
