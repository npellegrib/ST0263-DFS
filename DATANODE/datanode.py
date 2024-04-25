from flask import Flask, request, jsonify, send_file
import os
import grpc
from concurrent import futures
import threading
import protocol_pb2
import protocol_pb2_grpc
import time

UPLOAD_FOLDER = 'DATANODE/files'
HOST_DATANODE = '127.0.0.1'
PORT_GRPC = 1036
PORT_FLASK = 5000
HOST_REPLICATION = '127.0.0.1'
PORT_REPLICATION = 50050

# Inicializa aplicación Flask
app = Flask(__name__)

# Comunicación gRPC
class DataNodeService(protocol_pb2_grpc.DataNodeServiceServicer):
    def ReplicateChunk(self, request, context):
        chunk_id = request.chunk_id
        chunk_content = request.chunk_content
        file_path = os.path.join(UPLOAD_FOLDER, chunk_id)

        with open(file_path, "wb") as f:
            f.write(chunk_content)
        
        return protocol_pb2.ReplicateChunkResponse(success=True)

    def ListFiles(self, request, context):
        path_to_folder = os.path.join(os.path.dirname(__file__), 'files')

        #Envia un error si la carpeta files no existe
        if not os.path.isdir(path_to_folder):
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("La carpeta 'files' no existe")
            return protocol_pb2.ListFilesResponse()

        #Obtener la lista de archivos disponibles
        file_names = os.listdir(path_to_folder)

        return protocol_pb2.ListFilesResponse(file_names=file_names)

# Inicializar el servidor gRPC
def run_grpc_server():
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocol_pb2_grpc.add_DataNodeServiceServicer_to_server(DataNodeService(), grpc_server)
    grpc_server.add_insecure_port(f'{HOST_DATANODE}:{PORT_GRPC}')
    grpc_server.start()
    print("Servidor escuchando en el puerto")
    grpc_server.wait_for_termination()

# Función para enviar una solicitud ReplicateChunk a otro DataNode
def send_replicate_chunk_request(chunk_id, file, data_node_ip):
    channel = grpc.insecure_channel(data_node_ip)
    stub = protocol_pb2_grpc.DataNodeServiceStub(channel)
    chunk_content = file.read()
    request = protocol_pb2.ReplicateChunkRequest(chunk_id=chunk_id, chunk_content=chunk_content)
    response = stub.ReplicateChunk(request)
    print(f"DataNode{data_node_ip} recibió respuesta de replicación: {response.success}")


# Definir una ruta REST en Flask
@app.route('/upload_chunk/<chunk_id>', methods=['POST'])
def upload_chunk(chunk_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    file_content = file.read()
    file_path = os.path.join(UPLOAD_FOLDER, chunk_id)

    with open(file_path, "wb") as f:
        f.write(file_content)

    send_replicate_chunk_request(chunk_id, file, f'{HOST_REPLICATION}:{PORT_REPLICATION}')

    return jsonify({'message': 'File uploaded successfully'})

@app.route('/download_chunk', methods=['GET'])
def download_chunk():
    chunk_id = request.args.get('chunk_id')
    
    chunk = f"files/{chunk_id}" #Ruta al chunk que me piden

    return send_file(chunk, as_attachment=True)  #as_attachment forza la descarga como archivo adjunto

@app.route('/heart_beat', methods=['GET'])
def heart_beat():
    return {'status': 'DataNode is running'}, 200

# Ejecutar grpc en un hilo e iniciar flask
if __name__ == '__main__':
    grpc_thread = threading.Thread(target=run_grpc_server)
    grpc_thread.start()
    time.sleep(1) 
    app.run(host=HOST_DATANODE, port=PORT_FLASK, debug=True)
