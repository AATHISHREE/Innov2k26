# app.py (UPDATED VERSION)
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import logging

# Import from core modules
from core.database import save_screening_result, get_patient_history, get_system_stats
from core.patient_service import register_patient, check_patient_exists, get_patient_details
from core.ml_client import MLClient  # ✅ UPDATED IMPORT
from core.sms_service import send_sms_alert

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize ML Client
ml_client = MLClient()  # ✅ INITIALIZE HERE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    ml_status = ml_client.get_status()  # ✅ USE ml_client
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ml_integration': ml_status,
        'upload_folder': os.path.abspath(UPLOAD_FOLDER),
        'message': 'PulseEcho Backend is running'
    })

@app.route('/analyze', methods=['POST'])
def analyze_heart_sound():
    """Analyze uploaded heart sound"""
    try:
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(audio_file.filename):
            return jsonify({'error': 'File type not allowed. Use WAV, MP3, or M4A'}), 400
        
        # Generate unique filename
        filename = secure_filename(audio_file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the file
        audio_file.save(audio_path)
        logger.info(f"Audio saved: {audio_path}")
        
        # Get patient data from form
        patient_id = request.form.get('patient_id', '')
        patient_name = request.form.get('patient_name', '')
        age = request.form.get('age', type=int)
        gender = request.form.get('gender', '')
        doctor_id = request.form.get('doctor_id', '')
        symptoms = request.form.get('symptoms', '')
        
        # Create patient context
        patient_context = {
            'patient_id': patient_id,
            'name': patient_name,
            'age': age,
            'gender': gender,
            'doctor_id': doctor_id,
            'symptoms': symptoms
        }
        
        # Analyze with ML client - ✅ UPDATED CALL
        logger.info(f"Analyzing audio for patient {patient_id}")
        ml_result = ml_client.analyze_heart_sound(audio_path, patient_context)
        
        # Prepare screening result for database
        screening_data = {
            'patient_id': patient_id,
            'patient_name': patient_name,
            'age': age,
            'gender': gender,
            'doctor_id': doctor_id,
            'audio_filename': unique_filename,
            'prediction': ml_result.get('prediction'),
            'confidence': ml_result.get('confidence'),
            'risk_level': ml_result.get('risk_level'),
            'recommendation': ml_result.get('recommendation'),
            'ml_source': ml_result.get('ml_source'),
            'symptoms': symptoms,
            'created_at': datetime.now().isoformat()
        }
        
        # Save to database
        db_result = save_screening_result(screening_data)
        
        # Send SMS alert if high risk
        if ml_result.get('risk_level') == 'high' and patient_context.get('phone'):
            phone = patient_context.get('phone')
            message = f"Urgent: Your heart screening shows high risk. {ml_result.get('recommendation', '')}"
            sms_result = send_sms_alert(phone, message)
            ml_result['sms_sent'] = sms_result.get('success', False)
        
        # Add database ID to response
        ml_result['screening_id'] = db_result.get('id', '')
        ml_result['audio_file'] = unique_filename
        
        return jsonify(ml_result)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/mock-analyze', methods=['POST'])
def mock_analyze():
    """Mock analysis endpoint for testing"""
    try:
        data = request.get_json() or {}
        
        patient_context = {
            'patient_id': data.get('patient_id', 'TEST001'),
            'age': data.get('age', 35),
            'gender': data.get('gender', 'male'),
            'symptoms': data.get('symptoms', '')
        }
        
        # Use ML client's mock analysis
        result = ml_client._mock_analysis(patient_context)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/patients/register', methods=['POST'])
def register_patient_endpoint():
    """Register a new patient"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result = register_patient(data)
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/patients/check', methods=['POST'])
def check_patient():
    """Check if patient exists"""
    try:
        data = request.get_json()
        
        if not data or 'patient_id' not in data:
            return jsonify({'error': 'patient_id required'}), 400
        
        result = check_patient_exists(data['patient_id'])
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient details"""
    try:
        result = get_patient_details(patient_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history/<patient_id>', methods=['GET'])
def get_history(patient_id):
    """Get patient screening history"""
    try:
        history = get_patient_history(patient_id)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        stats = get_system_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>', methods=['GET'])
def get_audio(filename):
    """Serve uploaded audio file"""
    try:
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if os.path.exists(audio_path):
            return send_file(audio_path, mimetype='audio/wav')
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create uploads directory if not exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Create ml_model directory if not exists
    os.makedirs('ml_model', exist_ok=True)
    
    print("🚀 Starting PulseEcho Backend Server...")
    print(f"✅ ML Client Status: {ml_client.get_status()}")
    print(f"📁 Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print("🌐 Server running on http://localhost:5000")
    print("📋 Endpoints:")
    print("   GET  /health            - Health check")
    print("   POST /analyze           - Analyze heart sound")
    print("   POST /mock-analyze      - Mock analysis")
    print("   POST /patients/register - Register patient")
    print("   GET  /history/<id>      - Get patient history")
    
    app.run(host='0.0.0.0', port=5000, debug=True)