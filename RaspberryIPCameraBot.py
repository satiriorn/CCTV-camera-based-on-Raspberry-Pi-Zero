from gpiozero import MotionSensor
from datetime import datetime
import pytz
from telegram.ext import Updater, MessageHandler, Filters
import os
import Thread

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
            self.updater.bot.send_message(os.getenv("Chat_id"), "Motion detected! Current Time ="+str(current_time))

RaspberryPiBot()
