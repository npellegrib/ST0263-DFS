import requests

def dividir_archivo_en_chunks(file_path, chunk_size=1024*1024):
    chunks = []
    with open(file_path, 'rb') as file:
        chunk = file.read(chunk_size)
        while chunk:
            chunks.append(chunk)
            chunk = file.read(chunk_size)
    return chunks

def obtener_datanodes_del_namenode(nombre_del_archivo, numero_de_chunks):
    """
    Consulta al NameNode para obtener los DataNodes disponibles
    basándose en el nombre del archivo y la cantidad de chunks.
    """
    response = requests.get(f'http://namenode:port/upload/{nombre_del_archivo}/{numero_de_chunks}')
    if response.status_code == 200:
        # Asume que la respuesta es una lista de diccionarios con 'ip', 'port' para cada chunk
        return response.json()
    else:
        print("Error al obtener la lista de DataNodes desde el NameNode.")
        return []

def distribuir_chunks_a_datanodes(nombre_del_archivo, chunks, datanodes):
    for i, (chunk, datanode) in enumerate(zip(chunks, datanodes)):
        chunk_filename = f"{nombre_del_archivo}{i+1}"  # Construye el nombre del chunk
        url = f"http://{datanode['ip']}:{datanode['port']}/upload_chunk/{chunk_filename}"
        
        # Asume que el servidor espera el contenido del chunk en el cuerpo de la solicitud,
        # y utiliza 'chunk_filename' para identificarlo en el servidor.
        response = requests.post(url, files={'file': (chunk_filename, chunk)})
        
        if response.status_code == 200:
            print(f"Chunk {i+1} ({chunk_filename}) enviado correctamente a {datanode['ip']}")
        else:
            print(f"Error al enviar el chunk {i+1} ({chunk_filename}) a {datanode['ip']}")

def obtener_informacion_de_chunks(nombre_del_archivo):
    """
    Realiza una solicitud al endpoint '/archivo_info' para obtener la lista de DataNodes
    y los identificadores de chunks para un archivo específico.
    """
    response = requests.get(f'http://namenode:port/archivo_info?nombre={nombre_del_archivo}')
    if response.status_code == 200:
        # Asume que la respuesta contiene información sobre los DataNodes y los identificadores de los chunks
        return response.json()
    else:
        print(f"Error al obtener información de los chunks para el archivo {nombre_del_archivo}.")
        return []

def descargar_chunks(chunks_info, datanode_base_url):
    """
    Descarga los chunks especificados desde los DataNodes.
    """
    chunks = []
    for info in chunks_info:
        chunk_id = info['chunk_id']
        # Actualiza la URL según cómo el DataNode espere recibir el identificador del chunk.
        url = f'{datanode_base_url}/download_chunk?chunk_id={chunk_id}'
        response = requests.get(url)
        if response.status_code == 200:
            chunks.append(response.content)
        else:
            print(f"Error al descargar el chunk {chunk_id}.")
    return chunks

def reconstruir_archivo(nombre_del_archivo, chunks):
    """
    Reconstruye el archivo original a partir de los chunks descargados.
    """
    with open(nombre_del_archivo, 'wb') as archivo_final:
        for chunk in chunks:
            archivo_final.write(chunk)
    print(f"Archivo {nombre_del_archivo} reconstruido exitosamente.")

def subir_archivo():
    file_path = input("Ingrese el camino al archivo para subir: ")
    nombre_del_archivo = input("Ingrese el nombre base para los chunks: ")
    chunk_size = int(input("Ingrese el tamaño del chunk en bytes (ej. 1048576 para 1MB): "))
    chunks = dividir_archivo_en_chunks(file_path, chunk_size)
    datanodes = obtener_datanodes_del_namenode(nombre_del_archivo, len(chunks))
    print("Distribuyendo chunks...")
    distribuir_chunks_a_datanodes(nombre_del_archivo, chunks, datanodes)
    print("Chunks distribuidos exitosamente.")
    # Aquí iría la lógica para distribuir los chunks (se asume simulada en este ejemplo).

def descargar_archivo():
    nombre_del_archivo = input("Ingrese el nombre del archivo para descargar: ")
    chunks_info = obtener_informacion_de_chunks(nombre_del_archivo)
    datanode_base_url = input("Ingrese la URL base del DataNode (ej. http://datanode:port): ")
    chunks = descargar_chunks(chunks_info, datanode_base_url)
    reconstruir_archivo(nombre_del_archivo, chunks)

def main():
    print("1. Subir archivo")
    print("2. Descargar archivo")
    opcion = input("Seleccione una opción: ")
    if opcion == '1':
        subir_archivo()
    elif opcion == '2':
        descargar_archivo()
    else:
        print("Opción inválida.")

if __name__ == "__main__":
    main()
