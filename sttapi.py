import base64
import json
import threading
import requests
import time

class SttApi:

    def __init__(self, RATE, CHUNK, RECORD_SECONDS):
        self.host = 'https://t-stt.chunjaeai.com'
        self.STT_STATUS = 'P01' # P01 진행중, P02 첫음검출, P03 끝음검출
        self.RATE = RATE
        self.CHUNK = CHUNK
        self.RECORD_SECONDS = RECORD_SECONDS
        self.index = 0
     
        self.frames = []
    
    @staticmethod
    #클래스 생성 없이도, 데코레이터 스테틱 매서드를 통해
    #객체 생성없이 함수 사용이 가능.
    def create(RATE, CHUNK, RECORD_SECONDS):
        return SttApi(RATE, CHUNK, RECORD_SECONDS)

    def post(self, url, field_data) :
        headers = {'API-KEY-ID':'ACADEMY_SPEECH', 'API-KEY':'e8j8GPwcLqeijX1D', 'Content-Type':'application/json'}
        return requests.post(url, headers=headers, data=field_data)

    def setData(self, data):
        self.frames.append(data)

    def getData(self):
        return self.frames[0:self.index]

    def sendData(self, i, data):
        if (self.STT_STATUS == 'P01' or self.STT_STATUS == 'P02'):
            bdata = base64.b64encode(data).decode('utf8')

            field_data = json.dumps({'sttId':self.sttId,'dataIndex':i+1,'data':bdata})
            url = self.host + '/stt/sendData'
            res = self.post(url, field_data)

            jsonObject = json.loads(json.dumps(res.json()))
            self.STT_STATUS = jsonObject.get('analysisResult').get('progressCode')

            return res

    def sendBody(self, sttId, stream):
        self.sttId = sttId

        while(self.STT_STATUS == 'P01' or self.STT_STATUS == 'P02'):
            if(len(self.frames) > (self.index + 1)):
                self.sendData(self.index, self.frames[self.index])
                self.index = self.index + 1
            time.sleep(0.01)

    def prepare(self, keywordlist):
        field_data = json.dumps({'modelId':'1','useEpd':'1','codec':'1','midResult':'1','pitchResult':'1','keywordList':keywordlist})
        url = self.host + '/stt/prepare'
        res = self.post(url, field_data)
        jsonObject = json.loads(json.dumps(res.json()))
        sttId = jsonObject.get('sttId')
        print(res)
        return sttId

    def finish(self, sttId):
        field_data = json.dumps({'sttId':sttId})
        url = self.host + '/stt/finish'
        res = self.post(url, field_data)
        return res