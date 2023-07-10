from gpiozero import MotionSensor
from datetime import datetime
import pytz
from telegram.ext import Updater, CommandHandler
import os
import Thread
import picamera
from subprocess import call

pir = MotionSensor(4)


class RaspberryPiBot(object):
    _instance = None

    def __new__(cls):
        if not hasattr(cls, '_inst'):
            RaspberryPiBot._instance = super(RaspberryPiBot, cls).__new__(cls)
            return RaspberryPiBot._instance

    def __init__(self):
        self.updater = Updater(os.getenv("TOKEN"), use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480)
        self.CreateHandler()
        self.run()

    def CreateHandler(self):
        self.dispatcher.add_handler(CommandHandler("photo", self.get_photo))

    def run(self):
        Thread.Thread(self.detect_motion, ())
        self.updater.start_polling(timeout=1990000, poll_interval=5)
        self.updater.idle()

    def get_photo(self, update, context):
        print(update)
        self.camera.resolution = (1920, 1080)
        now = datetime.now(pytz.timezone('Europe/Kyiv'))
        photo_file = '/home/pi/Desktop/Photo/' + now.strftime("%d-%m-%Y-%H-%M-%S") + ".h264"
        self.camera.start_preview()
        self.camera.capture(photo_file)
        context.bot.sendPhoto(os.getenv("CHAT_ID"), open(photo_file, 'rb'))

    def detect_motion(self):
        while True:
            print("wait for a motion")
            pir.wait_for_motion()
            now = datetime.now(pytz.timezone('Europe/Kyiv'))
            current_time = now.strftime("%H:%M:%S")
            print("Motion detected! Current Time =", current_time)
            self.updater.bot.send_message("397362619", ("Motion detected! Current Time =", current_time))
            self.file_name = "/home/pi/Desktop/Video/" + now.strftime("%d-%m-%Y-%H-%M-%S") + ".h264"
            self.camera.start_recording(self.file_name)
            self.camera.wait_recording(20)
            self.camera.stop_recording()
            self.convert_video()
            self.updater.bot.send_video(os.getenv("CHAT_ID"), open(self.file_name, 'rb'))

    def convert_video(self):
        file_mp4 = self.file_name.replace(".h264", ".mp4")
        command = "MP4Box -add " + self.file_name + " " + file_mp4
        print(command)
        call([command], shell=True)
        self.file_name = file_mp4


RaspberryPiBot()
