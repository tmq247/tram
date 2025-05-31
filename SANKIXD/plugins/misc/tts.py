from pyrogram import Client, filters
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from SANKIXD import app
from pydub.effects import normalize, speedup

@app.on_message(filters.command('tts'))
def text_to_speech(client, message):
    text = message.text.split(' ', 1)[1]
    
    # Tạo tệp âm thanh từ văn bản
    tts = gTTS(text=text, lang='vi')
    tts.save('speech.mp3')
    
    # Chỉnh sửa âm thanh bằng pydub
    audio = AudioSegment.from_file("speech.mp3", format="mp3")
    audio = normalize(audio)  # Chuẩn hóa âm lượng
    audio = speedup(audio, playback_speed=1.1)  # Tăng tốc độ phát nhẹ
    audio = audio.set_frame_rate(32000)  # Nâng cao tần số mẫu
    # Lưu file mới
    audio.export('speech.mp3', format='mp3')
    
    # Gửi file âm thanh
    client.send_audio(message.chat.id, 'peech.mp3')
