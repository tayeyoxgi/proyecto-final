import tkinter as tk
import random
import math

# --- 1. CONFIGURACIÓN DE VARIABLES GLOBALES ---
asteroides = []
ancho_pantalla = 800
alto_pantalla = 600
nombre_piloto = "Piloto Alfa"
puntuacion = 0

# Guardaremos los IDs del texto para poder moverlos al frente siempre
id_marcador_sombra = None
id_marcador_texto = None

# --- 2. FUNCIÓN PARA CREAR UN ASTEROIDE CON ESTILO ---
def crear_asteroide():
    global asteroides, canvas
    
    x = random.choice([random.randint(0, 200), random.randint(600, ancho_pantalla)])
    y = random.choice([random.randint(0, 150), random.randint(450, alto_pantalla)])
    
    radio = random.choice([15, 30, 50])
    
    id_canvas = canvas.create_oval(
        x - radio, y - radio, 
        x + radio, y + radio, 
        fill="#222226",      
        outline="#A0A0A5",   
        width=2              
    )
    
    angulo_azar = math.radians(random.randint(0, 360))
    velocidad_base = random.uniform(0.8, 2.5)
    
    vx = math.sin(angulo_azar) * velocidad_base
    vy = -math.cos(angulo_azar) * velocidad_base
        
    asteroides.append({
        "id": id_canvas,
        "x": x, "y": y,
        "vx": vx, "vy": vy,
        "radio": radio
    })

# --- 3. CREAR UN FONDO DE ESTRELLAS ALEATORIAS ---
def generar_estrellas():
    global canvas
    for _ in range(60):  
        ex = random.randint(0, ancho_pantalla)
        ey = random.randint(0, alto_pantalla)
        tamano = random.choice([1, 2]) 
        
        color_estrella = random.choice(["#FFFFFF", "#E0E0FF", "#FFFFD0"])
        canvas.create_oval(ex, ey, ex + tamano, ey + tamano, fill=color_estrella, outline="")

# --- 4. FUNCIÓN DE MOVIMIENTO CONTINUO ---
def actualizar_juego():
    global asteroides, canvas, ventana, id_marcador_sombra, id_marcador_texto
    
    for ast in asteroides:
        ast["x"] += ast["vx"]
        ast["y"] += ast["vy"]
        
        # Pantalla infinita
        if ast["x"] < -50: ast["x"] = ancho_pantalla + 50
        elif ast["x"] > ancho_pantalla + 50: ast["x"] = -50
        
        if ast["y"] < -50: ast["y"] = alto_pantalla + 50
        elif ast["y"] > alto_pantalla + 50: ast["y"] = -50
            
        canvas.coords(
            ast["id"], 
            ast["x"] - ast["radio"], 
            ast["y"] - ast["radio"], 
            ast["x"] + ast["radio"], 
            ast["y"] + ast["radio"]
        )
    
    # SOLUCIÓN CLAVE: Forzamos a que los dos textos del marcador se traigan al frente
    # en cada fotograma del juego, quedando siempre encima de los asteroides.
    if id_marcador_sombra and id_marcador_texto:
        canvas.tag_raise(id_marcador_sombra)
        canvas.tag_raise(id_marcador_texto)
    
    ventana.after(30, actualizar_juego)

# --- 5. CONFIGURACIÓN DE LA INTERFAZ GRÁFICA ---
ventana = tk.Tk()
ventana.title("Asteroids Space Simulator")
ventana.resizable(False, False)

canvas = tk.Canvas(ventana, width=ancho_pantalla, height=alto_pantalla, bg="#080810", highlightthickness=0)
canvas.pack()

# Generamos las estrellas de fondo
generar_estrellas()

# Creamos el marcador superior estilo Arcade y guardamos sus referencias
id_marcador_sombra = canvas.create_text(152, 27, text=f"PILOTO: {nombre_piloto}   |   SCORE: {puntuacion}", fill="#000000", font=("Courier New", 12, "bold"))
id_marcador_texto = canvas.create_text(150, 25, text=f"PILOTO: {nombre_piloto}   |   SCORE: {puntuacion}", fill="#00FF66", font=("Courier New", 12, "bold"))

# Crear los asteroides estilizados
for i in range(8):
    crear_asteroide()

# Iniciar físicas
actualizar_juego()

ventana.mainloop()
