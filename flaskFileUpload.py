from flask import Flask, render_template, request,jsonify
from werkzeug.utils import secure_filename
from websocket import create_connection
import requests
import json
from types import SimpleNamespace
from multiprocessing import Pool
from datetime import datetime
import concurrent.futures
import random
import time


headers = {
    'authority': 'sync.free4talk.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '^\\^Google',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    'content-type': 'text/plain;charset=UTF-8',
    'accept': '*/*',
    'origin': 'https://www.free4talk.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.free4talk.com/',
    'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
}

params = (
    ('a', 'sync-get-free4talk-groups'),
)

data = ''


token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjM0MjQ0NzE1MDgiLCJuYW1lIjoiY2luIiwiZW1haWwiOiJzaGhocGxhdGZvcm1AZ21haWwuY29tIiwiYXZhdGFyIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EtL0FPaDE0R2dDTjVtZTVmVmtVdkthOVFzTklzMENRSm1UcW0xM193SkZHTy16Iiwib2lkIjoiMTExMTMxNzI3OTUwMzk2NTcxNTA4Iiwic3MiOiIzOTFkNTI0NjBmNTIxMTdiN2U2NGIyNDYzOTJiNTE0ZDo4OGZmMzE5OTVkZGZiN2RkMjI1YWQwMGZlOGU3ZjRlOGZkZjhlZTIwYzEwNzc0MmI4YjI4ZmJlYjQ2OGUxNmM5YTZhYjNiZWY3NTJkYjUxOTI0NmI0NjI4MGZjMTcwZjNjYmVjNWJiMjVkZTNmNTE1ZmQ3YzcxNDk3MTNlMjM1NmRlZDA0ODY5NmM1NTFhZjdiODYwOTVhOTU3MGI3NTg2NmY2OTEzZjA4YjE3ZDM5YmNhYWUwNGEyOGE4ZGQyNWNhZTFmZTI4OTRjZTY1Mzg0OTllOTNkNTIxYWQ0MTgyNGJkZDVlZTRhZTc4ZWE5NDY1NTkwYTQ0YmM5ZGNkODA4MmEyODYxMjJhYTBlY2ZiZjE2ZDdjMDZhOGVjYTk3NzEiLCJzc3ZlciI6MSwiaWF0IjoxNjE4NzQ1Nzc4LCJleHAiOjE2MTkzNTA1Nzh9.ZF_wocrQ5iVwL84SzItyXMw8IpWzzyj1XFeoWUD76Q0'

def createRandStr():
    randStr="z"+str(random.randint(1,9))+"CsD"+str(random.randint(1,9))+"qWr"
    #print(randStr)
    return randStr

def createJoinId():
    return str(random.randint(10000000,99999999))

def leaveAndUnregister(ws,roomid,pid):
    ws.send('{"e":"room:leave","d":{"rid":"'+roomid+'"}}')
    ws.send('{"e":"room:transporter:unregister","d":{"peerId":"OlPCG9ae:'+pid+'"}}')

ListofKeys=[]

def sendWithWs(roomId):
	pid=createRandStr()
	ws = create_connection("wss://free4talk-ws.herokuapp.com/ws/ws?pathname=/room/"+roomId)
    
	ws.send('{"e":"subscribe","d":{"name":"users","token":"'+token+'"}}')
	ws.recv()
	ws.send('{"e":"room:transporter:register","d":{"peerId":"UyNtZrgN:'+pid+'"}}')
	ws.send('{"e":"room:join","d":{"joinId":"0.36977999'+createJoinId()+'","rid":"'+roomId+'","pid":"UyNtZrgN:'+pid+'","token":"'+token+'"}}')
	ws.send('{"p":"0.247831099'+createJoinId()+'","e":"room:config"}')
	ws.send('{"p":"0.97924181'+createJoinId()+'","e":"room:settings","d":{"rid":"'+roomId+'"}}')
	y = json.loads(ws.recv())
	try:
		a={}
		a["UserID"]=y["d"]["resolve"]["settings"]["group"]["userId"]
		a["Key"]=y["d"]["resolve"]["settings"]["group"]["key"]
		a["Url"]="http://www.free4talk.com/room/"+roomId+"?key="+a["Key"]
		ListofKeys.append(a)
		print(a)
		return a
	except Exception as e:
		print("Not found!")
		return "Not Found"
	#leaveAndUnregister(ws,roomId,pid)
	ws.close()

def scan():
	try:
		response = requests.post('https://sync.free4talk.com/sync/get/free4talk/groups/', headers=headers, params=params, data=data)

		x = json.loads(response.content)
 
		dt = [x["data"][i]["url"].split("/")[-1] for i in x["data"] ]

		print("now =", datetime.now().time())
		with concurrent.futures.ThreadPoolExecutor(max_workers=200) as pool:
			respList = pool.map(sendWithWs, dt)
              	
		print("now =", datetime.now().time())
		print("----------------------")

	except Exception as e:
		print("Exception")

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/upload')
def upload_file1():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save("uploadedFiles/"+secure_filename(f.filename))
      return 'file uploaded successfully'

@app.route('/keys')
def keyServices():
   scan()

   return jsonify(ListofKeys)

		
if __name__ == '__main__':
   app.run(debug = True,host= '0.0.0.0',port=5050)