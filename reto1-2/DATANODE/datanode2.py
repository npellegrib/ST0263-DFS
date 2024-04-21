from flask import Flask, request, jsonify, send_file
import grpc
from concurrent import futures
import protocol_pb2
import protocol_pb2_grpc

# Inicializa aplicación Flask
#app = Flask(__name__)

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
grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
protocol_pb2_grpc.add_DataNodeServiceServicer_to_server(DataNodeService(), grpc_server)
grpc_server.add_insecure_port('[::]:50050')
grpc_server.start()
grpc_server.wait_for_termination()



# Ejecutar la aplicación Flask
#if __name__ == '__main__':
#    app.run(debug=True, port=50050)
