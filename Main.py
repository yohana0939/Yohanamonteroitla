from flask import Flask, render_template, request
import json# Lista de diccionarios con datos de ejemplo
productos = [
    {"titulo": "Reloj Casio F91W", "precio": 1800, "detalle": "Reloj digital clásico, resistente y ligero"},
    {"titulo": "Reloj Casio G-Shock", "precio": 7500, "detalle": "Reloj deportivo resistente a golpes y agua"},
    {"titulo": "Perfume Bleu de Chanel", "precio": 6500, "detalle": "Fragancia masculina elegante y duradera"},
    {"titulo": "Perfume Versace Eros", "precio": 5800, "detalle": "Perfume masculino con aroma fuerte y fresco"},
    {"titulo": "Perfume Good Girl", "precio": 6200, "detalle": "Perfume femenino con aroma dulce y sofisticado"},
    {"titulo": "Aire acondicionado 12000 BTU", "precio": 32000, "detalle": "Aire acondicionado inverter ideal para habitaciones"},
    {"titulo": "Aire acondicionado 18000 BTU", "precio": 42000, "detalle": "Aire acondicionado potente para espacios medianos"},
    {"titulo": "Aire acondicionado portátil", "precio": 28000, "detalle": "Aire acondicionado fácil de mover entre habitaciones"},
    {"titulo": "Ventilador de pedestal", "precio": 3500, "detalle": "Ventilador con altura ajustable y 3 velocidades"},
    {"titulo": "Reloj Casio Edifice", "precio": 9800, "detalle": "Reloj elegante para uso formal"},
    {"titulo": "Perfume Dior Sauvage", "precio": 7200, "detalle": "Fragancia masculina intensa y moderna"},
    {"titulo": "Reloj Casio Vintage", "precio": 2500, "detalle": "Reloj estilo retro muy popular"},
    {"titulo": "Difusor de aroma", "precio": 1500, "detalle": "Dispositivo para aromatizar espacios"},
    {"titulo": "Mini aire acondicionado USB", "precio": 4500, "detalle": "Aire pequeño ideal para escritorio"},
    {"titulo": "Set de perfumes mini", "precio": 3000, "detalle": "Colección de fragancias en tamaño pequeño"}
]
personas = [
    {"id": 1, "nombre": "Yohana", "hobby": "Leer"},
    {"id": 2, "nombre": "Carlos", "hobby": "Jugar fútbol"},
    {"id": 3, "nombre": "Ana", "hobby": "Escuchar música"},
    {"id": 4, "nombre": "Luis", "hobby": "Cocinar"},
    {"id": 5, "nombre": "María", "hobby": "Bailar"}
    
] 
def buscar_personas(id ):
    for persona in personas:
        if persona["id"] == int(id) :
         return json.dumps(persona) 
    

app = Flask(__name__)
@app.route("/persona")
def persona():
    id = request.args.get('id') 
    return buscar_personas(id) 
   

@app.route("/")
def home():
    return render_template("index.html" , productos=productos) 

@app.route("/acerca")
def acerca():
    return render_template("acerca.html")


@app.route("/tienda")
def tienda():
    return render_template("Product.html", productos=productos)

if __name__ == "__main__":
    app.run(debug=True)



