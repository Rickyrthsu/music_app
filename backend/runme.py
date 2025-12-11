import os
import requests 
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from groq import Groq

# ==========================================
# 🛠️ 路徑設定
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(os.path.dirname(current_dir), 'frontend')

app = Flask(__name__, template_folder=frontend_dir, static_folder=frontend_dir)
CORS(app)

# ==========================================
# 🔑 API 金鑰
# ==========================================
SPOTIPY_CLIENT_ID = '你的_SPOTIFY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = '你的_SPOTIFY_CLIENT_SECRET'
GROQ_API_KEY = '你的_GROQ_API_KEY'

# ==========================================
# 🛠️ 初始化服務
# ==========================================
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
    print("✅ Groq 連線成功")
except Exception as e:
    print(f"❌ Groq 連線失敗: {e}")

sp_auth = None
try:
    sp_auth = SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET
    )
    token = sp_auth.get_access_token(as_dict=False)
    print("✅ Spotify 認證成功")
except Exception as e:
    print(f"❌ Spotify 認證失敗: {e}")

# ==========================================
# 🚀 API 路由
# ==========================================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/recommend_by_emoji', methods=['POST'])
def recommend_by_emoji():
    try:
        data = request.json
        emoji = data.get('emoji')
        print(f"📩 收到 Emoji: {emoji}")

        # 1. 設定參數
        target_valence = 0.5
        target_energy = 0.5
        seed_genres = 'pop' 

        if emoji in ['😢', '😭', 'sad']:
            seed_genres = 'acoustic,piano'
            target_energy = 0.2
            target_valence = 0.1
        elif emoji in ['⚡', '🔥', 'angry']:
            seed_genres = 'edm,work-out'
            target_energy = 0.9
            target_valence = 0.8
        elif emoji in ['🧘', 'calm']:
            seed_genres = 'ambient,classical'
            target_energy = 0.1
            target_valence = 0.5
        elif emoji in ['🥰', '❤️', 'happy']:
            seed_genres = 'romance,pop'
            target_energy = 0.6
            target_valence = 0.9
        
        # 2. 取得 Token
        access_token = sp_auth.get_access_token(as_dict=False)
        
        # 3. 🔥 修正這裡：使用正確的官方 API URL 🔥
        url = "https://api.spotify.com/v1/recommendations"
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "seed_genres": seed_genres,
            "limit": 1,
            "target_energy": target_energy,
            "target_valence": target_valence
        }

        # 4. 發送請求 (強制繞過 Proxy)
        print(f"⚡ 發送請求至: {url}")
        response = requests.get(
            url, 
            headers=headers, 
            params=params, 
            proxies={"http": None, "https": None}, # 確保不走系統 Proxy
            timeout=10
        )

        if response.status_code != 200:
            print(f"❌ Spotify API Error: {response.text}")
            return jsonify({'status': 'error', 'message': f"Spotify API Error: {response.status_code}"}), 500

        recommendations = response.json()
        
        tracks = []
        for track in recommendations.get('tracks', []):
            tracks.append({
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'url': track['external_urls']['spotify'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else None
            })

        return jsonify({'status': 'success', 'tracks': tracks})

    except Exception as e:
        print(f"❌ 嚴重錯誤: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/analyze_diary', methods=['POST'])
def analyze_diary():
    try:
        data = request.json
        diary_content = data.get('content', '')
        
        if not diary_content:
            return jsonify({'status': 'error', 'message': 'Empty content'}), 400

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "你是一個溫暖的諮商師，請簡短給予鼓勵。"},
                {"role": "user", "content": diary_content}
            ],
            model="llama3-8b-8192",
        )
        reply = chat_completion.choices[0].message.content

        return jsonify({'status': 'success', 'analysis': reply})

    except Exception as e:
        print(f"❌ 分析錯誤: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("🚀 LUMIYA 修正版啟動")
    print(f"📂 前端路徑: {frontend_dir}")
    app.run(debug=True, port=5000)