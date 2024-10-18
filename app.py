from flask import Flask, request, jsonify, render_template
import yt_dlp
import os
import json

app = Flask(__name__)

def get_youtube_download_url(url, format_type):
    # Membaca cookies dari file
    try:
        with open('cookies.txt', 'r') as f:
            cookies = json.load(f)
    except json.JSONDecodeError:
        return None, "Error: Invalid JSON in cookies.txt"
    except FileNotFoundError:
        return None, "Error: cookies.txt not found"

    # Menyimpan cookies ke dalam format yang diperlukan oleh yt-dlp
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict[cookie['name']] = cookie['value']

    # Opsi untuk yt-dlp
    ydl_opts = {
        'format': 'bestaudio' if format_type == 'audio' else 'bestvideo+bestaudio',
        'noplaylist': True,
        'cookies': cookie_dict  # Menambahkan cookies di sini
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            # Ambil link download terbaik berdasarkan format yang dipilih
            if format_type == 'audio':
                return info_dict['url'], None  # Link audio
            else:
                return info_dict['url'], None  # Link video
    except Exception as e:
        return None, str(e)  # Tangani kesalahan yt-dlp

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

    download_url, error = get_youtube_download_url(url, download_type)

    if error:
        return jsonify({'error': error}), 500

    return jsonify({'download_url': download_url})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
