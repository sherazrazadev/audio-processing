from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import subprocess
import speech_recognition as sr

app = Flask(__name__)

# Define the paths
UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './output'  # New output folder
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Create the uploads and output folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def tts_pipeline(text, model_name, vocoder_name, out_path):
    # Run TTS synthesis
    subprocess.run(['tts', '--text', text, '--model_name', model_name, '--vocoder_name', vocoder_name, '--out_path', out_path])

def stt_pipeline(audio_input, output_text_file):
    recognizer = sr.Recognizer()

    # Load the audio file
    with sr.AudioFile(audio_input) as source:
        audio_data = recognizer.record(source)

        try:
            # Use Google Speech Recognition to convert audio to text
            text = recognizer.recognize_google(audio_data)

            # Save the text to the output file
            with open(output_text_file, 'w') as output_file:
                output_file.write(text)

            print(f"STT Output saved to: {output_text_file}")

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

@app.route('/tts-stt', methods=['POST'])
def tts_stt():
    mode = request.form.get('mode')

    if mode is None or mode not in ['TTS', 'STT']:
        return jsonify({'error': 'Invalid or missing mode parameter. Use "TTS" or "STT"'})

    if mode == 'TTS':
        text = request.form.get('text')

        if text is None:
            return jsonify({'error': 'Missing required parameter "text"'})

        tts_model_name = 'tts_models/en/ljspeech/tacotron2-DDC_ph'
        vocoder_name = 'vocoder_models/en/ljspeech/univnet'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.mp3')  # Updated output path

        tts_pipeline(text, tts_model_name, vocoder_name, output_path)
        return jsonify({'result': 'TTS process initiated', 'output_path': output_path})
    elif mode == 'STT':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            stt_output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.txt')  # Updated output path
            stt_pipeline(file_path, stt_output_path)

            with open(stt_output_path, 'r') as f:
                stt_output = f.read()

            return jsonify({'result': stt_output, 'message': 'STT process complete', 'output_path': stt_output_path})
        else:
            return jsonify({'error': 'Invalid file extension'})

if __name__ == "__main__":
    app.run(debug=True)
