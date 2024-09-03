from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# Directorios para las imágenes y descripciones
IMAGE_DIR = 'dataset'
DESCRIPTION_DIR = 'dataset'

# Crear el directorio de imágenes si no existe
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para obtener la lista de imágenes
@app.route('/images')
def get_images():
    images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return jsonify(images)

# Ruta para servir archivos de imagen
@app.route('/images/<filename>')
def send_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

# Ruta para guardar la descripción
@app.route('/save-description', methods=['POST'])
def save_description():
    data = request.json
    image_name = data.get('imageName')
    description = data.get('description')

    if not image_name or not description:
        return jsonify({'error': 'Falta el nombre de la imagen o la descripción'}), 400

    if not os.path.exists(DESCRIPTION_DIR):
        os.makedirs(DESCRIPTION_DIR)

    txt_file_name = os.path.splitext(image_name)[0] + '.txt'
    file_path = os.path.join(DESCRIPTION_DIR, txt_file_name)

    with open(file_path, 'w') as f:
        f.write(description)

    return jsonify({'message': 'Descripción guardada correctamente'})

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'images' not in request.files:
        return jsonify({'error': 'No se han enviado imágenes'}), 400
    
    images = request.files.getlist('images')
    
    if not images or all(image.filename == '' for image in images):
        return jsonify({'error': 'No se han seleccionado imágenes'}), 400
    
    saved_images = []

    # Obtener la lista de imágenes existentes y calcular el siguiente número
    existing_images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    existing_numbers = [int(os.path.splitext(img)[0]) for img in existing_images if os.path.splitext(img)[0].isdigit()]
    
    next_number = max(existing_numbers, default=0) + 1
    
    for image in images:
        if image and image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            extension = os.path.splitext(image.filename)[1]
            new_filename = f"{next_number}{extension}"
            
            # Guardar la imagen con el nuevo nombre
            image_path = os.path.join(IMAGE_DIR, new_filename)
            image.save(image_path)
            
            saved_images.append(new_filename)
            next_number += 1

    return jsonify({'message': 'Imágenes subidas correctamente', 'filenames': saved_images})



# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
