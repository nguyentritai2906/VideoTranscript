import os
import shutil
import sys
import time
import tkinter as tk
from tkinter import filedialog

import speech_recognition as sr
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydub import AudioSegment
from pydub.silence import split_on_silence


# a function that splits the audio file into chunks
# and applies speech recognition
def silence_based_conversion(inputfile, outputfile):

    # open the audio file stored in
    # the local system as a wav file.
    sound = AudioSegment.from_wav(inputfile)

    # open a file where we will concatenate
    # and store the recognized text
    fh = open(outputfile, "w+")

    # split audio sound where silence is 700 miliseconds or more and get chunks
    print("Splitting audio into chunk...")
    chunks = split_on_silence(sound,
                              # experiment with this value for your audio file
                              min_silence_len=1000,
                              # adjust this per requirement
                              silence_thresh=sound.dBFS-14,
                              # keep the silence for 1 second, adjustable
                              keep_silence=500,
                              )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)

    # initialize the recognizer
    r = sr.Recognizer()

    # process each chunk
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        print("Recognizing chunk "+str(i)+"/"+str(len(chunks)))
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                print(text)
                fh.write(text)

    shutil.rmtree(folder_name)


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    root.update()
    filename = filedialog.askopenfilename(
        initialdir=".", title="Select File",
        filetypes=(("all files", "*.*"), ))
    root.destroy()
    if len(filename) == 0:
        sys.exit()
    print("Processing", filename)

    if filename[-3:] == "wav":
        silence_based_conversion(filename, filename[:-3] + "txt")
    else:
        # convert video to audio

        # insert Local Video File Path
        clip = VideoFileClip(filename)

        # insert Local Audio File Path
        clip.audio.write_audiofile(filename[:-3] + "wav")

        silence_based_conversion(
            filename[:-3] + "wav", filename[:-3] + "txt")
    print("Done!")
