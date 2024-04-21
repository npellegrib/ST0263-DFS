import requests

def upload_chunk(file_path, chunk_id, server_url):
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(f"{server_url}/upload_chunk/{chunk_id}", files=files)
            if response.status_code == 200:
                print("File uploaded successfully")
            else:
                print("Error:", response.json())
    except Exception as e:
        print("Error:", e)

# Ejemplo de uso
file_path = 'C:/Users/ASUS/Pictures/Fotos_HV/Nuevo Documento de texto.txt'
chunk_id = 'n1'
server_url = 'http://localhost:5000'  # Cambiar según la dirección del servidor
upload_chunk(file_path, chunk_id, server_url)
