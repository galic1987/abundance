from __future__ import absolute_import
from __future__ import print_function
from objc_util import *
import os
import time
import wave,array
import math
import numpy as np
import numpy.fft
import scene
from six.moves import range
import binascii
import pdb,sys
from rgbxy import Converter
#sys.setrecursionlimit(11000)
from phue import Bridge

b = Bridge('192.168.0.251')
b.connect() 
#pdb.set_trace()
# 2,8,9 my room 
# 1,3,4,5 living room 

'''
Root Chakra (Red Color)
Sacral Chakra (Orange Color)
Solar Plexus Chakra (Yellow Color)
Heart Chakra (Green Color)
Throat Chakra (Blue Color)
Third Eye Chakra (Indigo Color)
The Crown Chakra (Violet Color)
'''





class ChakraObject(object):
	def __init__(self,name,frequence,color):
		converter = Converter()
		self.name = name
		self.frequence = frequence
		self.color = converter.hex_to_xy(color)
		
		
class ChakraLightsCenter(object):
	def __init__(self,chakraobjects,huebridge):
		self.chakraobjects = chakraobjects
		self.huebridge = huebridge
		self.lastfreq = 0
		self.lastfreqamp = 0
		#expand with previous states
		
	def updateLigths(self,data):
		data4 = np.fft.fft(data[0:16000]*np.hanning(16000),16000)
		idx2 = np.argmax(np.abs(data4))
		#print(idx2)
		freq = data4[idx2]
		lamps = [1,3,4,5]
		freq_in_hertz = abs(freq)
		ind = np.argpartition(data4, -5)[-5:]
		
		
		
		print(abs(data4[167]))
		
		ampl = min( int((abs(data4[167])/1000)*255),255)
		#print(ampl)
		b.set_light(lamps,'bri',ampl)
		
		#scan 5 top frequencies 
		for top_freq in ind:
			#scan all the chakras 
			for chakrastate in self.chakraobjects:
				if abs(top_freq - chakrastate.frequence) < 1:
					#print(abs(top_freq - chakrastate.frequence))
					print(abs(data4[top_freq]))
					b.set_light(lamps,'xy',chakrastate.color)
					
		
		#print(ind)	
		#print(data4[ind])
		# color switch 
		'''
		if idx2 == 221:
			b.set_light([6,7], 'hue', 15000)
		if idx2 == 194:
			b.set_light([6,7], 'hue', 45000)		
		'''
		#print(str(idx2) + " - " + str(freq_in_hertz))
		#update logic here - iterate the array and check if peaks are there 
		return 0
		
		
chakraObjects = []

'''
chakraObjects.append(ChakraObject("Root",194.18,"ff0000"))
chakraObjects.append(ChakraObject("Sacral",210.42,"ffa500"))
chakraObjects.append(ChakraObject("Solar Plexus",126.22,"ffff00"))
chakraObjects.append(ChakraObject("Heart",136.10,"008000"))
chakraObjects.append(ChakraObject("Throat",141.27,"0000ff"))
chakraObjects.append(ChakraObject("3rd eye",221.23,"4b0082"))
chakraObjects.append(ChakraObject("Crown",172.06,"ee82ee"))
'''
chakraObjects.append(ChakraObject("7",248,"ff0000"))
chakraObjects.append(ChakraObject("2",296,"ffa500"))
chakraObjects.append(ChakraObject("1",264,"ffff00"))
chakraObjects.append(ChakraObject("3",331,"008000"))
chakraObjects.append(ChakraObject("5",396,"0000ff"))
chakraObjects.append(ChakraObject("7",495,"4b0082"))
chakraObjects.append(ChakraObject("6.",221,"ee82ee"))

chakraObjects.append(ChakraObject("1.",525,"808000"))
chakraObjects.append(ChakraObject("6",441,"FA8072"))
chakraObjects.append(ChakraObject("4",350,"008080"))
chakraObjects.append(ChakraObject("5",196,"000080"))

#b.set_light([6,7],'xy',self.color)
chakra = ChakraLightsCenter(chakraObjects,b)
	

# Some helper methods: 
AVAudioSession = ObjCClass('AVAudioSession')
class AVAudioSessionWrapper(object):
	def __init__(self,sample_rate=16000.0):
		shared_session = AVAudioSession.sharedInstance()
		category_set = shared_session.setCategory_error_('AVAudioSessionCategoryPlayAndRecord', None)
		kAudioFormat = int(binascii.b2a_hex(b'lpcm'),16)
		settings={'AVFormatIDKey':kAudioFormat,
		'AVSampleRateKey':sample_rate,
		'AVNumberOfChannelsKey':1}
		
		self.settings=settings
		self.shared_session=shared_session
		self.category_set=category_set
		
