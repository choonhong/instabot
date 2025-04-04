from flask import Flask, request, render_template, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from main import InstagramPostGenerator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'photos' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('photos')
    location = request.form.get('location', '')
    
    if not files:
        return jsonify({'error': 'No files selected'}), 400
    
    # Clear previous uploads
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
    
    # Save uploaded files
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_files.append(filepath)
    
    if not saved_files:
        return jsonify({'error': 'No valid files uploaded'}), 400
    
    try:
        # Generate Instagram post
        generator = InstagramPostGenerator(
            app.config['UPLOAD_FOLDER'],
            app.config['OUTPUT_FOLDER'],
            location
        )
        generator.generate_post()
        
        # Get the results
        formatted_images = [f for f in os.listdir(app.config['OUTPUT_FOLDER']) 
                          if f.startswith('formatted_')]
        caption_path = os.path.join(app.config['OUTPUT_FOLDER'], 'caption.txt')
        
        with open(caption_path, 'r', encoding='utf-8') as f:
            caption = f.read()
        
        return jsonify({
            'success': True,
            'message': 'Post generated successfully',
            'images': formatted_images,
            'caption': caption
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 