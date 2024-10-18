from flask import Flask, request, jsonify, render_template
import yt_dlp
import os
import json

app = Flask(__name__)

def get_youtube_download_url(url, format_type):
    cookies_file = 'cookies.txt'  # Pastikan ini adalah jalur yang benar untuk file cookies.txt
    ydl_opts = {
        'format': 'bestaudio' if format_type == 'audio' else 'bestvideo+bestaudio',
        'noplaylist': True,
        'cookiefile': cookies_file,  # Tambahkan opsi cookies
        'quiet': True,  # Untuk menghindari output yang berlebihan
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Format audio yang diinginkan
            'preferredquality': '192',  # Kualitas audio
        }] if format_type == 'audio' else []
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)

        if format_type == 'audio':
            # Mendapatkan URL audio yang sudah diproses
            audio_url = None
            for format in info_dict['formats']:
                if format['acodec'] != 'none':  # Memastikan format audio valid
                    audio_url = format['url']
                    break
            return audio_url
        else:
            # Untuk video, kita ambil URL video terbaik
            for format in info_dict['formats']:
                if format['vcodec'] != 'none':
                    return format['url']  # Link video

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
        if not download_url:
            return jsonify({'error': 'Could not retrieve download URL'}), 404
        return jsonify({'download_url': download_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