class AVAudioRecorderWrapper(object):
	def __init__(self,idx=1):
		sess=AVAudioSessionWrapper()
		self.output_path = os.path.abspath('recorder{}.wav'.format(idx))
		self.out_url = nsurl(self.output_path)
		#self.recorder1 = ObjCClass('AVAudioRecorder').alloc()
		self.recorder=ObjCClass('AVAudioRecorder').alloc().initWithURL_settings_error_(self.out_url, sess.settings, None)
		#self.recorder = AVAudioRecorder.alloc().initWithURL_settings_error_(self.out_url, sess.settings, None)
		self.record()
		self.stop()
	def record(self):
		self.recorder.record()
	def stop(self):
		self.recorder.stop()
	def data(self):
		try:
			wf=wave.open(self.output_path)
			N=wf.readframes(wf.getnframes())
			#print()			
			y=array.array('h',N)
			wf.close()
			#pdb.set_trace()
		except IOError:
			y=array.array('h',[])
		#os.remove(output_path)
		aa = np.double(y)/2**15
		#print(aa)
		'''
		freq = np.fft.fftfreq(self.data())
		for i in freq:
			print(freq)
		
		w = np.log10(abs(np.fft.fft(self.data()[0:2*W]*np.hanning(W*2),int(W*2))))[0:int(W)]
		print(w)'''
		#freqs = np.fft.fftfreq(len(w))
		
		return np.double(y)/2**15
	def fft(self):
		try:
			#print(self.data()[0:2*W]*np.hanning(W*2))
			data2 = self.data()
			data3 = np.fft.fft(data2[0:2*W]*np.hanning(W*2),int(W*2))
			# color switch 
			chakra.updateLigths(data2)
			
			#print(data4)
			return -0.1+0.1*np.log10(abs(data3))[0:int(W)]
			
		except ValueError:
			return np.double([])
	def __del__(self):
		import os
		self.recorder.stop()
		self.recorder.release()
		self.recorder=None
		os.remove(self.output_path)
		
					
T=1 # recording length.  dont make too small, or recorder wont record.
Nr=4 
	 # number of recorders.  this defines frame update time:mthe frame update will be is T/(Nr-1), though this may be driven slower by other factors
r=[AVAudioRecorderWrapper(i) for i in range(Nr)]

Np=float(1001); # float..num points to plot on screen.. too high will lower frame rate
import ui
W,H=ui.get_screen_size()

if 1:

	#import sk
	from threading import Thread
	class Vis(scene.Scene):
		def __init__(self,dofft=False):
			self.v=[scene.SpriteNode() for x in range(int(Np))]
			self.fixed_time_step=False
			for i,sp in enumerate(self.v):
				sp.size=(1.5,1.5)
				sp.position=(float(i)/Np*W,H/2)
				sp.color=(1.0*i/Np,(1-1.0*i/Np),(0.5+i/2.0))
				self.add_child(sp)
			# first, start r[0]
			# then, 0.5 sec later, start r[1]
			# then, 0.5 sec later, start r[2], stop r[0]
			# read r[0], then start r[0], stop r[1]
			# basically, each frame we read/start one, and stop i+1
			self.a1=scene.Action.call(self.update_y)
			self.a2=scene.Action.wait(T/(Nr-1))
			self.a3=scene.Action.sequence([self.a1,self.a2])
			self.a4=scene.Action.repeat(self.a3,-1)
			n=scene.Node()
			n.name='n'
			self.add_child(n)
			n.run_action(self.a4)
			self.dofft=dofft
			self.idx=0
		def update_y(self):
			if self.dofft:
				y=r[self.idx%Nr].fft()
				#print("idx "+str(self.idx)+" NR" + str(Nr))
			else :
				y=r[self.idx%Nr].data()
			# start idx, stop idx+1
			r[self.idx%Nr].record()
			#stop recorder a few samples before im ready to read it
			lookaheadidx=self.idx+1+int(0.25//(T/(Nr-1)))
			r[lookaheadidx%Nr].stop()
			self.idx+=1
			
			if len(y)==0:
				return
				
			for i,n in enumerate(self.v):
				iy=int(i/Np*len(y))
				#print(iy)
				n.position=(i/Np*W,y[iy]*H+H/2)
		def did_stop(self):
			print('stopping')
			#raise Error() 
			self['n'][0].remove_all_actions()
			[rec.stop() for rec in r]
			ui.delay(cleanup,0.25)
			# the scene seems to crash when restarting, unless we raise an error here
			raise KeyboardInterrupt
			
			
	sc=Vis(dofft=True)
	#sc=Vis(dofft=False)
	sc.shows_fps=True
	sc.shows_node_count=True
	scene.run(sc)