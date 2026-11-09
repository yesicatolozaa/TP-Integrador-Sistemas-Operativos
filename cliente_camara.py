import socket
import time
import os
import cv2

HOST = '127.0.0.1'
PORT = 5005

def seleccionar_perspectiva():
    print("=== CONFIGURACIÓN DE CCTV - EDIFICIO MALVINAS ARGENTINAS (UNAHUR) ===")
    print("1. Iniciar transmisión: Perspectiva Derecha")
    print("2. Iniciar transmisión: Perspectiva Izquierda")
    
    while True:
        opcion = input("Seleccione el número de cámara a simular (1 o 2): ").strip()
        if opcion in ["1", "2"]:
            return f"malvinas_{opcion}.mp4", opcion
        print("[ADVERTENCIA] Opción inválida. Marque 1 o 2.")

def iniciar_camara():
    archivo_video, camara_id = seleccionar_perspectiva()
    
    if not os.path.exists(archivo_video):
        print(f"[ERROR] No se encuentra el archivo '{archivo_video}' en la carpeta del TP.")
        return

    print(f"[CÁMARA {camara_id}] Intentando enlazar con el Centro de Monitoreo...")
    
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            print(f"[CÁMARA {camara_id}] Conexión TCP establecida con éxito.")
            
            cap = cv2.VideoCapture(archivo_video)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    # Bucle continuo al terminar el video
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                # Comprimir frame nativo limpio a JPG
                success, encoded_image = cv2.imencode('.jpg', frame)
                if not success: 
                    continue
                    
                datos_bytes = encoded_image.tobytes()
                tamano_video = len(datos_bytes)
                
                # Enviar tamaño en 4 bytes + datos binarios puros
                sock.sendall(tamano_video.to_bytes(4, byteorder='big'))
                sock.sendall(datos_bytes)
                
                # Velocidad calibrada para empatar los hilos de la GUI
                time.sleep(0.04)
                
            cap.release()
        except (ConnectionRefusedError, ConnectionResetError):
            print(f"[CÁMARA {camara_id}] Servidor no disponible. Reintentando en 5 segundos...")
            time.sleep(5)

if __name__ == "__main__":
    try:
        iniciar_camara()
    except KeyboardInterrupt:
        print("\nTerminal de la cámara cerrada por el usuario. Liberando recursos...")
