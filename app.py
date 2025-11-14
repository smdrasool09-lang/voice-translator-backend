from flask import Flask, request, jsonify
from flask_cors import CORS
from deep_translator import GoogleTranslator
import speech_recognition as sr
import tempfile
import os

app = Flask(__name__)
CORS(app)

@app.route("/translate", methods=["POST"])
def translate_text():
    try:
        text = request.form.get("text")
        if not text:
            return jsonify({"error": "No text provided"}), 400

        translated_en = text
        try:
            translated_en = GoogleTranslator(source="auto", target="en").translate(text)
        except:
            pass

        translated_te = GoogleTranslator(source="auto", target="te").translate(text)
        translated_ta = GoogleTranslator(source="auto", target="ta").translate(text)

        return jsonify({
            "original": text,
            "translated": {
                "english": translated_en,
                "telugu": translated_te,
                "tamil": translated_ta
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/voice", methods=["POST"])
def translate_voice():
    wav_path = None
    
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file"}), 400

        audio_file = request.files["audio"]
        
        # Save the WAV file directly
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            audio_file.save(temp_wav.name)
            wav_path = temp_wav.name
        
        print(f"Audio file saved: {wav_path}")
        print(f"File size: {os.path.getsize(wav_path)} bytes")
        
        # Recognize speech
        r = sr.Recognizer()
        try:
            with sr.AudioFile(wav_path) as source:
                print("Reading audio file...")
                audio_data = r.record(source)
                print("Recognizing speech...")
                text = r.recognize_google(audio_data)
                print(f"Recognized: {text}")
        except sr.UnknownValueError:
            if os.path.exists(wav_path):
                os.remove(wav_path)
            return jsonify({"error": "Could not understand audio. Please speak louder and clearer."}), 400
        except sr.RequestError as e:
            if os.path.exists(wav_path):
                os.remove(wav_path)
            return jsonify({"error": f"Google Speech Recognition service error: {str(e)}"}), 500
        except Exception as e:
            if os.path.exists(wav_path):
                os.remove(wav_path)
            return jsonify({"error": f"Audio processing error: {str(e)}"}), 500
        
        # Clean up WAV file
        if os.path.exists(wav_path):
            os.remove(wav_path)

        # Translate
        translated_te = GoogleTranslator(source="auto", target="te").translate(text)
        translated_ta = GoogleTranslator(source="auto", target="ta").translate(text)

        return jsonify({
            "original": text,
            "translated": {
                "english": text,
                "telugu": translated_te,
                "tamil": translated_ta
            }
        })
        
    except Exception as e:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Starting Flask server...")
    print("Make sure to install: pip install flask flask-cors deep-translator SpeechRecognition")
    app.run(debug=True, host="127.0.0.1", port=5000)