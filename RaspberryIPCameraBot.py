from gpiozero import MotionSensor
from datetime import datetime
import pytz
from telegram.ext import Updater, MessageHandler, Filters
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
        self.UseCommand = {}
        self.updater = Updater(os.getenv("TOKEN"), use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480)
        self.CreateHandler()
        self.run()

    def CreateHandler(self):
        dispatcher_handler_text = MessageHandler(Filters.command | Filters.text, RaspberryPiBot.Dispatcher_text)
        self.dispatcher.add_handler(dispatcher_handler_text)

    def run(self):
        Thread.Thread(self.detect_motion, ())
        self.updater.start_polling(timeout=1990000, poll_interval=5)
        self.updater.idle()

    @classmethod
    def Dispatcher_text(self, update, context):
        print(update)

    def detect_motion(self):
        while True:
            print("wait for a motion")
            pir.wait_for_motion()
            now = datetime.now(pytz.timezone('Europe/Kyiv'))
            current_time = now.strftime("%H:%M:%S")
            print("Motion detected! Current Time =", current_time)
            self.updater.bot.send_message(os.getenv("CHAT_ID"), ("Motion detected! Current Time =", current_time))
            self.file_name = "/home/pi/Desktop/Video/" + now.strftime("%d-%m-%Y-%H-%M-%S") + ".h264"
            self.camera.start_recording(self.file_name)
            self.camera.wait_recording(20)
            self.camera.stop_recording()
            self.convert_video()
            self.updater.bot.send_video(os.getenv("CHAT_ID"), open(self.file_name, 'rb'))

    def convert_video(self):
        file_mp4 = self.file_name.replace(".h264", ".mp4")
        command = "MP4Box -add " + self.file_name + " " + file_mp4
        call([command], shell=True)
        self.file_name = file_mp4


RaspberryPiBot()
