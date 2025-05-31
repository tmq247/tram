"""
from pyrogram import Client, filters
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from SANKIXD import app

@app.on_message(filters.command('tts'))
def text_to_speech(client, message):
    text = message.text.split(' ', 1)[1]
    
    # Tạo tệp âm thanh từ văn bản
    tts = gTTS(text=text, lang='vi')
    tts.save('speech.mp3')
    
    # Chỉnh sửa âm thanh bằng pydub
    audio = AudioSegment.from_file('speech.mp3', format='mp3')
    audio = audio.set_frame_rate(24000)  # Điều chỉnh tốc độ phát
    audio = audio + 5  # Tăng âm lượng
    
    # Lưu file mới
    audio.export('enhanced_speech.mp3', format='mp3')
    
    # Gửi file âm thanh
    client.send_audio(message.chat.id, 'enhanced_speech.mp3')
"""
from pyrogram import Client, filters
from TTS.api import TTS
from SANKIXD import app

@app.on_message(filters.command('tts'))
def text_to_speech(client, message):
    text = message.text.split(' ', 1)[1]
    
    # Khởi tạo mô hình TTS
    tts = TTS("tts_models/vietnamese/vietTTS")
    
    # Tạo file âm thanh với giọng tự nhiên
    tts.tts_to_file(text=text, file_path="speech.mp3")

    # Gửi file âm thanh
    client.send_audio(message.chat.id, "speech.mp3")
