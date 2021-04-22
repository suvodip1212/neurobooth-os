# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 10:46:13 2021

@author: adonay
"""

import pyrealsense2 as rs
from time import sleep as tsleep
from time import time
import threading
import uuid
from pylsl import StreamInfo, StreamOutlet
import functools
import warnings
warnings.filterwarnings('ignore')



def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        # try:
            return f(*args, **kwargs)
        # except Exception as e:
            # print('Caught an exception in function "{}" of type {}'.format(f.__name__, e))
    return func


class VidRec_Intel():        
    def __init__(self, size_rgb=(640, 480), size_depth=(640, 360),
                 fps_rgb=90, fps_depth=90, camindex=3):
        
        self.open = True
        self.recording = False
        self.device_index = camindex
        self.fps = (fps_rgb, fps_depth)                
        self.frameSize = (size_rgb, size_depth) 
        
        self.config = rs.config()
        self.pipeline =  rs.pipeline()
        self.config.enable_stream(rs.stream.depth, self.frameSize[0][0], 
                                  self.frameSize[0][1], rs.format.z16, self.fps[0])
        self.config.enable_stream(rs.stream.color, self.frameSize[1][0], 
                                  self.frameSize[1][1], rs.format.rgb8, self.fps [1])   

    @catch_exception
    def start(self, name="temp_video"):
        self.prepare(name)
        self.video_thread = threading.Thread(target=self.record)
        self.video_thread.start()
        
    @catch_exception
    def prepare(self, name):
        self.name = name
        self.video_filename = "{}.bag".format(name)     
        self.config.enable_record_to_file(self.video_filename)       
        self.outlet = self.createOutlet(name)

    @catch_exception        
    def createOutlet(self, filename):
        streamName = f'IndelFrameIndex_cam{self.device_index}'
        info = StreamInfo(name=streamName, type='videostream', channel_format='int32',
                          channel_count=2, source_id=str(uuid.uuid4()))
        info.desc().append_child_value("videoFile", filename)
        info.desc().append_child_value("size_rgb_depth", str(self.frameSize))         
        return StreamOutlet(info)
    
    @catch_exception
    def record(self):
        self.recording = True
        self.frame_counter = 0
        print(f"Intel {self.device_index} recording {self.video_filename}")
        self.pipeline.start(self.config)        
        while self.recording:
             frame = self.pipeline.wait_for_frames()
             self.n = frame.get_frame_number() 
             try:
                 self.outlet.push_sample([self.frame_counter, self.n]) 
             except:  # "OSError" from C++
                print("Reopening intel stream already closed")
                self.outlet = self.createOutlet(self.name)
                self.outlet.push_sample([self.frame_counter, self.n]) 
                
             self.frame_counter += 1
             
        self.pipeline.stop()
        print(f"Intel {self.device_index} recording ended, total frames captured: {self.n}, pushed lsl indexes: {self.frame_counter}") 
             
    @catch_exception
    def stop(self):
        if self.recording:
            self.recording = False     
                   
#            self.outlet.__del__()

    @catch_exception        
    def close(self):
        self.previewing = False  
        self.stop()        
        


    





