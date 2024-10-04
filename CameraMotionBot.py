# -*- coding: utf-8 -*-
import cv2
import os
import time
import pytz
from telegram.ext import Updater, CommandHandler
from datetime import datetime
from picamera import PiCamera
from picamera.array import PiRGBArray
import Thread
import subprocess
from gpiozero import CPUTemperature
import psutil

class RaspberryPiBot(object):
    def __init__(self):
        self.updater = Updater(os.getenv("TOKEN"), use_context=True)  # os.getenv("TOKEN2"), use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.camera = PiCamera()
        self.chat_id = os.getenv("CHAT_ID")
        self.camera.resolution = (720, 480)
        self.camera.framerate = 24
        self.rawCapture = PiRGBArray(self.camera, size=(720, 480))
        time.sleep(2)
        self.cpu = CPUTemperature()
        self.recording = False
        self.CreateHandler()
        self.run()

    def CreateHandler(self):
        # self.dispatcher.add_handler(CommandHandler("photo", self.get_photo))
        # self.dispatcher.add_handler(CommandHandler("video", self.get_video))
        self.dispatcher.add_handler(CommandHandler("stats", self.stats))
        self.dispatcher.add_handler(CommandHandler("restart", self.restart))

    def restart(self, update, context):
        if update.message.chat_id == self.chat_id:
            os.system("sudo reboot")

    def run(self):
        Thread.Thread(self.detect_motion, ())
        self.updater.start_polling(timeout=120, poll_interval=5)
        self.updater.idle()

    def stats(self, update, context):
        bytes_avail = psutil.disk_usage('/').free
        gigabytes_avail = bytes_avail / 1024 / 1024 / 1024
        print(gigabytes_avail)
        context.bot.send_message(self.chat_id,
                                 "Free space: {0}gb\nTemperature CPU: {1}c\n".format(gigabytes_avail,
                                                                                     self.cpu.temperature))

    def detect_motion(self):
        try:
            while True:
                first_frame = None
                now = datetime.now(pytz.timezone('Europe/Kyiv'))
                video_filename_h264 = "/home/pi/Desktop/Video/" + now.strftime("%d-%m-%Y-%H-%M-%S") + ".h264"
                video_filename_mp4 = "/home/pi/Desktop/Video/" + now.strftime("%d-%m-%Y-%H-%M-%S") + ".mp4"
                movement_detected = False
                last_motion_time = 0
                record_duration_after_motion = 10
                start_recording_time = time.time()
                max_video_length = 30

                self.camera.start_recording(video_filename_h264)

                for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
                    image = frame.array
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    gray = cv2.GaussianBlur(gray, (21, 21), 0)

                    if first_frame is None:
                        first_frame = gray
                        self.rawCapture.truncate(0)
                        continue

                    delta_frame = cv2.absdiff(first_frame, gray)
                    thresh_frame = cv2.threshold(delta_frame, 25, 255, cv2.THRESH_BINARY)[1]
                    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

                    image, contours, hierarchy = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL,
                                                                  cv2.CHAIN_APPROX_SIMPLE)
                    motion_in_frame = False

                    for contour in contours:
                        if cv2.contourArea(contour) < 2000:
                            continue

                        motion_in_frame = True
                        last_motion_time = time.time()  # Оновлюємо час останнього руху
                        print(f"Рух виявлено! Час: {last_motion_time}")
                        start_recording_time = time.time()
                        if not movement_detected:
                            movement_detected = True

                    if movement_detected:
                        first_frame = gray  # Оновлюємо кадр перевірки під час руху

                    if movement_detected and (time.time() - last_motion_time > record_duration_after_motion):
                        print("Рух припинився. Запис завершено.")
                        self.camera.stop_recording()
                        self.convert_to_mp4(video_filename_h264, video_filename_mp4)
                        self.updater.bot.send_video(self.chat_id, open(video_filename_mp4, 'rb'))
                        os.remove(video_filename_h264)
                        os.remove(video_filename_mp4)
                        movement_detected = False
                        self.camera.start_recording(video_filename_h264)  # Починаємо новий запис для наступного руху
                    if video_filename_h264 and time.time() - start_recording_time >= max_video_length:
                        print("Запис перевищує 30 секунд. Створення нового файлу.")
                        self.camera.stop_recording()
                        os.remove(video_filename_h264)
                        self.camera.start_recording(video_filename_h264)
                        start_recording_time = time.time()

                    self.rawCapture.truncate(0)
        except Exception as e:
            Thread.Thread(self.detect_motion, ())

    def convert_to_mp4(self, h264_file, mp4_file):
        command = ['ffmpeg', '-framerate', '24', '-i', h264_file, '-c:v', 'copy', mp4_file]
        subprocess.run(command)


RaspberryPiBot()