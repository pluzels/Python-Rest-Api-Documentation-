from flask import Flask, request, jsonify, render_template
import yt_dlp
import os

app = Flask(__name__)

# Fungsi untuk mendapatkan daftar format audio dan video dari YouTube
def get_video_formats(url):
    cookies_file = 'cookies.txt'
    ydl_opts = {
        'noplaylist': True,
        'cookiefile': cookies_file if os.path.exists(cookies_file) else None,
        'quiet': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            
            audio_options = []
            video_options = []
            
            for fmt in formats:
                # Tambahkan format audio
                if fmt.get('acodec') != 'none' and fmt.get('url'):
                    quality = fmt.get('abr', 'audio')  # Menggunakan bitrate audio
                    audio_options.append({'quality': f"{quality} kbps", 'url': fmt['url']})
                # Tambahkan format video
                if fmt.get('vcodec') != 'none' and fmt.get('url'):
                    quality = fmt.get('height', 'no audio')
                    video_options.append({'quality': f"{quality}p (no audio)", 'url': fmt['url']})

            return {'audio': audio_options, 'video': video_options}

    except Exception as e:
        raise ValueError(f"Failed to retrieve formats: {e}")

# Fungsi untuk mendapatkan URL download berdasarkan format yang dipilih
def get_youtube_download_url(url, quality):
    cookies_file = 'cookies.txt'
    ydl_opts = {
        'noplaylist': True,
        'cookiefile': cookies_file if os.path.exists(cookies_file) else None,
        'quiet': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            for fmt in info_dict['formats']:
                if fmt.get('abr') and f"{fmt['abr']} kbps" == quality and fmt.get('url'):
                    return fmt['url']
                if fmt.get('height') and f"{fmt['height']}p (no audio)" == quality and fmt.get('url'):
                    return fmt['url']
            # Fallback jika kualitas spesifik tidak ditemukan
            return info_dict['formats'][0]['url'] if info_dict['formats'] else None

    except Exception as e:
        raise ValueError(f"Failed to retrieve download URL: {e}")

# Fungsi untuk mendownload video dari TikTok
def download_tiktok_video(url):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict.get('url', None)
    except Exception as e:
        raise ValueError(f"Failed to retrieve TikTok video: {e}")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/youtube', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/tiktok', methods=['GET'])
def tiktok():
    return render_template('tiktok.html')

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
        app.logger.error(f"Error retrieving video formats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_youtube', methods=['POST'])
def download_youtube():
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
        app.logger.error(f"Error downloading YouTube video: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_tiktok', methods=['POST'])
def download_tiktok():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        download_url = download_tiktok_video(url)
        if not download_url:
            return jsonify({'error': 'Could not retrieve download URL'}), 404
        return jsonify({'download_url': download_url})
    except Exception as e:
        app.logger.error(f"Error downloading TikTok video: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
