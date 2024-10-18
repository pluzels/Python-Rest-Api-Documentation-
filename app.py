from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

# Fungsi untuk mendapatkan link download dengan cookies
def get_youtube_download_url(url, format_type):
    ydl_opts = {
        'format': 'bestaudio' if format_type == 'audio' else 'bestvideo+bestaudio',
        'noplaylist': True,
        'cookiefile': 'cookies.txt',  # Path ke file cookies
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict['url']
        except Exception as e:
            return str(e)

# Endpoint untuk mendapatkan link audio atau video
@app.route('/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('url')
    format_type = data.get('format', 'audio')  # Default ke audio jika format tidak ditentukan

    if not video_url:
        return jsonify({'error': 'Video URL is required'}), 400

    # Mendapatkan link download
    download_url = get_youtube_download_url(video_url, format_type)

    if 'error' in download_url:
        return jsonify({'error': download_url}), 500

    return jsonify({'download_url': download_url})

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(debug=True)
