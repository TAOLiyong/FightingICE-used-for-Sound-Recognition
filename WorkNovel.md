# 2022.11.10

问题：

1.双通道音频导出：getAudioData 的 raw_audio为（800,2）数据

解决方案：

先尝试把数据写入txt文件

```python
folderName=time.strftime("%Y%m%d%H%M", time.localtime())   
#get the local time as folder name
filePath=os.getcwd()+'\\dataset\\'+folderName+'\\'
	if not os.path.exists(filePath):    #create folder is not exist
    	os.makedirs(filePath)
        
mapped=zip(self.myAction,self.myX,self.myY,self.oppX,self.oppY,self.audio_data)
	
    for name in mapped:
        wavePath=filePath+name[0]+","+str(name[1])+","+str(name[2])+","+str(name[3])+...
        ...","+str(name[4])+".txt"
        file=open(wavePath,'w')
        file.write(str(name[5]))
        file.close()
```

出现新的问题：

​	音频变为str存进txt时太长导致中间内容被省略，且内容全为0

​	~~原因猜测：1：np.array和list 进行zip 操作后失真 （代码验证，zip不会改变zip前的数据类型）~~

​						~~2：append()导致 （代码验证，append()也不会改变数据类型，使用了普通np.array生成float）~~

​	~~但是，在分别print self.audio_data 和zip之后的数据发现，self.audio_data中是float32的array数据,有数据，但是self.audio_data[*]和zip中的数据却都为零~~

问题原因：processing时间过长，导致获取的动作和坐标数据，跟声音数据的数量不一样，zip出现错误，只zip了数据为0的部分。

2.python中创建文件路径：wavewrite无法自动创建路径

解决方案：

```python
import os
def txt(name,text):              #定义函数名
    b = os.getcwd()[:-4] + 'new\\'
    #os.getcwd()可以查看py文件所在路径；
	#在os.getcwd()后边 加上 [:-4] + 'xxoo\\' 就可以在py文件所在路径下创建 xxoo文件夹
	if not os.path.exists(b):     #判断当前路径是否存在，没有则创建new文件夹
    	os.makedirs(b)
 
	xxoo = b + name + '.txt'    #在当前py文件所在路径下的new文件中创建txt
 
	file = open(xxoo,'w')
	 
	file.write(text)        #写入内容信息
 
	file.close()
	print ('ok')
txt('test','hello,python')       #创建名称为test的txt文件，内容为hello,python
```



3.有时候出现某个数据多一个的情况

![worknote1](C:\FightingICE-master\worknote1.png)



4.列表长度和保存的数据长度不一样

![worknote2](C:\FightingICE-master\worknote2.png)

5.莫名报错，偶尔在游戏结束时出现

![worknote3](C:\FightingICE-master\worknote3.png)

6.尝试将全部获取的rawAudio导出，分别将左右声道提取为wav（还不会同时提取为wav）听了一下感觉怪怪的，有大量失真
