import pygame
import random
import os

# --- 1. CONFIGURACION INICIAL DE PYGAME ---
pygame.init()
ancho, alto = 800, 600
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Asteroids Space Simulator - Version Completa")
reloj = pygame.time.Clock()

pantalla.fill((8, 8, 16))
pygame.display.flip()

# --- 2. CARGA DE IMAGENES (con respaldo geometrico si no existen) ---
ruta_carpeta = r"C:\\Users\\eddyg\\Desktop\\prollectos p\\proyecto_final"
ruta_tierra = os.path.join(ruta_carpeta, "tierra.png")
ruta_halcon = os.path.join(ruta_carpeta, "halcon.png")
ruta_asteroide = os.path.join(ruta_carpeta, "asteroide.png")

# Nave
if os.path.exists(ruta_halcon):
    img_halcon_base = pygame.image.load(ruta_halcon).convert_alpha()
    img_halcon = pygame.transform.scale(img_halcon_base, (45, 45))
else:
    img_halcon = pygame.Surface((45, 45), pygame.SRCALPHA)
    pygame.draw.polygon(img_halcon, (0, 255, 255), [(22, 0), (0, 45), (45, 45)], 2)

# Tierra
if os.path.exists(ruta_tierra):
    img_tierra_base = pygame.image.load(ruta_tierra).convert_alpha()
    img_tierra = pygame.transform.scale(img_tierra_base, (1200, 350))
    usar_tierra = True
else:
    usar_tierra = False

# Molde del asteroide
if os.path.exists(ruta_asteroide):
    img_asteroide_original = pygame.image.load(ruta_asteroide).convert_alpha()
    usar_asteroide_img = True
else:
    img_asteroide_original = None
    usar_asteroide_img = False

# --- 3. FUENTES ---
fuente_hud = pygame.font.SysFont("Courier New", 16, bold=True)
fuente_grande = pygame.font.SysFont("Courier New", 48, bold=True)
fuente_media = pygame.font.SysFont("Courier New", 24, bold=True)

# --- 4. PUNTOS POR TAMANO DEL ASTEROIDE ---
# Mientras mas pequeno (y dificil de darle), mas puntos vale.
PUNTOS_POR_RADIO = {
    50: 10,   # grande
    30: 20,   # mediano
    15: 30,   # pequeno
}

# --- 5. CONFIGURACION DE NIVELES ---
# Puntos necesarios para pasar al siguiente nivel.
PUNTOS_PARA_SUBIR = 150
NIVEL_MAXIMO = 5

# --- 6. VARIABLES DE JUEGO ---
# Estados posibles: "nombre" -> "despegando" -> "jugando" -> "nivel" -> "game_over" -> "ganaste"
estado = "nombre"
nombre_piloto = ""
puntuacion = 0
nivel = 1

posicion_nave = pygame.math.Vector2(400, 590)
velocidad_nave = pygame.math.Vector2(0, 0)
nave_angulo = 0

planeta_y = 725
disparos = []
particulas = []
asteroides = []

# Temporizador para mostrar el cartel de "Nivel X"
timer_nivel = 0

estrellas = [[random.randint(0, ancho), random.randint(0, alto), random.choice([1, 2])] for _ in range(60)]


# --- 7. FACTOR DE VELOCIDAD SEGUN EL NIVEL ---
# Los asteroides se hacen un poquito mas rapidos casi al final.
def factor_velocidad(nivel_actual):
    # Nivel 1 = x1.0, nivel 2 = x1.2, ... sube de a poco.
    return 1.0 + (nivel_actual - 1) * 0.25


