from flask import Flask, request, jsonify, redirect, Response
import grpc
import threading
import time
import requests
import protocol_pb2
import protocol_pb2_grpc
import environs
from queue import PriorityQueue

app = Flask(__name__)

fileListed = {}

env = environs.Env()
env.read_env()

serverAddresses = env.list("DATANODES")

liveDataNodes= []

fileOrder = {}
# Se crea el heartbeat a otro NN
def checkHealth():
    otherServer = f"http://{env('NAME_NODE')}:8080/list"
    try: 
        response = requests.get(otherServer)
        if response.status_code != 200:
            return False
        else:
            return True
    except requests.RequestException:
        return False

def checkDataNode(address):
    response = f"http://{address}:5000/heart_beat"
    try:
        status= requests.get(response).status_code
        if status != 200:
            return False
        else:
            return True
        return True
    except:
        return False

def healthOfNetwork():
    for address in serverAddresses:
        if checkDataNode(address):
            liveDataNodes.append(address)
        else:
            if address in liveDataNodes:
                liveDataNodes.remove(address)
        time.sleep(20)



def failover():
    while True:
        if checkHealth():
            print("Name Node Health confirmed")
        else:
            interval = 60
            updateThread = threading.Thread(target = fileListUpdate, args = (interval, ))
            updateThread.setDaemon(True)
            updateThread.start()
        time.sleep(15)

def createStub(address):
    stub = grpc.insecure_channel(address+"1036")
    return protocol_pb2_grpc.DataNodeServiceStub(stub)

def fileList(address):
    try:
        stub = createStub(address)
        response = stub.ListFiles(protocol_pb2.ListFilesRequest)

        if response.fileNames:
            fileListed[address] = response.fileNames
            print(fileListed[address])
        else:
            fileListed[address] = []
    except grpc.RpcError as e:
        print(f"Error listing files from {address}: {e.details()}")

def fileListUpdate(timing):
    while True: 
        for address in liveDataNodes:
            fileList(address)
        time.sleep(timing)

@app.route("/list", methods=["GET"])
def listFiles():
    try:
        allFiles=[]

        for address in liveDataNodes:
            if address in fileListed:
                allFiles.extend(fileListed[address])
        
        if allFiles:
            return jsonify({"files":allFiles})
        else:
            return jsonify({"message":"Archivos no encontrados"})
    except Exception as e:
        return jsonify({"error":str(e)})

def getDNList2(chunks):
    pq = PriorityQueue()
    listasDeIPOrdenada = []
    for address in liveDataNodes:
        respuesta = fileListed[address]
        pq.put(len(respuesta), address)
    i=0
    while i < chunks:
        priority,address= pq.get()
        listasDeIPOrdenada[i] = address
        pq.put(priority+1, address)
        i+=1
    return listasDeIPOrdenada


def getDNList():
    listasDeDuplas = liveDataNodes
    i = 0
    for address in liveDataNodes:
        respuesta = fileListed[address]
        listasDeDuplas[i] = {len(respuesta), address}
        i += 1
    listasDeDuplas.sort()
    listasDeIPOrdenada = [x[1] for x in listasDeDuplas]
    return listasDeIPOrdenada

@app.route("/upload/<fileName>/<chunks>",methods=["GET"])
def upload(fileName,chunks):
    try:
        servers = getDNList2(chunks)
        fileOrder[fileName] = (servers,chunks)
        return jsonify({"DataNodes": servers})
    except Exception as e:
        return jsonify({"error": str(e)})

def getFileServer(fileName):
    return fileOrder[fileName]

@app.route('/archivo_info', methods=['GET'])
def archivo_info():

    if request.args:
        nombreArchivo = request.args.get('nombre')
        if nombreArchivo in fileOrder:

            address = getFileServer(nombreArchivo)
            serverOrder = address[0]
            chunkNumber = address[1]
            #url = "a"
            #respuesta = requests.get(url)
            return jsonify({"chunks":chunkNumber, "orden":serverOrder})
        else: 
            return jsonify({"error":"Archivo no existente"})
    else: 
        return jsonify({"error":"No se pidio ningun archivo"})





if __name__ == "__main__":
    # app.run(port=8080)
    # Se tira el monitoreo del otro servidor por si toca hacer failback
    monitorNameNodeThread = threading.Thread(target=failover)
    monitorNameNodeThread.daemon = True
    monitorNameNodeThread.start()

    monitorDataNodeThread = threading.Thread(target=healthOfNetwork)
    monitorDataNodeThread.daemon = True
    monitorDataNodeThread.start()
    # inicia app de flask
    app.run(host=env("SELF_IP"), port=8080, debug=True)


# hace keep alive de los DN, la aprioratizacion con la cantidad de archivos

