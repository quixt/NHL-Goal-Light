# import os

# import pygame
import time
from subprocess import call
class MusicPlayer:
    def __init__(self, staticDir:str = None):
        self.staticDir = f"./{staticDir}" if staticDir is not None else "./"
    def play_horn(self, team:str):
        call(["aplay","-D","hw:3,0",f"./static/{team}.wav"])

# class MusicPlayer:
#     def __init__(self, staticDir:str = None):
#         self.staticDir = f"./{staticDir}" if staticDir is not None else "./"
#         self.frequency = 44100
#         self.bitsize = -16
#         self.channels = 2 # Stereo audio
#         self.buffer = 2048
#         pygame.mixer.init()#self.frequency, self.bitsize, self.channels, self.buffer)
#     def play_horn(self, team:str, format:str = None, fadeIn:bool = False, volume:float = 0.8):
#         clock = pygame.time.Clock()
#         pygame.mixer.music.set_volume(volume)
#         fileName = f"{team}.{'wav' if format is None else format}"
#         filePath = f"{self.staticDir}/{fileName}"
#         try:
#             print(filePath)
#             pygame.mixer.music.load(filePath)
#             print("Music file {} loaded!".format(fileName))
#         except pygame.error as error:
#             print(error)
#             print("File {} not found! {}".format(fileName, pygame.get_error()))
#             return
#         pygame.mixer.music.play()
        
#         if fadeIn:
#             for x in range(0,100):
#                 pygame.mixer.music.set_volume(float(x)/100.0)
#                 time.sleep(0.0075)
#         while pygame.mixer.music.get_busy():
#             clock.tick(30)