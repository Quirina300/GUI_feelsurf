import pygame
import sys
import nidaqmx
import numpy as np
from nidaqmx import constants
import time
import threading
import matplotlib.pyplot as plt


normalForce = -0.35

global texture

class daqMxWrite(threading.Thread):
    def __init__(self,data,gain_msg,gain_car):
        threading.Thread.__init__(self)
        self.f_play = True
        self.gain_car = gain_car
        self.data = gain_msg*(data - np.mean(data))
        self.f_play_stop = False

    def init(self):
        # Configure the properties of the sine wave
        frequency = 3000  # Frequency of the sine wave (in Hz)
        amplitude = self.gain_car  # Amplitude of the sine wave (in volts)
        duration = len(self.data)/10000  # Duration of the generated waveform (in seconds)
        self.sampling_rate = 10000  # Sampling rate of the waveform (in samples per second)
        self.num_samples = int(duration * self.sampling_rate)

        # Generate the time axis for the waveform
        time1 = np.linspace(0, duration, self.num_samples)

        # Generate the sine wave
        self.sine_wave = amplitude * np.sin(2 * np.pi * frequency * time1)

        self.tex_data = self.data + self.sine_wave

    def run(self):
        while self.f_play:
            with nidaqmx.Task() as task:
                if not self.f_play_stop:
                    print("Texture is rendering")
                    # Configure the task for waveform generation
                    task.ao_channels.add_ao_voltage_chan("cDAQ1Mod2/ao1")  # Replace "your_device_name" with the actual device name and channel
                    task.timing.cfg_samp_clk_timing(rate=self.sampling_rate, samps_per_chan=self.num_samples)

                    # Write the sine wave to the output channel
                    task.write(self.tex_data, auto_start=True)

                    # Wait for the waveform generation to complete
                    task.wait_until_done()
                else:
                    print("Texture rendering stopped")
                    task.stop()
                    task.close()
                        
    #Daq stop
    def DaqStop(self):
        self.f_play = False
        self.f_play_stop = True
        print("Texture rendering stopped")

class daqMxRead(threading.Thread):
    def __init__(self,samples,filename):
        threading.Thread.__init__(self)
        self.taskRead = nidaqmx.Task()
        self.taskWrite = nidaqmx.Task()
        self.samples = samples
        self.filename = filename
        self.Gain = [[-0.00942, 0.01089, 0.02493, -1.63393, -0.09430, 1.64036],
                     [-0.11606, 1.86623, -0.00740, -0.92721, 0.05722, -0.98835],
                     [1.87323, -0.03371, 1.85568, 0.00612, 1.92144, -0.03760],
                     [-1.04628, 11.47082, 10.26017, -5.65531, -10.47020, -5.89761],
                     [-12.08599, 0.12561, 5.54598, 10.01850, 6.79895, -10.15092],
                     [-0.38992, 6.89826, -0.06954, 7.05122, -0.35058, 7.11827]]

        self.IMU_gain = [0.8, 0.8, 0.8]
        self.forceBias = np.zeros((100,6),dtype=float)
        self.f_record = True

    def init(self):
        self.taskWrite.ao_channels.add_ao_voltage_chan('Dev1/ao1','mychannel',0,3.6)
        self.taskRead.ai_channels.add_ai_voltage_chan("Dev1/ai2",terminal_config=constants.TerminalConfiguration.RSE)
        self.taskRead.ai_channels.add_ai_voltage_chan("Dev1/ai3",terminal_config=constants.TerminalConfiguration.RSE)
        self.taskRead.ai_channels.add_ai_voltage_chan("Dev1/ai4",terminal_config=constants.TerminalConfiguration.RSE)
        self.taskRead.ai_channels.add_ai_voltage_chan("Dev1/ai16",terminal_config=constants.TerminalConfiguration.DEFAULT)
        self.taskRead.ai_channels.add_ai_voltage_chan("Dev1/ai17",terminal_config=constants.TerminalConfiguration.DEFAULT)
        self.taskRead.ai_channels.add_ai_voltage_chan("Dev1/ai18",terminal_config=constants.TerminalConfiguration.DEFAULT)
        self.taskRead.ai_channels.add_ai_voltage_chan("Dev1/ai19",terminal_config=constants.TerminalConfiguration.DEFAULT)
        self.taskRead.ai_channels.add_ai_voltage_chan("Dev1/ai20",terminal_config=constants.TerminalConfiguration.DEFAULT)
        self.taskRead.ai_channels.add_ai_voltage_chan("Dev1/ai21",terminal_config=constants.TerminalConfiguration.DEFAULT)
        self.taskRead.timing.cfg_samp_clk_timing(10000, sample_mode=constants.AcquisitionType.CONTINUOUS)
        self.taskRead.start()
        self.taskWrite.start()

        data_cal = np.array(np.transpose(self.taskRead.read(100)))
        force_raw_cal = data_cal[:,3:]
        self.forceBias = np.transpose(np.matmul(self.Gain, np.transpose(force_raw_cal)))
        self.forceBias = np.average(self.forceBias,axis=0)

    #Write data function
    def daqWrite(self,value):
        self.taskWrite.write(value)
    
    def forceRead(self):
        Data = np.take(self.taskRead.read(),[3,4,5,6,7,8])
        forceData = np.matmul(self.Gain,(np.transpose(Data)))
        forceData1 = [ round(elem, 2) for elem in forceData ] - self.forceBias
        return forceData1

    def run(self):
        global normalForce
        while self.f_record:
            data = np.array(np.transpose(self.taskRead.read(self.samples)))
            imu_data = data[:,:3]
            force_raw_data = data[:,3:]
            force_data = np.transpose(np.matmul(self.Gain, np.transpose(force_raw_data))) - self.forceBias
            normalForce = np.take(np.average(force_data,axis=0),[2])
            combined_array = np.concatenate((imu_data, force_data), axis =1)
            # print (np.take(np.average(force_data,axis=0),[2]))
            if np.take(np.average(force_data,axis=0),[2]) < -0.02:
                with open("./Texture rendering/Output/"+str(self.filename)+".csv", "ab") as f:
                # with open("./Texture rendering/Output/"+"Sine_test_125"+".csv", "ab") as f:
                    np.savetxt(f, combined_array, delimiter=',')
                    # np.savetxt(f, forceZdata)

    #Daq stop
    def DaqStop(self):
        self.f_record = False
        self.taskRead.stop()
        self.taskRead.close()
        self.taskWrite.stop()
        self.taskWrite.close()


def gameWindow(texName, texture, Gain1, Gain2, terminate, show_img=True):
    pygame.init() # initializing the constructor
  
    # screen main window resolution
    mainRes = (1024,600) 
    clock = pygame.time.Clock()  # intializing clock
    window = pygame.display.set_mode(mainRes)

    renderFlag = True

    if show_img:
        img = pygame.image.load("./Texture_images/"+str(texName)+".tif").convert()
    else:
        img = pygame.image.load("./Texture_images/notexture.png")
    img = pygame.transform.scale(img, (600,600))

    run = True
    while run and not terminate.is_set():
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # forceRead.DaqStop()
                # texRend.DaqStop()
                run = False

        window.fill((0, 0, 0))
        if renderFlag == True:
            # texRend = daqMxWrite(texture,Gain1,Gain2)
            # texRend.init()
            # texRend.start()
            renderFlag = False

        window.blit(img, (200,0))
        pygame.display.flip()
    
    #print('Texture rendering has shut down gracefully.')
    pygame.quit()


if __name__ == '__main__':                                  
    pass
