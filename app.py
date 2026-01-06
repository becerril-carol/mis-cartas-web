import os
import random
from functools import wraps
from flask import Flask, render_template, request, make_response, redirect, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///registro_cartas.db'
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
                'No pudiste entrar. Usa el usuario y contraseña correctos.', 
                401, 
                {'WWW-Authenticate': 'Basic realm="Login Requerido"'}
            )
        return f(*args, **kwargs)
    return decorated
# ----------------------------------

class Carta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    fecha = db.Column(db.String(20))
    frase = db.Column(db.String(500))

with app.app_context():
    db.create_all()

def obtener_frase_aleatoria():
    if os.path.exists('frases.txt'):
        with open('frases.txt', 'r', encoding='utf-8') as f:
            frases = f.readlines()
        return random.choice(frases).strip()
    return "¡Eres una persona increíble!"

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    datos = {
        'nombre': request.form.get('nombre'),
        'fecha': request.form.get('fecha'),
        'fondo': request.form.get('color_fondo'),
        'texto': request.form.get('color_texto'),
        'frase': obtener_frase_aleatoria()
    }
    nueva_carta = Carta(nombre=datos['nombre'], fecha=datos['fecha'], frase=datos['frase'])
    db.session.add(nueva_carta)
    db.session.commit()
    return render_template('carta_pdf.html', **datos)

@app.route('/admin')
@requiere_login
def admin():
    cartas = Carta.query.all()
    return render_template('admin.html', cartas=cartas)

@app.route('/ver/<int:id>')
def ver_carta(id):
    carta = Carta.query.get_or_404(id)
    datos = {
        'nombre': carta.nombre,
        'fecha': carta.fecha,
        'frase': carta.frase,
        'fondo': '#ffffff',
        'texto': '#333333'
    }
    return render_template('carta_pdf.html', **datos)

@app.route('/eliminar/<int:id>')
@requiere_login
def eliminar(id):
    carta_a_eliminar = Carta.query.get_or_404(id)
    db.session.delete(carta_a_eliminar)
    db.session.commit()
    return redirect('/admin')
    
if __name__ == '__main__':
    app.run(debug=True)