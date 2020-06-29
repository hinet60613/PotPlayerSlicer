# coding=utf-8
import codecs
import re

class PbfParser():
    def __init__(self, file_name):
        self.file_name = file_name
    def getTimeMark(self):
        timemark_list = []
        with codecs.open(self.file_name, "r", encoding="utf-16") as f:
            head = f.readline()
            head= head.strip()
            print("header: {}".format(head))
            """
            if head is not "[Bookmark]":
                print("Error: input file({}) is not a PotPlayer bookmark file (pbf)".format(self.file_name))
            """
            for line in f.readlines():
                line = line.strip()
                x = re.split("\*", line)
                if len(x) < 2:
                    continue
                (bookmark_idx, timemark) = map(str, x[0].split("="))
                bookmark_name = x[1]
                timemark_list.append( (int(bookmark_idx), int(timemark), bookmark_name))
        return timemark_list

# utilities for converting time(milliseconds) to string(HH:MM:SS.MS)
def getTimeStr(t):
    scale = [1000, 60, 60, 60]
    strList = []
    for s in scale:
        strList.insert(0, str(t % s))
        t = t / s
    return ':'.join(strList[:-1]) + "." + strList[-1]

# utilities for converting milliseconds to seconds with decimal
def getSecStr(t):
    return '.'.join([str(t/1000), str(t%1000)])

def outputVideo(pbf_file_path, video_file_path, timemarks):
    import os
    if not os.path.exists("./output"):
        os.mkdir("./output")

    import ffmpeg
    in_file = ffmpeg.input(video_file_path)
    for (idx, mark) in enumerate(timemarks[:-1]):
        start_time = mark[1]
        end_time = timemarks[idx+1][1]
        str_start_time = getSecStr(start_time)
        str_end_time = getSecStr(end_time)
        str_duration = getSecStr(end_time - start_time)
        video = (
            in_file.video.trim(start = str_start_time, end = str_end_time).setpts('PTS-STARTPTS')
        )
        audio = (
            in_file.audio.filter('atrim', start=str_start_time, end=str_end_time)
        )
        
        out = ffmpeg.output(video, audio, filename='output/{}.mp4'.format(mark[0]+1))
        out.overwrite_output().run()

    mark = timemarks[-1]
    video = in_file.video.trim(start=getSecStr(mark[1])).setpts('PTS-STARTPTS')
    audio = in_file.audio.filter('atrim', start=str_start_time)
    ffmpeg.output(video, audio, filename='output/{}.mp4'.format(mark[0]+1)).overwrite_output().run()

def set_pbf_path():
    from tkinter import filedialog as fd
    filename = fd.askopenfilename(title="Select pbf file", filetypes=(("pbf file", "*.pbf"), ("all files", "*")))
    print("pbf: {}".format(filename))
    if filename:
        pbf_path_entry.delete(0,tk.END)
        pbf_path_entry.insert(0, filename)

def set_vid_path():
    from tkinter import filedialog as fd
    filename = fd.askopenfilename(title="Select video file")
    print("vid: {}".format(filename))
    if filename:
        vid_path_entry.delete(0,tk.END)
        vid_path_entry.insert(0, filename)

def gui_start_trimming():
    pbf_file_path = pbf_path_entry.get()
    video_file_path = vid_path_entry.get()

    # Parse PBF
    r = PbfParser(pbf_file_path)
    timemarks = r.getTimeMark()
    timemarks.insert(0, (-1, 0, "init"))

    outputVideo(pbf_file_path, video_file_path, timemarks)

    import tkMessageBox as msgbox
    msgbox.showinfo("Finished", "Trimming done.")


import tkinter as tk
window = tk.Tk()
top_frame = tk.Frame(window)
top_frame.pack()
center_frame = tk.Frame(window)
center_frame.pack()
bottom_frame = tk.Frame(window)
bottom_frame.pack()

txt_pbf_path = tk.Label(top_frame, text="Bookmark PBF file:")
txt_pbf_path.pack(side=tk.LEFT)
pbf_path_entry = tk.Entry(top_frame)#tk.Label(top_frame, textvariable=g_pbf_filename)
pbf_path_entry.pack(side=tk.LEFT)
btn_get_pbf = tk.Button(top_frame, text="...", command=set_pbf_path)
btn_get_pbf.pack(side=tk.LEFT)

txt_vid_path = tk.Label(center_frame, text="Video file:")
txt_vid_path.pack(side=tk.LEFT)
vid_path_entry = tk.Entry(center_frame)#tk.Label(center_frame, textvariable=g_vid_filename)
vid_path_entry.pack(side=tk.LEFT)
btn_get_vid = tk.Button(center_frame, text="...", command=set_vid_path)
btn_get_vid.pack(side=tk.LEFT)

btn_start_trimming = tk.Button(bottom_frame, text="Start trimming", command = gui_start_trimming)
btn_start_trimming.pack(side=tk.LEFT)


window.mainloop()
