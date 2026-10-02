import tkinter as tk
import random
import math

# --- 1. CONFIGURACIÓN DE VARIABLES GLOBALES ---
ancho_pantalla = 800
alto_pantalla = 600
nombre_piloto = "Piloto Alfa"
puntuacion = 0

id_marcador_sombra = None
id_marcador_texto = None

# Variables de partículas y disparos
particulas = []
disparos = [] # Lista para almacenar los proyectiles activos

# Variables de la nave y animación
estado = "despegando"  
nave_x = 400
nave_y = 590  
nave_angulo = 0  
nave_velocidad_x = 0
nave_velocidad_y = 0

id_nave = None
id_planeta = None

# --- 2. FUNCIÓN PARA CREAR LA NAVE Y EL PLANETA ---
def inicializar_nave_y_planeta():
    global canvas, id_nave, id_planeta
    
    # Superficie del planeta en la parte inferior
    id_planeta = canvas.create_oval(-200, 550, 1000, 900, fill="#331155", outline="#552288", width=3)
    
    # Polígono para la nave espacial (triángulo futurista cian)
    id_nave = canvas.create_polygon(0, 0, 0, 0, 0, 0, fill="#111116", outline="#00FFFF", width=2)
    
    actualizar_grafico_nave()

def actualizar_grafico_nave():
    global canvas, id_nave, nave_x, nave_y, nave_angulo
    rad = math.radians(nave_angulo)
    
    # Calcular los tres vértices del triángulo de la nave
    p1_x = nave_x + math.sin(rad) * 15
    p1_y = nave_y - math.cos(rad) * 15
    
    p2_x = nave_x + math.sin(rad + 2.5) * 12
    p2_y = nave_y - math.cos(rad + 2.5) * 12
    
    p3_x = nave_x + math.sin(rad - 2.5) * 12
    p3_y = nave_y - math.cos(rad - 2.5) * 12
    
    canvas.coords(id_nave, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y)

# --- 3. SISTEMA DE PARTICULAS DEL MOTOR ---
def crear_particula(x, y, angulo):
    global particulas, canvas
    # El fuego sale en dirección opuesta a donde mira la nave
    angulo_escape = math.radians(angulo + 180) + random.uniform(-0.3, 0.3)
    velocidad = random.uniform(2, 5)
    
    vx = math.sin(angulo_escape) * velocidad
    vy = -math.cos(angulo_escape) * velocidad
    radio = random.randint(3, 6)
    color = random.choice(["#FF3300", "#FF6600", "#FFCC00", "#FFFF00"]) # Rojo, naranja y amarillo
    
    id_p = canvas.create_oval(x - radio, y - radio, x + radio, y + radio, fill=color, outline="")
    
    particulas.append({
        "id": id_p, "x": x, "y": y, "vx": vx, "vy": vy, "radio": radio
    })

def actualizar_particulas():
    global particulas, canvas
    particulas_vivas = []
    
    for p in particulas:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["radio"] -= 0.25 # Se van haciendo más pequeñas en cada fotograma
        
        if p["radio"] > 0:
            canvas.coords(p["id"], p["x"] - p["radio"], p["y"] - p["radio"], p["x"] + p["radio"], p["y"] + p["radio"])
            particulas_vivas.append(p)
        else:
            canvas.delete(p["id"]) # Elimina de la interfaz cuando el radio llega a 0
            
    particulas = particulas_vivas

# --- 4. CONTROLES DEL TECLADO ---
def presionar_izquierda(event):
    global nave_angulo, estado
    if estado != "jugando": return  
    nave_angulo = (nave_angulo - 15) % 360

def presionar_derecha(event):
    global nave_angulo, estado
    if estado != "jugando": return  
    nave_angulo = (nave_angulo + 15) % 360

def presionar_arriba(event):
    global nave_velocidad_x, nave_velocidad_y, nave_angulo, estado, nave_x, nave_y
    if estado != "jugando": return  
    rad = math.radians(nave_angulo)
    nave_velocidad_x += math.sin(rad) * 0.6
    nave_velocidad_y -= math.cos(rad) * 0.6
    
    # Genera partículas al acelerar manualmente
    crear_particula(nave_x, nave_y, nave_angulo)

def presionar_abajo(event):
    global nave_velocidad_x, nave_velocidad_y, nave_angulo, estado
    if estado != "jugando": return  
    rad = math.radians(nave_angulo)
    nave_velocidad_x -= math.sin(rad) * 0.4
    nave_velocidad_y += math.cos(rad) * 0.4