# --- 8. FUNCION PARA CREAR UN ASTEROIDE ---
def crear_asteroide():
    global asteroides
    x = random.choice([random.randint(0, 200), random.randint(600, ancho)])
    y = random.choice([random.randint(0, 150), random.randint(450, alto)])

    radio = random.choice([15, 30, 50])
    diametro = radio * 2

    if usar_asteroide_img and img_asteroide_original:
        try:
            img_escalada = pygame.transform.scale(img_asteroide_original, (diametro, diametro))
            img_render = pygame.transform.rotate(img_escalada, random.randint(0, 360))
        except Exception:
            img_render = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
            pygame.draw.circle(img_render, (160, 160, 165), (radio, radio), radio, 2)
    else:
        img_render = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
        pygame.draw.circle(img_render, (160, 160, 165), (radio, radio), radio, 2)

    # Velocidad base lenta multiplicada por el factor del nivel actual.
    velocidad_lenta = random.uniform(0.3, 0.8) * factor_velocidad(nivel)
    vector_velocidad = pygame.math.Vector2(0, -velocidad_lenta).rotate(random.randint(0, 360))

    asteroides.append({
        "img": img_render,
        "pos": pygame.math.Vector2(x, y),
        "vel": vector_velocidad,
        "radio": radio,
    })


# --- 9. REINICIAR TODO EL JUEGO (empezar de nuevo) ---
def reiniciar_juego():
    global estado, puntuacion, nivel, posicion_nave, velocidad_nave
    global nave_angulo, planeta_y, timer_nivel
    estado = "despegando"
    puntuacion = 0
    nivel = 1
    posicion_nave = pygame.math.Vector2(400, 590)
    velocidad_nave = pygame.math.Vector2(0, 0)
    nave_angulo = 0
    planeta_y = 725
    timer_nivel = 0
    disparos.clear()
    asteroides.clear()
    particulas.clear()


# --- 10. PASAR AL SIGUIENTE NIVEL ---
def siguiente_nivel():
    global nivel, estado, timer_nivel
    nivel += 1
    if nivel > NIVEL_MAXIMO:
        estado = "ganaste"
        return
    estado = "nivel"
    timer_nivel = 120  # ~2 segundos mostrando el cartel
    asteroides.clear()
    disparos.clear()


