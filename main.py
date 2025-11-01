from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import tempfile
import os
import shutil

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "✅ Servidor de descargas activo"

# 🟢 Ruta para obtener información del video
@app.route("/info", methods=["POST"])
def info():
    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return jsonify({"error": "Falta el parámetro 'url'"}), 400

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        hashtags = []
        if "tags" in info and info["tags"]:
            hashtags = [f"#{tag}" for tag in info["tags"][:5]]

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "hashtags": hashtags
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔵 Ruta para descargar en baja o alta calidad
@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        url = data.get("url")
        quality = data.get("quality", "high")

        if not url:
            return jsonify({"error": "Falta el parámetro 'url'"}), 400

        temp_dir = tempfile.mkdtemp()

        if quality == "low":
            fmt = "best[height<=480][ext=mp4]/best[ext=mp4]/best"
        else:
            fmt = "bestvideo+bestaudio/best[ext=mp4]/best"

        ydl_opts = {
            "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
            "format": fmt,
            "merge_output_format": "mp4",
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.exists(filename):
            return jsonify({"error": "No se pudo descargar el video"}), 500

        response = send_file(filename, as_attachment=True)

        @response.call_on_close
        def cleanup():
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print("Error limpiando temporales:", e)

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)











