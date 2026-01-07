import os
import random
from functools import wraps
from flask import Flask, render_template, request, make_response, redirect, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///registro_reconocimientos.db'
db = SQLAlchemy(app)

# --- CONFIGURACIÓN DE SEGURIDAD ---
USUARIO_ADMIN = "carol.becerril"
PASSWORD_ADMIN = "Carol222" 

def requiere_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not (auth.username == USUARIO_ADMIN and auth.password == PASSWORD_ADMIN):
            return Response(
                'Acceso denegado al panel administrativo.', 
                401, 
                {'WWW-Authenticate': 'Basic realm="Login Requerido"'}
            )
        return f(*args, **kwargs)
    return decorated

# --- MODELO DE DATOS ACTUALIZADO ---
class Reconocimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    puesto = db.Column(db.String(100))   # Nuevo
    motivo = db.Column(db.Text)          # Nuevo
    fecha = db.Column(db.String(20))
    frase = db.Column(db.String(500))
    estilo = db.Column(db.String(50))    # Nuevo (Moderno, Elegante, etc.)

with app.app_context():
    db.create_all()

def obtener_frase_aleatoria():
    if os.path.exists('frases.txt'):
        with open('frases.txt', 'r', encoding='utf-8') as f:
            frases = [line.strip() for line in f.readlines() if line.strip()]
        return random.choice(frases) if frases else "¡Gracias por tu esfuerzo diario!"
    return "¡Eres una pieza clave en nuestro equipo!"

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    # Captura de todos los nuevos datos
    datos = {
        'nombre': request.form.get('nombre'),
        'puesto': request.form.get('puesto'),
        'motivo': request.form.get('motivo'),
        'fecha': request.form.get('fecha'),
        'estilo': request.form.get('estilo'),
        'fondo': request.form.get('color_fondo'),
        'texto': request.form.get('color_texto'),
        'frase': obtener_frase_aleatoria(),
        'empresa': "Nombre de tu Empresa S.A." # Puedes cambiar esto
    }
    
    # Guardar en la nueva estructura de base de datos
    nuevo = Reconocimiento(
        nombre=datos['nombre'], 
        puesto=datos['puesto'],
        motivo=datos['motivo'],
        fecha=datos['fecha'], 
        frase=datos['frase'],
        estilo=datos['estilo']
    )
    db.session.add(nuevo)
    db.session.commit()
    
    return render_template('carta_pdf.html', **datos)

@app.route('/admin')
@requiere_login
def admin():
    registros = Reconocimiento.query.all()
    total = Reconocimiento.query.count() # Contador automático
    return render_template('admin.html', registros=registros, total=total)

@app.route('/eliminar/<int:id>')
@requiere_login
def eliminar(id):
    item = Reconocimiento.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect('/admin')
    
if __name__ == '__main__':
    app.run(debug=True)