# --- 11. BUCLE PRINCIPAL (60 FPS) ---
ejecutando = True
while ejecutando:
    reloj.tick(60)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        elif evento.type == pygame.KEYDOWN:
            # --- Pantalla de ingreso de nombre ---
            if estado == "nombre":
                if evento.key == pygame.K_RETURN and nombre_piloto.strip() != "":
                    reiniciar_juego()
                elif evento.key == pygame.K_BACKSPACE:
                    nombre_piloto = nombre_piloto[:-1]
                else:
                    # Solo caracteres imprimibles y maximo 14 letras
                    if evento.unicode and evento.unicode.isprintable() and len(nombre_piloto) < 14:
                        nombre_piloto += evento.unicode

            # --- Disparo durante el juego ---
            elif evento.key == pygame.K_SPACE and estado == "jugando":
                flecha_disparo = pygame.math.Vector2(0, -10).rotate(-nave_angulo)
                disparos.append({"pos": pygame.math.Vector2(posicion_nave), "vel": flecha_disparo})

            # --- Reiniciar tras game over o victoria ---
            elif evento.key == pygame.K_r and estado in ("game_over", "ganaste"):
                reiniciar_juego()

    teclas = pygame.key.get_pressed()

    # ============ LOGICA DE JUEGO ============
    if estado == "despegando":
        posicion_nave.y -= 1
        planeta_y += 0.5
        particulas.append({
            "pos": pygame.math.Vector2(posicion_nave.x + random.uniform(-4, 4), posicion_nave.y + 20),
            "vel": pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(2, 4)),
            "radio": random.uniform(5.0, 7.0),
            "color": random.choice([(255, 68, 0), (255, 136, 0), (255, 204, 0)]),
        })
        if posicion_nave.y <= 300:
            estado = "jugando"
            for _ in range(8):
                crear_asteroide()

    elif estado == "nivel":
        # Mostrar el cartel "Nivel X" un ratito y luego seguir jugando
        timer_nivel -= 1
        if timer_nivel <= 0:
            estado = "jugando"
            for _ in range(8):
                crear_asteroide()

    elif estado == "jugando":
        if teclas[pygame.K_LEFT]:
            nave_angulo += 5
        if teclas[pygame.K_RIGHT]:
            nave_angulo -= 5

        if teclas[pygame.K_UP]:
            flecha_empuje = pygame.math.Vector2(0, -0.15).rotate(-nave_angulo)
            velocidad_nave += flecha_empuje
            flecha_escape = pygame.math.Vector2(0, 3).rotate(-nave_angulo)
            particulas.append({
                "pos": pygame.math.Vector2(posicion_nave),
                "vel": flecha_escape + pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)),
                "radio": random.uniform(4.0, 6.0),
                "color": random.choice([(255, 68, 0), (255, 136, 0), (255, 204, 0)]),
            })
        if teclas[pygame.K_DOWN]:
            flecha_freno = pygame.math.Vector2(0, 0.1).rotate(-nave_angulo)
            velocidad_nave += flecha_freno

        velocidad_nave *= 0.98
        if velocidad_nave.length() > 5.0:
            velocidad_nave.scale_to_length(5.0)
        posicion_nave += velocidad_nave

        # Efecto espejo para la nave
        if posicion_nave.x < -20: posicion_nave.x = ancho + 20
        elif posicion_nave.x > ancho + 20: posicion_nave.x = -20
        if posicion_nave.y < -20: posicion_nave.y = alto + 20
        elif posicion_nave.y > alto + 20: posicion_nave.y = -20

        # Mover asteroides y detectar choque con la nave
        for ast in asteroides:
            ast["pos"] += ast["vel"]
            if random.random() < 0.2:
                particulas.append({
                    "pos": ast["pos"] + pygame.math.Vector2(random.uniform(-8, 8), random.uniform(-8, 8)),
                    "vel": pygame.math.Vector2(random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3)),
                    "radio": random.uniform(2.0, 4.0),
                    "color": random.choice([(0, 255, 255), (0, 170, 204), (68, 136, 255)]),
                })

            distancia_a_nave = posicion_nave.distance_to(ast["pos"])
            if distancia_a_nave < (ast["radio"] + 15):
                estado = "game_over"

            if ast["pos"].x < -50: ast["pos"].x = ancho + 50
            elif ast["pos"].x > ancho + 50: ast["pos"].x = -50
            if ast["pos"].y < -50: ast["pos"].y = alto + 50
            elif ast["pos"].y > alto + 50: ast["pos"].y = -50

        # Mover disparos
        for d in disparos:
            d["pos"] += d["vel"]
        disparos[:] = [d for d in disparos if 0 <= d["pos"].x <= ancho and 0 <= d["pos"].y <= alto]

        # Impactos de laser: puntos segun el tamano del asteroide
        for d in disparos[:]:
            for ast in asteroides[:]:
                distancia = d["pos"].distance_to(ast["pos"])
                if distancia < ast["radio"]:
                    if d in disparos: disparos.remove(d)
                    if ast in asteroides: asteroides.remove(ast)
                    puntuacion += PUNTOS_POR_RADIO.get(ast["radio"], 10)
                    crear_asteroide()
                    break

        # Revisar si hay que subir de nivel
        if puntuacion >= PUNTOS_PARA_SUBIR * nivel:
            siguiente_nivel()

    # Actualizar particulas siempre (menos en game over, para que se congele)
    if estado not in ("nombre", "game_over", "ganaste"):
        for p in particulas:
            if estado == "despegando":
                p["pos"] += p["vel"]
            p["radio"] -= 0.1
        particulas[:] = [p for p in particulas if p["radio"] > 0]

    # ============ RENDERIZADO ============
    pantalla.fill((8, 8, 16))
    for x_est, y_est, tam_est in estrellas:
        pygame.draw.circle(pantalla, (255, 255, 255), (x_est, y_est), tam_est)

    # ----- PANTALLA: INGRESAR NOMBRE -----
    if estado == "nombre":
        titulo = fuente_grande.render("ASTEROIDS", True, (0, 255, 255))
        pantalla.blit(titulo, titulo.get_rect(center=(ancho // 2, 180)))

        pide = fuente_media.render("Nombre del piloto:", True, (0, 255, 102))
        pantalla.blit(pide, pide.get_rect(center=(ancho // 2, 280)))

        # Cursor parpadeante
        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        caja = fuente_media.render(nombre_piloto + cursor, True, (255, 255, 255))
        pantalla.blit(caja, caja.get_rect(center=(ancho // 2, 330)))

        ayuda = fuente_hud.render("Escribe tu nombre y pulsa ENTER para empezar", True, (150, 150, 150))
        pantalla.blit(ayuda, ayuda.get_rect(center=(ancho // 2, 420)))

    else:
        # Planeta Tierra en el despegue
        if estado == "despegando":
            if usar_tierra:
                pantalla.blit(img_tierra, img_tierra.get_rect(center=(400, planeta_y)))
            else:
                pygame.draw.circle(pantalla, (51, 17, 85), (400, int(planeta_y)), 300)

        # Particulas
        for p in particulas:
            pygame.draw.circle(pantalla, p["color"], (int(p["pos"].x), int(p["pos"].y)), int(p["radio"]))

        # Laseres
        for d in disparos:
            pygame.draw.circle(pantalla, (0, 255, 255), (int(d["pos"].x), int(d["pos"].y)), 3)

        # Asteroides
        for ast in asteroides:
            rect_ast = ast["img"].get_rect(center=(int(ast["pos"].x), int(ast["pos"].y)))
            pantalla.blit(ast["img"], rect_ast.topleft)

        # Nave (rotada segun su angulo)
        if estado in ("despegando", "jugando", "nivel", "game_over"):
            nave_rotada = pygame.transform.rotate(img_halcon, nave_angulo)
            rect_nave = nave_rotada.get_rect(center=(int(posicion_nave.x), int(posicion_nave.y)))
            pantalla.blit(nave_rotada, rect_nave.topleft)

        # HUD superior
        objetivo = PUNTOS_PARA_SUBIR * nivel
        hud = fuente_hud.render(
            f"PILOTO: {nombre_piloto}  |  SCORE: {puntuacion}  |  NIVEL: {nivel}  |  META: {objetivo}",
            True, (0, 255, 102))
        pantalla.blit(hud, (20, 20))

        # Cartel de nuevo nivel
        if estado == "nivel":
            msg = fuente_grande.render(f"NIVEL {nivel}", True, (255, 204, 0))
            pantalla.blit(msg, msg.get_rect(center=(ancho // 2, alto // 2)))

        # ----- PANTALLA: GAME OVER -----
        if estado == "game_over":
            capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            capa.fill((0, 0, 0, 170))
            pantalla.blit(capa, (0, 0))
            go = fuente_grande.render("GAME OVER", True, (255, 60, 60))
            pantalla.blit(go, go.get_rect(center=(ancho // 2, 230)))
            sc = fuente_media.render(f"{nombre_piloto}, puntaje final: {puntuacion}", True, (255, 255, 255))
            pantalla.blit(sc, sc.get_rect(center=(ancho // 2, 300)))
            op = fuente_media.render("Pulsa R para jugar de nuevo", True, (0, 255, 102))
            pantalla.blit(op, op.get_rect(center=(ancho // 2, 360)))

        # ----- PANTALLA: VICTORIA -----
        if estado == "ganaste":
            capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            capa.fill((0, 0, 0, 170))
            pantalla.blit(capa, (0, 0))
            win = fuente_grande.render("GANASTE!", True, (0, 255, 255))
            pantalla.blit(win, win.get_rect(center=(ancho // 2, 230)))
            sc = fuente_media.render(f"{nombre_piloto}, completaste todos los niveles!", True, (255, 255, 255))
            pantalla.blit(sc, sc.get_rect(center=(ancho // 2, 300)))
            sc2 = fuente_media.render(f"Puntaje final: {puntuacion}", True, (255, 204, 0))
            pantalla.blit(sc2, sc2.get_rect(center=(ancho // 2, 340)))
            op = fuente_media.render("Pulsa R para jugar de nuevo", True, (0, 255, 102))
            pantalla.blit(op, op.get_rect(center=(ancho // 2, 400)))

    pygame.display.flip()

pygame.quit()