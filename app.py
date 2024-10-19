from flask import Flask, request, jsonify, render_template
import yt_dlp
import os

app = Flask(__name__)

# Fungsi untuk mendapatkan daftar format audio dan video
def get_video_formats(url):
    cookies_file = 'cookies.txt'
    ydl_opts = {
        'noplaylist': True,
        'cookiefile': cookies_file,
        'quiet': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])
        
        audio_options = []
        video_options = []
        
        for fmt in formats:
            if fmt.get('acodec') != 'none':
                quality = fmt.get('abr', 'audio')
                audio_options.append({'quality': f"{quality} kbps", 'url': fmt['url']})
            elif fmt.get('vcodec') != 'none':
                quality = fmt.get('height', 'no audio')
                video_options.append({'quality': f"{quality}p (no audio)", 'url': fmt['url']})

    return {'audio': audio_options, 'video': video_options}

def get_youtube_download_url(url, quality):
    cookies_file = 'cookies.txt'
    ydl_opts = {
        'noplaylist': True,
        'cookiefile': cookies_file,
        'quiet': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        for fmt in info_dict['formats']:
            if 'abr' in fmt and f"{fmt['abr']} kbps" == quality:
                return fmt['url']
            elif 'height' in fmt and f"{fmt['height']}p (no audio)" == quality:
                return fmt['url']
    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/youtube_downloader')
def index():
    return render_template('index.html')

@app.route('/video_formats', methods=['POST'])
def video_formats():
    data = request.json
    url = data.get('url')
    download_type = data.get('type')

    if not url or not download_type:
        return jsonify({'error': 'URL and download type are required'}), 400

    try:
        formats = get_video_formats(url)
        if download_type == 'audio':
            return jsonify({'audio': formats['audio']})
        elif download_type == 'video':
            return jsonify({'video': formats['video']})
        else:
            return jsonify({'error': 'Invalid download type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    quality = data.get('quality')

    if not url or not quality:
        return jsonify({'error': 'URL and quality are required'}), 400

    try:
        download_url = get_youtube_download_url(url, quality)
        if not download_url:
            return jsonify({'error': 'Could not retrieve download URL'}), 404
        return jsonify({'download_url': download_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
