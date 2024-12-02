from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import cv2
import numpy as np
import base64

app = Flask(__name__)

BASE_IMAGE_PATH = 'static/images'

# Página principal (Proyecto 2: Predicciones)
@app.route('/')
def index():
    return render_template('index.html')

# Redirigir al Proyecto 1 (Imagen General)
@app.route('/general')
def general():
    ids = [d for d in os.listdir(BASE_IMAGE_PATH) if os.path.isdir(os.path.join(BASE_IMAGE_PATH, d))]
    return render_template('general.html', ids=ids)

# Ruta para información técnica
@app.route('/tecnico')
def tecnico():
    return render_template('tecnico.html')

# Ruta para información médica
@app.route('/resumen')
def resumen():
    return render_template('resumen.html')

# Reconstruir Imagen General (Proyecto 1)
@app.route('/reconstruct', methods=['POST'])
def reconstruct():
    data = request.json
    selected_id = data['id']
    apply_filter = data['filter']
    id_path = os.path.join(BASE_IMAGE_PATH, selected_id)

    patches = {}
    for file_name in os.listdir(id_path):
        if file_name.endswith('.png'):
            parts = file_name.split('_')
            if len(parts) >= 5 and 'x' in parts[2] and 'y' in parts[3]:
                x_coord = int(parts[2][1:])
                y_coord = int(parts[3][1:])
                img = cv2.imread(os.path.join(id_path, file_name), cv2.IMREAD_COLOR)

                if apply_filter:
                    label = int(parts[4][5])
                    if label == 1:
                        overlay = np.zeros_like(img)
                        overlay[:, :, 1] = 255
                        img = cv2.addWeighted(overlay, 0.5, img, 0.5, 0)
                patches[(x_coord, y_coord)] = img

    grid_data = []
    if patches:
        x_coords = [x for x, y in patches.keys()]
        y_coords = [y for x, y in patches.keys()]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)

        patch_size = 50
        for y in range(min_y, max_y + 1, patch_size):
            row = []
            for x in range(min_x, max_x + 1, patch_size):
                img = patches.get((x, y), np.zeros((patch_size, patch_size, 3), dtype=np.uint8))
                _, buffer = cv2.imencode('.png', img)
                img_data = base64.b64encode(buffer).decode('utf-8')
                row.append({'x': x, 'y': y, 'image': img_data})
            grid_data.append(row)

    return jsonify(grid_data=grid_data)

# Seleccionar Miniimagen para Predicciones
@app.route('/get_patch', methods=['POST'])
def get_patch():
    data = request.json
    selected_id = data['id']
    x = data['x']
    y = data['y']
    id_path = os.path.join(BASE_IMAGE_PATH, selected_id)

    for file_name in os.listdir(id_path):
        if file_name.endswith('.png'):
            parts = file_name.split('_')
            if f'x{x}' in file_name and f'y{y}' in file_name:
                img_path = os.path.join(id_path, file_name)
                img = cv2.imread(img_path, cv2.IMREAD_COLOR)
                _, buffer = cv2.imencode('.png', img)
                img_data = base64.b64encode(buffer).decode('utf-8')
                return jsonify({'image_data': img_data, 'file_name': file_name, 'redirect': url_for('index')})
    return jsonify({'error': 'No se encontró la miniimagen.'})

if __name__ == '__main__':  
    app.run(host="0.0.0.0", port=4000, debug=True)
