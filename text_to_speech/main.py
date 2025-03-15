import argparse
import os
import subprocess
import speech_recognition as sr

def tts_pipeline(text, model_name, vocoder_name, out_path):
    # Run TTS synthesis
    subprocess.run(['tts', '--text', text, '--model_name', model_name, '--vocoder_name', vocoder_name, '--out_path', out_path])

    return out_path

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

def main():
    parser = argparse.ArgumentParser(description="TTS and STT Pipeline")

    parser.add_argument("--mode", choices=["TTS", "STT"], required=True, help="Select TTS or STT mode")
    parser.add_argument("--text", help="Text input for TTS mode")
    parser.add_argument("--input_path",  help="Input audio path for STT mode")
    parser.add_argument("--tts_model_name", default="tts_models/en/ljspeech/tacotron2-DDC_ph", help="Model name for TTS")
    parser.add_argument("--vocoder_name", default="vocoder_models/en/ljspeech/univnet", help="Vocoder name for TTS")
    parser.add_argument("--output_path", default="./", help="Output path for TTS or STT")

    args = parser.parse_args()

    if args.mode == "TTS":
        mp3_output_path = tts_pipeline(args.text, args.tts_model_name, args.vocoder_name, args.output_path)
        print(f"TTS Output saved to: {mp3_output_path}")
    elif args.mode == "STT":
        stt_pipeline(args.input_path, args.output_path)
        print(f"STT Output saved to: {args.output_path}")

if __name__ == "__main__":
    main()
