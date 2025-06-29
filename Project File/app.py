import os
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import tensorflow as tf
import numpy as np
from PIL import Image
import io
from datetime import datetime # Import datetime for the dynamic year in footer
# IMPORTANT: Import preprocess_input from ResNet50 for consistent preprocessing
from tensorflow.keras.applications.resnet50 import preprocess_input

# Initialize the Flask application
app = Flask(__name__)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print(f"Uploads directory ensured at: {os.path.abspath(UPLOAD_FOLDER)}")

# Load the trained model
model = None # Initialize model to None
try:
    model_path = 'healthy_vs_rotten_best_model.h5'
    if os.path.exists(model_path):
        model = tf.keras.models.load_model(model_path)
        print(f"Model '{model_path}' loaded successfully.")
    else:
        print(f"Error: Model file '{model_path}' not found. Please ensure it's in the same directory as app.py.")
except Exception as e:
    print(f"Error loading model: {e}")
    # If model loading fails, the app will still run, but predictions will show an error.

# Define the image size expected by your model (consistent with training script)
IMG_HEIGHT = 224
IMG_WIDTH = 224

# Define the class names and their mapping to indices.
# This should match how your ImageDataGenerator ordered the classes during training.
# By default, flow_from_directory sorts alphabetically.
# If your dataset had 'healthy' and 'rotten' folders, it's likely:
# {'healthy': 0, 'rotten': 1}
# YOU MUST VERIFY THIS FROM THE OUTPUT OF YOUR TRAINING SCRIPT'S `train_generator.class_indices`
CLASS_NAMES = {0: 'Healthy', 1: 'Rotten'}
# If your training script showed {'rotten': 0, 'healthy': 1}, then change this to:
# CLASS_NAMES = {0: 'Rotten', 1: 'Healthy'}


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """
    Render the main page where users can upload an image.
    Pass the current year to the template for the footer.
    """
    return render_template('index.html', now={'year': datetime.now().year})

@app.route('/output', methods=['POST'])
def predict():
    """
    Handle image upload, preprocess, predict using the model, and display results.
    """
    if 'image' not in request.files:
        print("No 'image' file part in request.")
        # Pass now for footer on error page as well, though output.html doesn't use it directly in its current form
        return render_template('output.html', prediction_text="No file part", image_path=None, now={'year': datetime.now().year})

    file = request.files['image']

    if file.filename == '':
        print("No selected file.")
        return render_template('output.html', prediction_text="No selected file", image_path=None, now={'year': datetime.now().year})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            print(f"File saved successfully to: {filepath}")
        except Exception as e:
            print(f"Error saving file: {e}")
            return render_template('output.html', prediction_text=f"Error saving image file: {e}", image_path=None, now={'year': datetime.now().year})

        if model is None:
            print("Model is not loaded. Cannot make predictions.")
            return render_template('output.html', prediction_text="Error: Model could not be loaded. Check server logs.", image_path=None, now={'year': datetime.now().year})

        try:
            img = Image.open(filepath)
            
            # Ensure image is in RGB mode for consistent processing
            if img.mode != 'RGB':
                img = img.convert('RGB')

            img = img.resize((IMG_WIDTH, IMG_HEIGHT))
            img_array = np.array(img)
            
            # IMPORTANT: Apply ResNet50 specific preprocessing function
            # This must match the `preprocessing_function=preprocess_input` used during training
            img_array = preprocess_input(img_array)
            
            img_array = np.expand_dims(img_array, axis=0) # Add batch dimension

            # Make a prediction
            predictions = model.predict(img_array)
            print(f"Raw predictions: {predictions}") # For debugging: e.g., [[0.1, 0.9]]

            # Interpret softmax output (two probabilities)
            predicted_class_index = np.argmax(predictions[0]) # Get the index of the highest probability
            confidence = predictions[0][predicted_class_index] # Get the confidence for that class

            # Map the index to the human-readable class label
            class_label = CLASS_NAMES.get(predicted_class_index, "Unknown")
            confidence_percentage = f"{confidence * 100:.2f}%"

            prediction_text = f"The fruit/vegetable is predicted to be: {class_label} (Confidence: {confidence_percentage})"
            
            image_path = url_for('uploaded_file', filename=filename)

            return render_template('output.html', prediction_text=prediction_text, image_path=image_path, now={'year': datetime.now().year})

        except Exception as e:
            print(f"An error occurred during image processing or prediction: {e}")
            return render_template('output.html', prediction_text=f"An error occurred during prediction: {e}", image_path=None, now={'year': datetime.now().year})
    else:
        print("Invalid file type uploaded.")
        return render_template('output.html', prediction_text="Invalid file type. Please upload an image (png, jpg, jpeg, gif).", image_path=None, now={'year': datetime.now().year})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Serve uploaded files from the UPLOAD_FOLDER.
    """
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)