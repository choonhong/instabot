from flask import Flask, request, render_template, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from main import InstagramPostGenerator
import logging
import json
from gpt4all import GPT4All
import io
from PIL import Image

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize GPT4All
try:
    model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
    logger.info("GPT4All model loaded successfully")
except Exception as e:
    logger.error(f"Error loading GPT4All model: {str(e)}")
    model = None

# Ensure output directory exists
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
    try:
        logger.debug("Upload request received")
        logger.debug(f"Files in request: {request.files}")
        
        # Log the total size of the upload
        total_size = 0
        for file in request.files.getlist('photos'):
            if file and file.filename:
                file.seek(0, 2)  # Seek to end of file
                size = file.tell()  # Get current position (file size)
                total_size += size
                file.seek(0)  # Reset file pointer
                logger.debug(f"File {file.filename} size: {size / 1024 / 1024:.2f} MB")
        
        logger.debug(f"Total upload size: {total_size / 1024 / 1024:.2f} MB")
        
        if 'photos' not in request.files:
            logger.error("No 'photos' in request.files")
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('photos')
        location = request.form.get('location', '')
        
        logger.debug(f"Number of files: {len(files)}")
        logger.debug(f"Location: {location}")
        
        if not files:
            logger.error("No files in request.files['photos']")
            return jsonify({'error': 'No files selected'}), 400
        
        # Process files in memory
        processed_files = []
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                # Read the file into memory
                file_data = file.read()
                # Create a BytesIO object
                file_buffer = io.BytesIO(file_data)
                # Open the image using PIL
                img = Image.open(file_buffer)
                # Save to output folder with a unique name
                output_filename = secure_filename(file.filename)
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                img.save(output_path)
                processed_files.append(output_path)
                logger.debug(f"Processed file: {output_path}")
        
        if not processed_files:
            logger.error("No valid files were processed")
            return jsonify({'error': 'No valid files uploaded'}), 400
        
        # Generate Instagram post
        generator = InstagramPostGenerator(
            app.config['OUTPUT_FOLDER'],
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
        
        logger.debug(f"Successfully processed {len(formatted_images)} images")
        return jsonify({
            'success': True,
            'message': 'Post generated successfully',
            'images': formatted_images,
            'caption': caption
        })
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/generate_caption', methods=['POST'])
def generate_caption():
    try:
        logger.debug("Generate caption request received")
        logger.debug(f"Files in request: {request.files}")
        
        # Log the total size of the upload
        total_size = 0
        for file in request.files.getlist('photos'):
            if file and file.filename:
                file.seek(0, 2)  # Seek to end of file
                size = file.tell()  # Get current position (file size)
                total_size += size
                file.seek(0)  # Reset file pointer
                logger.debug(f"File {file.filename} size: {size / 1024 / 1024:.2f} MB")
        
        logger.debug(f"Total upload size: {total_size / 1024 / 1024:.2f} MB")
        
        if 'photos' not in request.files:
            logger.error("No 'photos' in request.files")
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('photos')
        location = request.form.get('location', '')
        
        logger.debug(f"Number of files: {len(files)}")
        logger.debug(f"Location: {location}")
        
        if not files:
            logger.error("No files in request.files['photos']")
            return jsonify({'error': 'No files selected'}), 400
        
        # Process files in memory
        processed_files = []
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                # Read the file into memory
                file_data = file.read()
                # Create a BytesIO object
                file_buffer = io.BytesIO(file_data)
                # Open the image using PIL
                img = Image.open(file_buffer)
                # Save to output folder with a unique name
                output_filename = secure_filename(file.filename)
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                img.save(output_path)
                processed_files.append(output_path)
                logger.debug(f"Processed file: {output_path}")
        
        if not processed_files:
            logger.error("No valid files were processed")
            return jsonify({'error': 'No valid files uploaded'}), 400
        
        # Generate Instagram post
        generator = InstagramPostGenerator(
            app.config['OUTPUT_FOLDER'],
            app.config['OUTPUT_FOLDER'],
            location
        )
        generator.generate_post()
        
        # Get the caption
        caption_path = os.path.join(app.config['OUTPUT_FOLDER'], 'caption.txt')
        
        # Check if the caption file exists
        if not os.path.exists(caption_path):
            logger.warning(f"Caption file not found at {caption_path}, creating a default caption")
            # Create a default caption if the file doesn't exist
            default_caption = f"Beautiful moments captured in {location if location else 'this amazing place'}! #travel #wanderlust #adventure"
            with open(caption_path, 'w', encoding='utf-8') as f:
                f.write(default_caption)
            logger.debug(f"Created default caption file at {caption_path}")
        
        # Now read the caption file
        with open(caption_path, 'r', encoding='utf-8') as f:
            caption = f.read()
        
        logger.debug("Caption generated successfully")
        return jsonify({
            'success': True,
            'message': 'Caption generated successfully',
            'caption': caption
        })
        
    except Exception as e:
        logger.error(f"Error generating caption: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/chat_with_ai', methods=['POST'])
def chat_with_ai():
    try:
        data = request.json
        message = data.get('message', '')
        current_caption = data.get('currentCaption', '')
        
        logger.debug(f"Chat request received: {message}")
        logger.debug(f"Current caption: {current_caption}")
        
        # Check if model is available
        if not model:
            logger.error("GPT4All model not loaded")
            return jsonify({
                'success': False,
                'error': 'AI model not loaded. Please check the logs for details.',
                'caption': current_caption,
                'response': "I'm sorry, but I can't process your request right now. The AI service is not configured."
            })
        
        try:
            # Prepare the prompt
            system_prompt = """
            You are an expert Instagram caption writer. Your task is to modify the provided caption based on the user's request.
            The caption should be engaging, authentic, and appropriate for Instagram.
            Return your response in JSON format with two fields:
            1. "caption": The modified caption text
            2. "explanation": A brief explanation of what you changed and why
            
            Keep the original caption's core message but modify it according to the user's request.
            """
            
            user_prompt = f"""
            Current caption: {current_caption}
            
            User request: {message}
            
            Please modify the caption based on the user's request.
            """
            
            logger.debug(f"Sending request to GPT4All")
            
            # Generate response using GPT4All
            response = model.generate(
                prompt=f"{system_prompt}\n\n{user_prompt}",
                max_tokens=500,
                temp=0.7,
                top_k=40,
                top_p=0.9,
                repeat_penalty=1.1
            )
            
            logger.debug(f"GPT4All response: {response}")
            
            # Parse the JSON response
            try:
                response_data = json.loads(response)
                updated_caption = response_data.get("caption", current_caption)
                explanation = response_data.get("explanation", "I've updated your caption based on your request.")
            except json.JSONDecodeError:
                # If the response is not valid JSON, use it as the caption
                logger.warning(f"Failed to parse GPT4All response as JSON: {response}")
                updated_caption = response
                explanation = "I've updated your caption based on your request."
            
            logger.debug(f"Updated caption: {updated_caption}")
            
            return jsonify({
                'success': True,
                'response': explanation,
                'caption': updated_caption
            })
            
        except Exception as e:
            logger.error(f"Error calling GPT4All: {str(e)}", exc_info=True)
            # Fall back to the rule-based approach if GPT4All fails
            return fallback_caption_modification(message, current_caption)
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def fallback_caption_modification(message, current_caption):
    """Fallback method for caption modification if GPT4All fails"""
    logger.info("Using fallback caption modification")
    
    # Analyze the user's request
    if "hashtag" in message.lower() or "#" in message:
        # User wants to add hashtags
        hashtags = "#travel #wanderlust #adventure #explore #travelgram #instatravel #travelphotography #traveltheworld #travelblogger"
        updated_caption = current_caption + "\n\n" + hashtags
        response = "I've added some popular travel hashtags to your caption. These will help increase visibility for your post."
    
    elif "shorter" in message.lower() or "concise" in message.lower():
        # User wants a shorter caption
        # Split the caption into lines and take the first few
        lines = current_caption.split('\n')
        updated_caption = '\n'.join(lines[:2])  # Take first two lines
        response = "I've made your caption shorter and more concise. Sometimes less is more on Instagram!"
    
    elif "longer" in message.lower() or "more detail" in message.lower():
        # User wants a longer caption
        updated_caption = current_caption + "\n\nThis place has so much to offer - from the stunning views to the local culture. Every moment here feels like a new adventure waiting to be discovered. The memories created here will last a lifetime."
        response = "I've expanded your caption with more details about the experience. This gives your followers a better sense of what made this moment special."
    
    elif "funny" in message.lower() or "humorous" in message.lower():
        # User wants a funny caption
        updated_caption = current_caption + "\n\nPOV: Trying to take the perfect Instagram photo but your friend photobombed you for the 10th time 😂 #TravelProblems"
        response = "I've added a humorous touch to your caption. A little humor can make your post more relatable and engaging!"
    
    elif "serious" in message.lower() or "professional" in message.lower():
        # User wants a serious caption
        updated_caption = current_caption + "\n\nReflecting on the profound impact this journey has had on my perspective. Sometimes the most meaningful experiences come from the simplest moments."
        response = "I've updated your caption with a more serious and reflective tone. This adds depth to your post and encourages thoughtful engagement."
    
    elif "inspirational" in message.lower() or "motivational" in message.lower():
        # User wants an inspirational caption
        updated_caption = current_caption + "\n\nRemember: The world is full of possibilities waiting to be explored. Every journey begins with a single step. Where will your next adventure take you?"
        response = "I've added an inspirational message to your caption. This can motivate your followers to explore and create their own adventures."
    
    elif "emoji" in message.lower():
        # User wants to add emojis
        updated_caption = current_caption.replace(".", " ✨").replace("!", " 🌟").replace("?", " 🤔")
        updated_caption = "🌟 " + updated_caption + " 🌎 ✈️ 📸"
        response = "I've added some emojis to make your caption more visually appealing and expressive. Emojis can help convey emotions that words alone might not capture."
    
    else:
        # Generic modification based on user input
        updated_caption = current_caption + f"\n\n{message}"
        response = f"I've incorporated your request into the caption. Is there anything specific you'd like me to change about it?"
    
    logger.debug(f"Fallback updated caption: {updated_caption}")
    
    return jsonify({
        'success': True,
        'response': response,
        'caption': updated_caption
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=True
    ) 