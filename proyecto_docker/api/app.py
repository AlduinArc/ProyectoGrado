# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from simplepam import authenticate
import os
import subprocess
import logging

app = Flask(__name__, template_folder='templates')
app.secret_key = 'Dasherfkrslf321#'  # Considera usar una clave más segura en produccion


# Configuracion
USERS_DIR = "/home"  # Asegurate que esta ruta sea correcta para tu docker
PAM_SERVICE = "system-auth"

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return redirect('/landing/index.html')

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "API is running!"})

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        # Crear usuario en el sistema del contenedor
        subprocess.run(['useradd', '-m', username], check=True)
        
        # Establecer la contraseña
        subprocess.run(
            ['bash', '-c', f'echo "{username}:{password}" | chpasswd'],
            check=True
        )

        # Crear directorio public_html
        public_dir = os.path.join(USERS_DIR, username, 'public_html')
        os.makedirs(public_dir, mode=0o755, exist_ok=True)

        return jsonify({"message": f"User {username} created successfully!"})
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({"error": "Failed to create user"}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            if authenticate(username, password, service=PAM_SERVICE):
                session['username'] = username
                return redirect(url_for('file_manager'))
            else:
                error = "Invalid Credentials"
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            error = "Error en el servidor durante autenticacion"
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/file_manager')
def file_manager():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    return render_template('manage.html', username=username)

@app.route('/create_file', methods=['POST'])
def create_file():
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.json
    filename = data.get('filename')
    content = data.get('content', '')
    
    if not filename:
        return jsonify({"error": "Nombre de archivo requerido"}), 400
    
    username = session['username']
    user_dir = os.path.join(USERS_DIR, username, 'public_html')
    filepath = os.path.join(user_dir, filename)
    
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error creating file: {str(e)}")
        return jsonify({"error": "Error al crear archivo"}), 500

@app.route('/get_file', methods=['POST'])
def get_file():
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({"error": "Nombre de archivo requerido"}), 400
    
    username = session['username']
    user_dir = os.path.join(USERS_DIR, username, 'public_html')
    filepath = os.path.join(user_dir, filename)
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return jsonify({"success": True, "content": content})
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return jsonify({"error": "Error al leer archivo"}), 500

@app.route('/save_file', methods=['POST'])
def save_file():
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.json
    filename = data.get('filename')
    content = data.get('content', '')
    
    if not filename:
        return jsonify({"error": "Nombre de archivo requerido"}), 400
    
    username = session['username']
    user_dir = os.path.join(USERS_DIR, username, 'public_html')
    filepath = os.path.join(user_dir, filename)
    
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return jsonify({"error": "Error al guardar archivo"}), 500

@app.route('/delete_file', methods=['POST'])
def delete_file():
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({"error": "Nombre de archivo requerido"}), 400
    
    username = session['username']
    user_dir = os.path.join(USERS_DIR, username, 'public_html')
    filepath = os.path.join(user_dir, filename)
    
    try:
        os.remove(filepath)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return jsonify({"error": "Error al eliminar archivo"}), 500

@app.route('/list_files', methods=['GET'])
def list_files():
    if 'username' not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    username = session['username']
    user_dir = os.path.join(USERS_DIR, username, 'public_html')
    
    try:
        if not os.path.exists(user_dir):
            os.makedirs(user_dir, mode=0o755, exist_ok=True)
            return jsonify([])
        
        files = [
            f for f in os.listdir(user_dir)
            if os.path.isfile(os.path.join(user_dir, f)) and f.endswith('.txt')
        ]
        return jsonify(sorted(files))  # Orden alfabetico
    
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({"error": "Error al listar archivos"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)