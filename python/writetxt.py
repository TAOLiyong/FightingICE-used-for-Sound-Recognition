import numpy as np
import os
import time

myAction=['CROUCH_FB', 'AIR_FB', 'AIR_DB', 'CROUCH_FB', 'CROUCH_FB', 'AIR_B', 'AIR_DB', 'CROUCH_FB', 'CROUCH_FB', 'CROUCH_FB', 'CROUCH_FB', 'CROUCH_FB', 'CROUCH_FB', 'CROUCH_A', 'CROUCH_FB', 'CROUCH_FB', 'CROUCH_FB', 'AIR_B', 'AIR_B', 'STAND_F_D_DFA', 'STAND_F_D_DFA', 'AIR_D_DB_BB', 'STAND_FB', 'STAND_F_D_DFA', 'CROUCH_FB', 'STAND_FB', 'STAND_FB', 'STAND_FB', 'AIR_B', 'AIR_B', 'AIR_DB', 'CROUCH_FB', 'AIR_B', 'CROUCH_B', 'STAND_F_D_DFB', 'AIR_B', 'AIR_B', 'CROUCH_B', 'STAND_F_D_DFB', 'AIR_B', 'AIR_FB', 'STAND_FB', 'STAND_F_D_DFA', 'AIR_D_DB_BB', 'CROUCH_A', 'AIR_DA', 'AIR_D_DB_BB', 'CROUCH_A', 'STAND_F_D_DFB', 'AIR_B', 'AIR_F_D_DFB']
myX=[240, 240, 233, 173, 143, 20, 20, 20, 20, 20, 20, 20, 20, 23, 23, 23, 23, 20, 43, 265, 336, 297, 87, 72, 111, 56, 56, 56, 81, 81, 81, 81, 81, 81, 81, 197, 207, 228, 228, 213, 284, 284, 284, 473, 272, 287, 422, 214, 214, 199, 207]
myY=[537, 557, 537, 435, 452, 557, 537, 557, 557, 557, 557, 557, 557, 537, 557, 557, 557, 557, 537, 537, 537, 537, 587, 537, 537, 557, 557, 557, 537, 537, 537, 557, 557, 537, 557, 537, 537, 537, 557, 537, 537, 537, 537, 537, 587, 557, 537, 587, 557, 537, 537]
oppX=[720, 311, 291, 421, 441, 77, 85, 130, 130, 256, 256, 327, 327, 117, 234, 217, 315, 20, 20, 39, 114, 66, 557, 662, 372, 367, 367, 355, 20, 20, 20, 20, 30, 20, 20, 154, 164, 167, 122, 155, 185, 47, 20, 360, 229, 214, 214, 170, 165, 130, 143]
oppY=[537, 537, 525, 525, 537, 537, 523, 537, 537, 537, 537, 537, 537, 587, 537, 537, 537, 457, 537, 557, 537, 537, 378, 537, 421, 537, 537, 494, 273, 312, 523, 537, 537, 525, 537, 447, 480, 523, 537, 447, 557, 284, 537, 486, 537, 557, 557, 537, 557, 447, 523]
audio_data=[]
for i in range(51):
    audio_data.append(2*np.random.random((800,2))-1)

folderName=time.strftime("%Y%m%d%H%M%S", time.localtime())
filePath=os.getcwd()+"\\dataset\\"+folderName+"\\"
if not os.path.exists(filePath):     #判断当前路径是否存在，没有则创建new文件夹
    os.makedirs(filePath)

mapped=zip(myAction,myX,myY,oppX,oppY,audio_data)
for name in mapped:
    wavePath=filePath+name[0]+","+str(name[1])+","+str(name[2])+","+str(name[3])+","+str(name[4])+".txt"
    np.savetxt(wavePath,name[5],fmt='%f',delimiter=',')