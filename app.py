from flask import Flask, request, jsonify, render_template
import yt_dlp
import os

app = Flask(__name__)

# Fungsi untuk mendapatkan daftar format video dan audio
def get_video_formats(url):
    cookies_file = 'cookies.txt'  # Pastikan ini adalah jalur yang benar untuk file cookies.txt
    ydl_opts = {
        'noplaylist': True,
        'cookiefile': cookies_file,  # Tambahkan opsi cookies
        'quiet': True,  # Untuk menghindari output yang berlebihan
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])
        video_options = []
        for fmt in formats:
            if fmt.get('acodec') != 'none':  # Format audio tersedia
                video_options.append(f"{fmt['height']}p (audio)")  # Misalnya: 1080p (audio)
            elif fmt.get('vcodec') != 'none':  # Format video tanpa audio
                video_options.append(f"{fmt['height']}p (no audio)")  # Misalnya: 720p (no audio)

    return video_options

# Fungsi untuk mendapatkan URL download berdasarkan format yang dipilih
def get_youtube_download_url(url, format_type):
    cookies_file = 'cookies.txt'  # Pastikan ini adalah jalur yang benar untuk file cookies.txt
    ydl_opts = {
        'format': 'bestaudio' if format_type == 'audio' else 'bestvideo+bestaudio',
        'noplaylist': True,
        'cookiefile': cookies_file,  # Tambahkan opsi cookies
        'quiet': True,  # Untuk menghindari output yang berlebihan
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)

        if format_type == 'audio':
            audio_url = None
            for format in info_dict['formats']:
                if 'acodec' in format and format['acodec'] != 'none':
                    audio_url = format['url']
                    break
            if audio_url is None:
                return None
            return audio_url
        else:
            for format in info_dict['formats']:
                if 'vcodec' in format and format['vcodec'] != 'none':
                    return format['url']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_formats', methods=['POST'])
def video_formats():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        formats = get_video_formats(url)
        return jsonify({'formats': formats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