def presionar_espacio(event):
    global disparos, canvas, nave_x, nave_y, nave_angulo, estado
    if estado != "jugando": return  
    
    # El disparo nace en la punta/centro de la nave y va hacia donde apunta el ángulo
    rad = math.radians(nave_angulo)
    velocidad_disparo = 10
    
    vx = math.sin(rad) * velocidad_disparo
    vy = -math.cos(rad) * velocidad_disparo
    radio = 3
    
    # Dibujar proyectil pequeño de color cian brillante
    id_d = canvas.create_oval(nave_x - radio, nave_y - radio, nave_x + radio, nave_y + radio, fill="#00FFFF", outline="")
    
    disparos.append({
        "id": id_d, "x": nave_x, "y": nave_y, "vx": vx, "vy": vy
    })

# --- 5. GESTIÓN DE PROYECTILES ---
def actualizar_disparos():
    global disparos, canvas
    disparos_vivos = []
    
    for d in disparos:
        d["x"] += d["vx"]
        d["y"] += d["vy"]
        
        # Comprobar si el disparo sigue dentro de la pantalla
        if 0 <= d["x"] <= ancho_pantalla and 0 <= d["y"] <= alto_pantalla:
            canvas.coords(d["id"], d["x"] - 3, d["y"] - 3, d["x"] + 3, d["y"] + 3)
            disparos_vivos.append(d)
        else:
            canvas.delete(d["id"]) # Borrar del canvas si sale del mapa
            
    disparos = disparos_vivos

# --- 6. GENERACIÓN DE ESTRELLAS ---
def generar_estrellas():
    global canvas
    for _ in range(60):  
        ex = random.randint(0, ancho_pantalla)
        ey = random.randint(0, alto_pantalla)
        tamano = random.choice([1, 2]) 
        color_estrella = random.choice(["#FFFFFF", "#E0E0FF", "#FFFFD0"])
        canvas.create_oval(ex, ey, ex + tamano, ey + tamano, fill=color_estrella, outline="")

# --- 7. BUCLE PRINCIPAL DE JUEGO ---
def actualizar_juego():
    global canvas, ventana, id_marcador_sombra, id_marcador_texto
    global estado, nave_x, nave_y, nave_velocidad_x, nave_velocidad_y, id_planeta, id_nave
    
    # Animación de despegue automático
    if estado == "despegando":
        nave_y -= 3  
        actualizar_grafico_nave()
        canvas.move(id_planeta, 0, 1.5)
        
        # Generar ráfagas de partículas constantes durante el despegue hacia abajo
        crear_particula(nave_x, nave_y, nave_angulo)
        crear_particula(nave_x, nave_y, nave_angulo)
        
        if nave_y <= 300:
            estado = "jugando"
            canvas.delete(id_planeta)  
            
    elif estado == "jugando":
        nave_velocidad_x *= 0.98
        nave_velocidad_y *= 0.98
        nave_x += nave_velocidad_x
        nave_y += nave_velocidad_y
        
        # Límites de pantalla (Efecto espejo)
        if nave_x < 0: nave_x = ancho_pantalla
        elif nave_x > ancho_pantalla: nave_x = 0
        if nave_y < 0: nave_y = alto_pantalla
        elif nave_y > alto_pantalla: nave_y = 0
            
        actualizar_grafico_nave()

    # Actualizar la física visual de todas las partículas y disparos
    actualizar_particulas()
    actualizar_disparos()
    
    # Control de capas (Traer nave, disparos y textos al frente)
    if id_marcador_sombra and id_marcador_texto:
        canvas.tag_raise(id_marcador_sombra)
        canvas.tag_raise(id_marcador_texto)
    
    for d in disparos:
        canvas.tag_raise(d["id"])
        
    if id_nave:
        canvas.tag_raise(id_nave) 
        
    ventana.after(30, actualizar_juego)

# --- 8. CONFIGURACIÓN DE LA INTERFAZ ---
ventana = tk.Tk()
ventana.title("Asteroids Space Simulator")
ventana.resizable(False, False)

canvas = tk.Canvas(ventana, width=ancho_pantalla, height=alto_pantalla, bg="#080810", highlightthickness=0)
canvas.pack()

# Capturar teclado
ventana.bind("<Left>", presionar_izquierda)
ventana.bind("<Right>", presionar_derecha)
ventana.bind("<Up>", presionar_arriba)
ventana.bind("<Down>", presionar_abajo)
ventana.bind("<space>", presionar_espacio) # Captura de la barra espaciadora

generar_estrellas()
inicializar_nave_y_planeta()

id_marcador_sombra = canvas.create_text(152, 27, text=f"PILOTO: {nombre_piloto}   |   SCORE: {puntuacion}", fill="#000000", font=("Courier New", 12, "bold"))
id_marcador_texto = canvas.create_text(150, 25, text=f"PILOTO: {nombre_piloto}   |   SCORE: {puntuacion}", fill="#00FF66", font=("Courier New", 12, "bold"))

actualizar_juego()
ventana.mainloop()
