from py4j.java_gateway import get_field
import numpy as np
import time
import os

class KickAI(object):
    def __init__(self, gateway):
        self.gateway = gateway
        ##########################byTAO
        self.nonDelay=None
        self.ad=[]
        self.currentAd=None
        self.audio_data=[] 
        self.myAction=[]
        self.myX=[]
        self.myY=[]
        self.oppX=[]
        self.oppY=[]
        self.allSound=[]
        self.frameCount=0
        self.isRunning=False
        ##########################byTAO
        
    def close(self):
        pass
        
    def getInformation(self, frameData, isControl,nonDelay):
        # Getting the frame data of the current frame
        if self.isRunning:
            pass
        else:
            self.frameData = frameData
            self.cc.setFrameData(self.frameData, self.player)
            self.nonDelay=nonDelay

    # please define this method when you use FightingICE version 3.20 or later
    def roundEnd(self, x, y, z):
        #print("len of myAction:",len(self.myAction))
        print("len of myX:",len(self.myX))
        print("len of myY:",len(self.myY))
        print("len of oppX:",len(self.oppX))
        print("len of oppY:",len(self.oppY))
        print("len of audio_data:",len(self.audio_data), np.array(self.audio_data).shape)
        print("frameCount:",self.frameCount)
        
        if len(self.myX)==len(self.myY)==len(self.oppX)==len(self.oppY)==len(self.audio_data):
            folderName=time.strftime("%Y%m%d%H%M%S", time.localtime())   #get the local time as folder name
            filePath=os.getcwd()+'\\dataset\\'+folderName+'\\'
            if not os.path.exists(filePath):    #create folder is not exist
                os.makedirs(filePath)
            
            mapped=zip(self.myX,self.myY,self.oppX,self.oppY,self.audio_data)

            for name in mapped:
                #wavePath=filePath+name[0]+","+str(name[1])+","+str(name[2])+","+str(name[3])+","+str(name[4])+".wav"
                #wf.write_wave(wavePath, name[5])
                wavePath=filePath+str(name[0])+","+str(name[1])+","+str(name[2])+","+str(name[3])+time.strftime('%H%M%S')+".txt"
                #file=open(wavePath,'w')
                #file.write(str(name[5]))
                #file.close()
                if(sum(sum(name[4]))!=0):
                    np.savetxt(wavePath,name[4],fmt='%f',delimiter=',')
            np.savetxt(filePath+"allSound.txt",self.allSound,fmt='%f',delimiter=',')

        self.nonDelay=None
        self.audio_data=[]
        self.myAction=[]
        self.myX=[]
        self.myY=[]
        self.oppX=[]
        self.oppY=[]
        self.allSound=[]
        self.frameCount=0
    
    def getAudioData(self, audio_data):
        # process audio
        ##########################byTAO
        try:
            byte_data = audio_data.getRawDataAsBytes()
            np_array = np.frombuffer(byte_data, dtype=np.float32)
            raw_audio = np_array.reshape((2, 1024))
            raw_audio = raw_audio.T
            raw_audio = raw_audio[:800, :]
        except Exception as ex:
            raw_audio = np.zeros((800, 2))
		
        self.currentAd=raw_audio

        #self.ad.extend(raw_audio)
        self.allSound.extend(raw_audio)
        self.frameCount+=1

    # please define this method when you use FightingICE version 4.00 or later

    def getScreenData(self, sd):
        pass
        
    def initialize(self, gameData, player):
        # Initializng the command center, the simulator and some other things
        self.inputKey = self.gateway.jvm.struct.Key()
        self.frameData = self.gateway.jvm.struct.FrameData()
        self.cc = self.gateway.jvm.aiinterface.CommandCenter()
            
        self.player = player
        self.gameData = gameData
        self.simulator = self.gameData.getSimulator()
                
        return 0
        
    def input(self):
        # Return the input for the current frame
        return self.inputKey
        
    def processing(self):

        # Just compute the input for the current frame
        if self.frameData.getEmptyFlag() or self.frameData.getRemainingFramesNumber() <= 0:
                
                self.isRunning=False
                return
                
        if self.cc.getSkillFlag():
                self.inputKey = self.cc.getSkillKey()
                
                return

        
        self.audio_data.append(self.currentAd)

        self.inputKey.empty()
        self.cc.skillCancel()
        # Just spam kick
        self.cc.commandCall("B")

        my=self.nonDelay.getCharacter(self.player)
        opp=self.nonDelay.getCharacter(not self.player)
        self.myX.append(my.getCenterX())
        self.myY.append(my.getCenterY())
        self.oppX.append(opp.getCenterX())
        self.oppY.append(opp.getCenterY())
        
        #self.audio_data.append(self.ad)
        #self.ad=[]

        

        
                        
    # This part is mandatory
    class Java:
        implements = ["aiinterface.AIInterface"]
        
