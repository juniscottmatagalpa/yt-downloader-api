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

@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "Falta el parámetro 'url'"}), 400

        # 📂 Crear carpeta temporal para el video
        temp_dir = tempfile.mkdtemp()

        # 🔹 Aquí colocas el bloque de opciones de yt-dlp
        ydl_opts = {
            "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
            "format": "best[ext=mp4]/best",  # fuerza un formato mp4 con audio y video juntos
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True
        }

        # 📥 Descargar el video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # 🧾 Verificar que el archivo existe
        if not os.path.exists(filename):
            return jsonify({"error": "No se pudo descargar el video."}), 500

        # 📦 Enviar el archivo como descarga directa
        response = send_file(filename, as_attachment=True)

        # 🧹 Eliminar el archivo y carpeta temporal después de enviarlo
        @response.call_on_close
        def cleanup():
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Error limpiando archivos temporales: {e}")

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)







