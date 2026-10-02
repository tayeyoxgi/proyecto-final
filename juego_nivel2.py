import pygame
import random
import os
import json
from datetime import datetime, timezone

pygame.init()
ancho, alto = 800, 600
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Asteroids - Tierra a Luna 6570h REAL")
reloj = pygame.time.Clock()

ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
ruta_tiempo = os.path.join(ruta_carpeta, "mision_tiempo.json")

# Carpeta del proyecto donde estan las imagenes PNG
ruta_externa = r"C:\Users\eddyg\Desktop\prollectos p\proyecto_final"

# --- UTILIDADES PARA QUITAR EL CUADRADO DE LAS IMAGENES ---
def hacer_circular(surf, diametro):
    """Recorta una imagen en circulo para que no se vea el cuadrado."""
    escalada = pygame.transform.smoothscale(surf, (diametro, diametro)).convert_alpha()
    circ = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
    circ.fill((0, 0, 0, 0))
    mascara = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
    mascara.fill((0, 0, 0, 0))
    pygame.draw.circle(mascara, (255, 255, 255, 255), (diametro // 2, diametro // 2), diametro // 2)
    circ.blit(escalada, (0, 0))
    circ.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return circ

def quitar_halo_blanco(surf, umbral=180):
    """Hace transparentes los pixeles claros: quita la 'cosa blanca' que rodea al asteroide."""
    surf = surf.convert_alpha()
    ancho_s, alto_s = surf.get_size()
    surf.lock()
    for x in range(ancho_s):
        for y in range(alto_s):
            px = surf.get_at((x, y))
            if px.r >= umbral and px.g >= umbral and px.b >= umbral:
                surf.set_at((x, y), (px.r, px.g, px.b, 0))
    surf.unlock()
    return surf

def quitar_fondo(surf, tolerancia=30):
    """Quita el fondo solido (cuadrado) de una imagen tomando el color de la esquina."""
    surf = surf.convert_alpha()
    try:
        fondo = surf.get_at((0, 0))
    except Exception:
        return surf
    if fondo.a == 0:
        return surf  # ya es transparente, no hay cuadrado
    ancho_s, alto_s = surf.get_size()
    surf.lock()
    for x in range(ancho_s):
        for y in range(alto_s):
            px = surf.get_at((x, y))
            if (abs(px.r - fondo.r) < tolerancia and
                abs(px.g - fondo.g) < tolerancia and
                abs(px.b - fondo.b) < tolerancia):
                surf.set_at((x, y), (px.r, px.g, px.b, 0))
    surf.unlock()
    return surf

# --- CLASE PLANETA: OBJETOS SEPARADOS PARA CADA IMAGEN PNG ---
class Planeta:
    def __init__(self, nombre_archivo, diametro, y_inicial, color_fallback):
        self.nombre = nombre_archivo
        self.diametro = diametro
        self.y_inicial = y_inicial
        self.y = y_inicial
        self.x = 400
        self.img, self.existe = self.cargar_imagen_redonda(nombre_archivo, diametro, color_fallback)

    def cargar_imagen_redonda(self, nombre, diametro, fallback_color):
        """Quita el cuadrado feo haciendo el planeta circular"""
        posibles = [os.path.join(ruta_externa, nombre), os.path.join(ruta_carpeta, nombre), os.path.join(os.getcwd(), nombre), nombre]
        ruta_final = None
        for p in posibles:
            if os.path.exists(p):
                ruta_final = p
                break
        if ruta_final:
            try:
                original = pygame.image.load(ruta_final).convert_alpha()
                planeta = hacer_circular(original, diametro)
                print(f"[OK] {nombre} CIRCULO {diametro}px sin cuadrado")
                return planeta, True
            except Exception as e:
                print(f"[ERROR] {nombre}: {e}")
        print(f"[AVISO] {nombre} no encontrado")
        fallback = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
        fallback.fill((0, 0, 0, 0))
        pygame.draw.circle(fallback, fallback_color, (diametro // 2, diametro // 2), diametro // 2)
        return fallback, False

    def dibujar(self, superficie):
        rect = self.img.get_rect(center=(self.x, int(self.y)))
        superficie.blit(self.img, rect.topleft)

    def mover(self, dy):
        self.y += dy

    def reset(self):
        self.y = self.y_inicial

# OBJETOS DONDE VAN LAS IMAGENES (uno por nivel de despegue)
# y_inicial elegido para que el planeta sea VISIBLE abajo durante el despegue
planeta_tierra = Planeta("tierra.png", 600, 820, (25, 90, 180))   # NIVEL 1 - GRANDE
planeta_luna   = Planeta("luna.png", 380, 710, (190, 190, 200))   # NIVEL 2 - MEDIANA (antes no se veia)
planeta_marte  = Planeta("marte.png", 460, 740, (200, 90, 50))    # NIVEL 3+ - OBJETO EXTRA

def planeta_actual(n):
    if n == 1:
        return planeta_tierra
    elif n == 2:
        return planeta_luna
    return planeta_marte

# Nave
img_halcon = None
for p in [os.path.join(ruta_externa, "halcon.png"), os.path.join(ruta_carpeta, "halcon.png"), os.path.join(os.getcwd(), "halcon.png"), "halcon.png"]:
    if os.path.exists(p):
        try:
            cargada = pygame.image.load(p).convert_alpha()
            cargada = quitar_fondo(cargada)  # quita el cuadrado de fondo
            img_halcon = pygame.transform.smoothscale(cargada, (45, 45))
            break
        except Exception:
            pass
if not img_halcon:
    img_halcon = pygame.Surface((45, 45), pygame.SRCALPHA)
    pygame.draw.polygon(img_halcon, (0, 255, 255), [(22, 0), (0, 45), (45, 45)], 2)

img_asteroide_original = None
usar_asteroide_img = False
for p in [os.path.join(ruta_externa, "asteroide.png"), os.path.join(ruta_carpeta, "asteroide.png"), os.path.join(os.getcwd(), "asteroide.png"), "asteroide.png"]:
    if os.path.exists(p):
        try:
            img_asteroide_original = pygame.image.load(p).convert_alpha()
            img_asteroide_original = quitar_fondo(img_asteroide_original, tolerancia=40)  # quita el fondo negro
            img_asteroide_original = quitar_halo_blanco(img_asteroide_original)            # quita el halo blanco
            usar_asteroide_img = True
            break
        except Exception:
            pass

fuente_hud = pygame.font.SysFont("Courier New", 16, bold=True)
fuente_grande = pygame.font.SysFont("Courier New", 48, bold=True)
fuente_media = pygame.font.SysFont("Courier New", 24, bold=True)
fuente_peque = pygame.font.SysFont("Courier New", 14)
fuente_reloj = pygame.font.SysFont("Courier New", 18, bold=True)

# --- TIEMPO (TEMPORIZADOR) DISTINTO POR NIVEL ---
# Nivel 1: 72 horas para pasar al nivel 2
# Nivel 2: 6570 horas para pasar al nivel 3
HORAS_OBJETIVO = {1: 72.0, 2: 6570.0}

def horas_objetivo(n):
    return HORAS_OBJETIVO.get(n, 6570.0)

def segundos_max_nivel(n):
    return int(horas_objetivo(n) * 3600)

def guardar_inicio():
    try:
        ahora = datetime.now(timezone.utc)
        with open(ruta_tiempo, 'w') as f:
            json.dump({"inicio_utc": ahora.isoformat()}, f)
        return ahora
    except Exception:
        return datetime.now(timezone.utc)

def cargar_inicio():
    if os.path.exists(ruta_tiempo):
        try:
            with open(ruta_tiempo, 'r') as f:
                data = json.load(f)
                dt = datetime.fromisoformat(data["inicio_utc"])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
        except Exception:
            pass
    return guardar_inicio()

def tiempo_restante():
    ahora = datetime.now(timezone.utc)
    inicio = cargar_inicio()
    trans = (ahora - inicio).total_seconds()
    rest = segundos_max_nivel(nivel) - trans
    return rest, inicio, ahora

def horas_transcurridas():
    rest, _, _ = tiempo_restante()
    return (segundos_max_nivel(nivel) - rest) / 3600.0

def fmt(seg):
    if seg < 0:
        seg = 0
    h = int(seg // 3600)
    m = int((seg % 3600) // 60)
    s = int(seg % 60)
    return f"{h:02d}:{m:02d}:{s:02d}", seg / 3600

PUNTOS_POR_RADIO = {50: 10, 30: 20, 15: 30}
# Requisitos para subir de nivel (horas Y puntos)
REQUISITOS_NIVEL = {
    1: {"horas": 72.0,   "puntos": 1000},    # Nivel 1 -> Nivel 2
    2: {"horas": 6570.0, "puntos": 100000},  # Nivel 2 -> Nivel 3 (fin)
}
NIVEL_FINAL = 3  # al llegar al nivel 3 ya no hay mas niveles
estado = "nombre"
nombre_piloto = ""
puntuacion = 0
nivel = 1
cheat_buffer = ""
segundos_restantes, inicio_mision, ahora_utc = tiempo_restante()
posicion_nave = pygame.math.Vector2(400, 590)
velocidad_nave = pygame.math.Vector2(0, 0)
nave_angulo = 0
disparos = []
particulas = []
asteroides = []
estrellas = [[random.randint(0, ancho), random.randint(0, alto), random.choice([1, 2])] for _ in range(100)]

def factor_velocidad(n):
    return 1.0 + (n - 1) * 0.6

def crear_asteroide():
    # Aparecer lejos de la nave para no matar al jugador al instante
    x, y = 0, 0
    for _ in range(30):
        x = random.randint(0, ancho)
        y = random.randint(0, alto)
        if pygame.math.Vector2(x, y).distance_to(posicion_nave) > 180:
            break
    radio = random.choice([15, 30, 50])
    diametro = radio * 2
    if usar_asteroide_img and img_asteroide_original:
        try:
            # circular = sin cuadrado alrededor
            circ = hacer_circular(img_asteroide_original, diametro)
            img_r = pygame.transform.rotate(circ, random.randint(0, 360))
        except Exception:
            img_r = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
            pygame.draw.circle(img_r, (160, 160, 165), (radio, radio), radio, 2)
    else:
        img_r = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
        pygame.draw.circle(img_r, (160, 160, 165), (radio, radio), radio, 2)
    vel = random.uniform(0.3, 0.8) * factor_velocidad(nivel)
    vec = pygame.math.Vector2(0, -vel).rotate(random.randint(0, 360))
    asteroides.append({"img": img_r, "pos": pygame.math.Vector2(x, y), "vel": vec, "radio": radio})

def reiniciar_juego(reset_tiempo=True):
    global estado, puntuacion, nivel, posicion_nave, velocidad_nave, nave_angulo, cheat_buffer
    estado = "despegando"
    puntuacion = 0
    nivel = 1
    cheat_buffer = ""
    posicion_nave = pygame.math.Vector2(400, 590)
    velocidad_nave = pygame.math.Vector2(0, 0)
    nave_angulo = 0
    planeta_tierra.reset()
    planeta_luna.reset()
    planeta_marte.reset()
    disparos.clear(); asteroides.clear(); particulas.clear()
    if reset_tiempo:
        guardar_inicio()

def siguiente_nivel():
    global nivel, estado, nave_angulo
    nivel += 1
    # Al llegar al nivel 3 ya no hay mas niveles: mensaje y detener el juego
    if nivel >= NIVEL_FINAL:
        nivel = NIVEL_FINAL
        estado = "sin_niveles"
        asteroides.clear(); disparos.clear(); particulas.clear()
        print("NIVEL 3 alcanzado: ya no hay mas niveles. Juego detenido.")
        return
    # Pasar al nivel 2: la nave vuelve a su punto de origen y queda recta
    estado = "despegando"
    planeta_tierra.reset()
    planeta_luna.reset()
    planeta_marte.reset()
    posicion_nave.xy = (400, 590)
    velocidad_nave.xy = (0, 0)
    nave_angulo = 0  # nave recta en su punto de origen
    asteroides.clear(); disparos.clear(); particulas.clear()
    # El temporizador se reinicia con el objetivo de horas del nuevo nivel
    guardar_inicio()
    print(f"NIVEL {nivel}: Temporizador reiniciado ({horas_objetivo(nivel)}h). Despegando!")

ejecutando = True
while ejecutando:
    reloj.tick(60)
    segundos_restantes, inicio_mision, ahora_utc = tiempo_restante()
    tiempo_str, _ = fmt(segundos_restantes)
    horas_pasadas = (segundos_max_nivel(nivel) - segundos_restantes) / 3600.0

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            if estado == "nombre":
                if evento.key == pygame.K_RETURN and nombre_piloto.strip() != "":
                    reiniciar_juego(reset_tiempo=True)
                elif evento.key == pygame.K_BACKSPACE:
                    nombre_piloto = nombre_piloto[:-1]
                else:
                    if evento.unicode and evento.unicode.isprintable() and len(nombre_piloto) < 14:
                        nombre_piloto += evento.unicode
            elif evento.key == pygame.K_SPACE and estado == "jugando":
                flecha = pygame.math.Vector2(0, -10).rotate(-nave_angulo)
                disparos.append({"pos": pygame.math.Vector2(posicion_nave), "vel": flecha})
            elif evento.key == pygame.K_r and estado in ("game_over", "ganaste", "sin_niveles"):
                reiniciar_juego(reset_tiempo=True)
            if estado in ("despegando", "jugando") and evento.unicode and evento.unicode.isalpha():
                cheat_buffer = (cheat_buffer + evento.unicode.lower())[-10:]
                # Comando "esme": solo funciona para pasar del nivel 1 al nivel 2.
                if cheat_buffer.endswith("esme") and nivel == 1:
                    cheat_buffer = ""
                    siguiente_nivel()
                # Comando "marisol": solo funciona para pasar del nivel 2 al nivel 3.
                elif cheat_buffer.endswith("marisol") and nivel == 2:
                    cheat_buffer = ""
                    siguiente_nivel()

    teclas = pygame.key.get_pressed()
    if estado == "despegando":
        posicion_nave.y -= 1.2
        planeta_actual(nivel).mover(0.5)
        particulas.append({
            "pos": pygame.math.Vector2(posicion_nave.x + random.uniform(-4, 4), posicion_nave.y + 20),
            "vel": pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(2, 4)),
            "radio": random.uniform(5.0, 7.0),
            "color": random.choice([(255, 68, 0), (255, 136, 0), (255, 204, 0)])
        })
        if posicion_nave.y <= 320:
            estado = "jugando"
            for _ in range(8 if nivel == 1 else 10):
                crear_asteroide()
    elif estado == "jugando":
        if teclas[pygame.K_LEFT]: nave_angulo += 5
        if teclas[pygame.K_RIGHT]: nave_angulo -= 5
        if teclas[pygame.K_UP]:
            empuje = pygame.math.Vector2(0, -0.15).rotate(-nave_angulo)
            velocidad_nave += empuje
            escape = pygame.math.Vector2(0, 3).rotate(-nave_angulo)
            particulas.append({
                "pos": pygame.math.Vector2(posicion_nave),
                "vel": escape + pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)),
                "radio": random.uniform(3.0, 5.0),
                "color": random.choice([(255, 100, 0), (255, 200, 0)])
            })
        posicion_nave += velocidad_nave
        velocidad_nave *= 0.99
        if posicion_nave.x < 0: posicion_nave.x = ancho
        if posicion_nave.x > ancho: posicion_nave.x = 0
        if posicion_nave.y < 0: posicion_nave.y = alto
        if posicion_nave.y > alto: posicion_nave.y = 0
        for ast in asteroides:
            ast["pos"] += ast["vel"]
            if ast["pos"].x < -50: ast["pos"].x = ancho + 50
            if ast["pos"].x > ancho + 50: ast["pos"].x = -50
            if ast["pos"].y < -50: ast["pos"].y = alto + 50
            if ast["pos"].y > alto + 50: ast["pos"].y = -50
        for d in disparos[:]:
            d["pos"] += d["vel"]
            if not (0 <= d["pos"].x <= ancho and 0 <= d["pos"].y <= alto):
                disparos.remove(d)
        for ast in asteroides[:]:
            if posicion_nave.distance_to(ast["pos"]) < ast["radio"] + 18:
                estado = "game_over"
                break
        for d in disparos[:]:
            for ast in asteroides[:]:
                if d["pos"].distance_to(ast["pos"]) < ast["radio"]:
                    if d in disparos: disparos.remove(d)
                    if ast in asteroides: asteroides.remove(ast)
                    puntuacion += PUNTOS_POR_RADIO.get(ast["radio"], 10)
                    crear_asteroide()
                    break
        # Para subir de nivel: cumplir las horas Y los puntos del nivel actual
        req = REQUISITOS_NIVEL.get(nivel)
        if req and puntuacion >= req["puntos"] and horas_pasadas >= req["horas"]:
            siguiente_nivel()

    if estado not in ("nombre", "game_over", "ganaste", "sin_niveles"):
        for p in particulas:
            if estado == "despegando": p["pos"] += p["vel"]
            p["radio"] -= 0.1
        particulas[:] = [p for p in particulas if p["radio"] > 0]

    pantalla.fill((8, 8, 16))
    for x_e, y_e, t_e in estrellas:
        pygame.draw.circle(pantalla, (255, 255, 255), (x_e, y_e), t_e)

    if estado == "nombre":
        titulo = fuente_grande.render("ASTEROIDS", True, (0, 255, 255))
        pantalla.blit(titulo, titulo.get_rect(center=(ancho // 2, 110)))
        pide = fuente_media.render("Nombre del piloto:", True, (0, 255, 102))
        pantalla.blit(pide, pide.get_rect(center=(ancho // 2, 200)))
        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        caja = fuente_media.render(nombre_piloto + cursor, True, (255, 255, 255))
        pygame.draw.rect(pantalla, (0, 255, 102), (ancho // 2 - 120, 240, 240, 40), 2)
        pantalla.blit(caja, caja.get_rect(center=(ancho // 2, 260)))
        ayuda = fuente_hud.render("ENTER para empezar", True, (150, 150, 150))
        pantalla.blit(ayuda, ayuda.get_rect(center=(ancho // 2, 310)))
    else:
        if estado == "despegando":
            planeta_actual(nivel).dibujar(pantalla)
            if nivel == 1:
                frase_nivel = "de la tierra a la luna nivel 1"
            elif nivel == 2:
                frase_nivel = "de la luna a marte nivel 2"
            else:
                frase_nivel = ""
            if frase_nivel:
                txt_nivel = fuente_media.render(frase_nivel, True, (0, 255, 255))
                pantalla.blit(txt_nivel, txt_nivel.get_rect(center=(ancho // 2, 60)))
        for p in particulas:
            pygame.draw.circle(pantalla, p["color"], (int(p["pos"].x), int(p["pos"].y)), int(p["radio"]))
        for d in disparos:
            pygame.draw.circle(pantalla, (0, 255, 255), (int(d["pos"].x), int(d["pos"].y)), 3)
        for ast in asteroides:
            rect = ast["img"].get_rect(center=(int(ast["pos"].x), int(ast["pos"].y)))
            pantalla.blit(ast["img"], rect.topleft)
        if estado in ("despegando", "jugando", "game_over"):
            rot = pygame.transform.rotate(img_halcon, nave_angulo)
            rect_n = rot.get_rect(center=(int(posicion_nave.x), int(posicion_nave.y)))
            pantalla.blit(rot, rect_n.topleft)

        # --- HUD SOLO CON: PILOTO + NOMBRE, PUNTOS Y HORAS ---
        hud = fuente_hud.render(f"PILOTO: {nombre_piloto} | PUNTOS: {puntuacion}", True, (0, 255, 102))
        pantalla.blit(hud, (20, 20))
        color_t = (255, 80, 80) if segundos_restantes < 43200 else (255, 204, 0)
        hud_t = fuente_reloj.render(f"HORAS: {tiempo_str}", True, color_t)
        pantalla.blit(hud_t, (20, 44))

        if estado == "game_over":
            capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            capa.fill((0, 0, 0, 170))
            pantalla.blit(capa, (0, 0))
            go = fuente_grande.render("GAME OVER", True, (255, 60, 60))
            pantalla.blit(go, go.get_rect(center=(ancho // 2, 230)))
            sc = fuente_media.render(f"{nombre_piloto}, puntaje:{puntuacion}", True, (255, 255, 255))
            pantalla.blit(sc, sc.get_rect(center=(ancho // 2, 300)))
            op = fuente_media.render("Pulsa R para reiniciar", True, (0, 255, 102))
            pantalla.blit(op, op.get_rect(center=(ancho // 2, 360)))

        if estado == "ganaste":
            capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            capa.fill((0, 0, 0, 170))
            pantalla.blit(capa, (0, 0))
            win = fuente_grande.render("\u00a1GANASTE!", True, (0, 255, 255))
            pantalla.blit(win, win.get_rect(center=(ancho // 2, 230)))
            op = fuente_media.render("Pulsa R", True, (0, 255, 102))
            pantalla.blit(op, op.get_rect(center=(ancho // 2, 360)))

        if estado == "sin_niveles":
            capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            capa.fill((0, 0, 0, 190))
            pantalla.blit(capa, (0, 0))
            msg1 = fuente_grande.render("YA NO HAY NIVELES", True, (0, 255, 255))
            pantalla.blit(msg1, msg1.get_rect(center=(ancho // 2, 220)))
            msg2 = fuente_media.render(f"{nombre_piloto}, llegaste al nivel 3", True, (255, 255, 255))
            pantalla.blit(msg2, msg2.get_rect(center=(ancho // 2, 295)))
            msg3 = fuente_media.render("Juego detenido - Pulsa R para reiniciar", True, (0, 255, 102))
            pantalla.blit(msg3, msg3.get_rect(center=(ancho // 2, 360)))

    pygame.display.flip()

pygame.quit()
