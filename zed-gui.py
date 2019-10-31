import sys
import os
import cv2
import pyzed.sl as sl
import tkinter as tk
from tkinter import Frame
from PIL import Image
from PIL import ImageTk
import threading


# Initialize GUI
root = tk.Tk()
root.title("ZED Vision App")

# Create camera object
zed = sl.Camera()

# Configure initial parameter configuration for zed
# Disable depth mode and set resolution to HD2K
init = sl.InitParameters()
init.camera_resolution = sl.RESOLUTION.RESOLUTION_HD2K
init.depth_mode = sl.DEPTH_MODE.DEPTH_MODE_NONE

# Open the camera
err = zed.open(init)
if err != sl.ERROR_CODE.SUCCESS :
    print(repr(err))
    zed.close()
    exit(1)

# Configure the runtime to standard sensing mode and no depth image
runtime = sl.RuntimeParameters()
runtime.sensing_mode = sl.SENSING_MODE.SENSING_MODE_STANDARD
runtime.enable_depth = False

# Configure image holder for live preview
image_size = zed.get_resolution()
image_zed_full = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.MAT_TYPE_8U_C4)


stopFlag = False

# Start recording the video
def startCapture():
    print("Entering Capture")
    global stopFlag
    stopFlag = False
    # Enable recording on the filename provided
    filename = 'output.svo'
    # filename = sys.argv[1]
    err = zed.enable_recording(filename, sl.SVO_COMPRESSION_MODE.SVO_COMPRESSION_MODE_AVCHD)

    print("Recording...  Press Q to quit.")
    while True:
        if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS :
            # Each new frame is added to the SVO file
            zed.record()
        if stopFlag:
            zed.disable_recording()
            break
    print("Exiting Capture")
        


def getCapture():
    capture = threading.Thread(target=startCapture, args=())
    capture.start()

# Disable recording
def stopCapture():
    global stopFlag
    stopFlag = True
    print("Stop capture.")  
    convert()

# VideoLoop to show live preview
def videoLoop():
    try:
        panel = None
        while True:
            if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS :
                
                zed.retrieve_image(image_zed_full, sl.VIEW.VIEW_SIDE_BY_SIDE , sl.MEM.MEM_CPU, int(image_size.width/2), int(image_size.height/4))
                
                image_ocv_full = image_zed_full.get_data()

                image = cv2.cvtColor(image_ocv_full, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                if panel is None:
                    panel = tk.Label(image=image)
                    panel.image = image
                    panel.pack(side="left", padx=10, pady=10)
                else:   
                    panel.configure(image=image)
                    panel.image = image
            if stopVideo:
                zed.close()
                break
    except RuntimeError:
        print("[INFO] caught a RuntimeError")

def convert():
    print("Converting...")
    dirpath = os.getcwd()
    converter_path = "ZED_SVO_Export.exe"
    input_path = 'output.svo'
    output_path = dirpath+ "\\videos\\"+ 'output.svo'.split('.')[0] + ".avi"
    #print(output_path)
    os.popen(converter_path + " " + input_path + " " + output_path + " 0")
    #check conversion, delete .svo when done
    print("Done...")

def snapCapture():
    print("Snap")

def onClose():
    global stopVideo
    stopVideo = True
    global stopEvent
    stopEvent.set()
    global root
    root.quit()



# Configure GUI
bottomframe = Frame(root)
bottomframe.pack(side='bottom', fill=tk.X)
start_btn = tk.Button(bottomframe, height=5, text="Start", command=getCapture)
start_btn.pack(side='left', expand=1, fill=tk.X, padx=10, pady=10)
stop_btn = tk.Button(bottomframe, height=5, text="Stop", command=stopCapture)
stop_btn.pack(side='right', expand=1, fill=tk.X, padx=10, pady=10)
# snap_btn = tk.Button(root, text="SnapShot", command=snapCapture)
# snap_btn.pack()

# camera_label = tk.Label(root, text="No connected")
# camera_label.pack()

stopVideo = False

stopEvent = threading.Event()
video = threading.Thread(target=videoLoop, args=())
video.start()

root.wm_title("ZED Stereo Recorder")
root.wm_protocol("WM_DELETE_WINDOW", onClose)

root.mainloop()

