from flask import Flask, request, jsonify, send_file
import os
import grpc
from concurrent import futures
import protocol_pb2
import protocol_pb2_grpc

UPLOAD_FOLDER = 'DATANODE/files'

# Inicializa aplicación Flask
app = Flask(__name__)

# Comunicación gRPC
class DataNodeService(protocol_pb2_grpc.DataNodeServiceServicer):
    def ReplicateChunk(self, request, context):
        # Lógica para replicar un chunk
        success = True  # Supongamos que la replicación fue exitosa
        return protocol_pb2.ReplicateChunkResponse(success=success)

    def ListFiles(self, request, context):
        # Lógica para listar los archivos
        file_names = ['archivo1.txt', 'archivo2.txt']  # Supongamos que estos son los nombres de los archivos
        return protocol_pb2.ListFilesResponse(file_names=file_names)

# Inicializar el servidor gRPC
#grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#protocol_pb2_grpc.add_DataNodeServiceServicer_to_server(DataNodeService(), grpc_server)
#grpc_server.add_insecure_port('[::]:50051')
#grpc_server.start()


# Función para enviar una solicitud ReplicateChunk a otro DataNode
def send_replicate_chunk_request(chunk_id, file, data_node_ip):
    channel = grpc.insecure_channel(f'http://127.0.0.1:50050')
    stub = protocol_pb2_grpc.DataNodeServiceStub(channel)

    chunk = file.read()

    request = protocol_pb2.ReplicateChunkRequest(
        chunk_id=chunk_id,
        chunk_content=chunk
    )
    print("F")
    response = stub.ReplicateChunk(request)
    print("G")
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

    #print("A")
    #send_replicate_chunk_request(chunk_id, file, 'localhost:50055')
    #print("B")
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/download_chunk', methods=['GET'])
def download_chunk():
    chunk_id = request.args.get('chunk_id')
    
    chunk = f"files/{chunk_id}" #Ruta al chunk que me piden

    return send_file(chunk, as_attachment=True)  #as_attachment forza la descarga como archivo adjunto

@app.route('/heart_beat', methods=['GET'])
def heart_beat():
    return {'status': 'DataNode is running'}, 200

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
