from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)  # 🔥 Esto permite peticiones desde cualquier dominio

@app.route("/")
def home():
    return "✅ Servidor de descargas activo"

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Falta el parámetro 'url'"}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best',
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
            download_url = formats[-1]["url"] if formats else info.get("url")

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "download_url": download_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)



