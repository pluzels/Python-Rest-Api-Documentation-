import os
from flask import Flask, request, jsonify, render_template
import yt_dlp

app = Flask(__name__)

def get_youtube_download_url(url, format_type):
    ydl_opts = {
        'format': 'bestaudio' if format_type == 'audio' else 'bestvideo+bestaudio',
        'noplaylist': True,
        'cookiefile': 'cookies.txt'  # Pastikan ini sesuai dengan nama file cookies
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        if format_type == 'audio':
            return info_dict['url']  # Link audio
        else:
            return info_dict['url']  # Link video

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
        return jsonify({'download_url': download_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
