
import pyaudio
import wave
import base64
import json
import threading
import time
import scipy.io as sio
import scipy.io.wavfile
import numpy as np
import matplotlib.pyplot as plt
from sttapi import SttApi

# 설정
WAVE_OUTPUT_FILENAME = "output.wav"
CHUNK = 1024
#bit
FORMAT = pyaudio.paInt16
CHANNELS = 1
#두 개 다 같은 음성으로 저장된다!
RATE = 16000
RECORD_SECONDS = 30
#30초 지나면 알아서 끊ㄱㅣ는 파라미터

KEYWORD = '안녕|하세' # 예) 안녕|하세

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Start to record the audio.")

# init
stt = SttApi.create(RATE, CHUNK, RECORD_SECONDS)

# prepare
sttId = stt.prepare(KEYWORD)

thdSend = threading.Thread(target=stt.sendBody, args=(sttId, stream))
thdSend.start()

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    stt.setData(data)
    if not(stt.STT_STATUS == 'P01' or stt.STT_STATUS == 'P02'):
        break

print("Recording is finished.")

stream.stop_stream()
stream.close()
p.terminate()

while(stt.STT_STATUS == 'P01' or stt.STT_STATUS == 'P02'):
    print('')
# finish
res = stt.finish(sttId)
print('==============================result==============================')
print(res.json())
print('==============================result==============================')

# save audio
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(stt.getData()))
wf.close()

# graph
rate, data = sio.wavfile.read(WAVE_OUTPUT_FILENAME)
size = len(data)
times = np.arange(size)/float( rate)

print ('sample_size: ', size)
print ('shape of data: ', data.shape )
print ('sample_rate: ', rate)
print ('play time : : ', times[-1] )

plt.plot(times, data)
plt.xlim(times[0], times[-1])

plt.xlabel('time (s)')
plt.ylabel('amplitude')
plt.show()