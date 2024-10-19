from flask import Flask, request, jsonify, render_template
from pytube import YouTube
import os

app = Flask(__name__)

# Fungsi untuk mendapatkan link unduhan YouTube
def get_youtube_download_url(url, format_type):
    try:
        yt = YouTube(url)
        if format_type == 'audio':
            # Mengambil stream audio terbaik
            stream = yt.streams.filter(only_audio=True).first()
        else:
            # Mengambil stream video terbaik dengan resolusi tertinggi yang memiliki audio
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if stream:
            return stream.url
        else:
            return None
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    download_type = data.get('type', 'video')  # 'video' atau 'audio'

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        download_url = get_youtube_download_url(url, download_type)
        if download_url:
            return jsonify({'download_url': download_url})
        else:
            return jsonify({'error': 'Unable to find stream'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
