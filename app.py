from flask import Flask, request, jsonify, render_template
import yt_dlp
import os

app = Flask(__name__)

# Fungsi untuk mendapatkan daftar format audio dan video
def get_video_formats(url):
    cookies_file = 'cookies.txt'  # Pastikan ini adalah jalur yang benar untuk file cookies.txt
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
            # Tambahkan format audio
            if fmt.get('acodec') != 'none':
                quality = fmt.get('abr', 'audio')  # Menggunakan bitrate audio
                audio_options.append({'quality': f"{quality} kbps", 'url': fmt['url']})
            elif fmt.get('vcodec') != 'none':  # Format video tanpa audio
                quality = fmt.get('height', 'no audio')
                video_options.append({'quality': f"{quality}p (no audio)", 'url': fmt['url']})

    return {'audio': audio_options, 'video': video_options}

# Fungsi untuk mendapatkan URL download berdasarkan format yang dipilih
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

# Fungsi untuk mendownload video TikTok
def download_tiktok_video(url):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])  # Mengunduh video TikTok
            print(f'Successfully downloaded: {url}')
        except Exception as e:
            print(f'Error downloading video: {str(e)}')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/youtube', methods=['GET'])
def youtube_index():
    return render_template('index.html')

@app.route('/video_formats', methods=['POST'])
def video_formats():
    data = request.json
    url = data.get('url')
    download_type = data.get('type')  # Mengambil tipe download (audio/video)

    if not url or not download_type:
        return jsonify({'error': 'URL and download type are required'}), 400

    try:
        formats = get_video_formats(url)
        if download_type == 'audio':
            return jsonify({'audio': formats['audio']})  # Mengembalikan hanya format audio
        elif download_type == 'video':
            return jsonify({'video': formats['video']})  # Mengembalikan hanya format video
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

@app.route('/download_tiktok', methods=['POST'])
def download_tiktok():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        download_tiktok_video(url)
        return jsonify({'message': 'Video is downloading'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
