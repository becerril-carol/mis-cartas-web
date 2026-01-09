import os
import random
from functools import wraps
from flask import Flask, render_template, request, make_response, redirect, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Usamos una nueva base de datos para los nuevos campos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///registro_reconocimientos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
                'Acceso denegado. Use las credenciales correctas.', 
                401, 
                {'WWW-Authenticate': 'Basic realm="Login Requerido"'}
            )
        return f(*args, **kwargs)
    return decorated

# --- MODELO DE DATOS ---
class Reconocimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    puesto = db.Column(db.String(100), nullable=False)
    motivo = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    frase = db.Column(db.Text, nullable=False)
    estilo = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

def obtener_frase_aleatoria():
    if os.path.exists('frases.txt'):
        with open('frases.txt', 'r', encoding='utf-8') as f:
            frases = [line.strip() for line in f.readlines() if line.strip()]
        if frases:
            return random.choice(frases)
    return "¡Gracias por tu invaluable contribución al equipo!"

# --- RUTAS ---

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/nueva_frase')
def nueva_frase():
    return obtener_frase_aleatoria()

@app.route('/generar', methods=['POST'])
def generar():
    # Recolectamos la frase del formulario (la que el usuario eligió con el botón refrescar)
    # Si por algo llega vacía, generamos una nueva
    frase_elegida = request.form.get('frase') or obtener_frase_aleatoria()
    
    datos = {
        'nombre': request.form.get('nombre'),
        'puesto': request.form.get('puesto'),
        'motivo': request.form.get('motivo'),
        'fecha': request.form.get('fecha'),
        'estilo': request.form.get('estilo'),
        'fondo': request.form.get('color_fondo'),
        'texto': request.form.get('color_texto'),
        'frase': frase_elegida,
        'empresa': "CORPORATIVO TESCo." 
    }
    
    nuevo_registro = Reconocimiento(
        nombre=datos['nombre'],
        puesto=datos['puesto'],
        motivo=datos['motivo'],
        fecha=datos['fecha'],
        frase=datos['frase'],
        estilo=datos['estilo']
    )
    db.session.add(nuevo_registro)
    db.session.commit()
    
    return render_template('carta_pdf.html', **datos)

@app.route('/admin')
@requiere_login
def admin():
    registros = Reconocimiento.query.all()
    total = Reconocimiento.query.count()
    return render_template('admin.html', registros=registros, total=total)

@app.route('/eliminar/<int:id>')
@requiere_login
def eliminar(id):
    registro_a_borrar = Reconocimiento.query.get_or_404(id)
    db.session.delete(registro_a_borrar)
    db.session.commit()
    return redirect('/admin')

@app.route('/ver_carta/<int:id>')
@requiere_login
def ver_carta(id):
    registro = Reconocimiento.query.get_or_404(id)
    datos = {
        'nombre': registro.nombre,
        'puesto': registro.puesto,
        'motivo': registro.motivo,
        'fecha': registro.fecha,
        'frase': registro.frase,
        'estilo': registro.estilo,
        'fondo': '#ffffff', 
        'texto': '#1a2a6c',
        'empresa': "CORPORATIVO TESCo."
    }
    return render_template('carta_pdf.html', **datos)

if __name__ == '__main__':
    app.run(debug=True)