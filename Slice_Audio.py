from flask import Flask, render_template, request, send_file
from pydub import AudioSegment
import os
import webbrowser
from threading import Timer

app = Flask(
    __name__,
    template_folder="../Frontend",
    static_folder="../Styling",
    static_url_path="/static"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "..", "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/slice", methods=["POST"])
def slice_audio():

    if "audio" not in request.files:
        return "No audio file selected!"

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return "Please select an audio file!"

    try:
        start = float(request.form["start"])
        end = float(request.form["end"])

        upload_path = os.path.join(
            UPLOAD_FOLDER,
            audio_file.filename
        )

        audio_file.save(upload_path)

        audio = AudioSegment.from_file(upload_path)

        duration = len(audio) / 1000

        if start < 0:
            return "Start time cannot be negative!"

        if end > duration:
            return f"End time exceeds audio duration ({duration:.2f} sec)"

        if start >= end:
            return "Start time must be less than end time!"

        clip = audio[int(start * 1000):int(end * 1000)]

        filename, ext = os.path.splitext(audio_file.filename)

        output_file = f"sliced_{filename}.mp3"

        output_path = os.path.join(
            OUTPUT_FOLDER,
            output_file
        )

        clip.export(output_path, format="mp3")

        if not os.path.exists(output_path):
            return "Output file was not created!"

        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_file
        )

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    Timer(1, open_browser).start()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )