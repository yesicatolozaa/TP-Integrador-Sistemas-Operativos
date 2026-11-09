import socket
import threading
import io
import queue
import tkinter as tk
import datetime
from PIL import Image, ImageTk, ImageDraw

HOST = '127.0.0.1'
PORT = 5005

class ServidorMonitoreoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Centro de Monitoreo - UNAHUR Seguridad")
        
        # Cola segura de mensajería entre hilos
        self.cola_imagenes = queue.Queue()
        
        # Diccionario para mapear cada dirección de red a un panel físico
        self.mapeo_camaras = {}
        
        # Crear marcos rígidos con tamaño fijo en PÍXELES (500x380)
        self.marco_cam1 = tk.Frame(root, width=500, height=380, bg="black")
        self.marco_cam1.pack(side=tk.LEFT, padx=20, pady=20)
        self.marco_cam1.pack_propagate(False)
        
        self.label_cam1 = tk.Label(self.marco_cam1, text="Cámara 1:\nEsperando conexión...", bg="black", fg="white", font=("Arial", 14))
        self.label_cam1.pack(expand=True, fill=tk.BOTH)
        
        self.marco_cam2 = tk.Frame(root, width=500, height=380, bg="black")
        self.marco_cam2.pack(side=tk.RIGHT, padx=20, pady=20)
        self.marco_cam2.pack_propagate(False)
        
        self.label_cam2 = tk.Label(self.marco_cam2, text="Cámara 2:\nEsperando conexión...", bg="black", fg="white", font=("Arial", 14))
        self.label_cam2.pack(expand=True, fill=tk.BOTH)
        
        # Iniciar hilo de red de fondo
        threading.Thread(target=self.iniciar_red, daemon=True).start()
        
        # Monitorear la cola de imágenes de forma continua
        self.procesar_cola()

    def iniciar_red(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"[SERVIDOR] Escuchando en el puerto {PORT}...")
        
        while True:
            socket_cliente, direccion = servidor.accept()
            direccion_str = f"{direccion[0]}:{direccion[1]}"
            
            valores_activos = list(self.mapeo_camaras.values())
            if "Cámara 1" not in valores_activos:
                id_ranura = "Cámara 1"
            elif "Cámara 2" not in valores_activos:
                id_ranura = "Cámara 2"
            else:
                id_ranura = "Cámara Extra"
                
            self.mapeo_camaras[direccion_str] = id_ranura
            threading.Thread(target=self.atender_camara, args=(socket_cliente, direccion_str, id_ranura), daemon=True).start()

    def atender_camara(self, socket_cliente, direccion_str, id_ranura):
        print(f"[{id_ranura}] Conectada desde {direccion_str}")
        contador_frames = 0 # Reemplaza el booleano para controlar la velocidad del parpadeo
        
        try:
            while True:
                bytes_tamano = socket_cliente.recv(4)
                if not bytes_tamano:
                    break
                
                tamano_imagen = int.from_bytes(bytes_tamano, byteorder='big')
                
                bytes_imagen = b""
                while len(bytes_imagen) < tamano_imagen:
                    paquete = socket_cliente.recv(tamano_imagen - len(bytes_imagen))
                    if not paquete:
                        raise ConnectionError()
                    bytes_imagen += paquete
                
                imagen_pil = Image.open(io.BytesIO(bytes_imagen))
                imagen_pil = imagen_pil.convert("RGB")
                imagen_pil = imagen_pil.resize((500, 380), Image.Resampling.LANCZOS)
                
                # EFECTO EN VIVO: Estampar reloj y punto de grabación ralentizado
                dibujo = ImageDraw.Draw(imagen_pil)
                contador_frames += 1
                
                # El estado cambia cada 15 fotogramas para ir un toque más lento
                if (contador_frames // 15) % 2 == 0:
                    dibujo.ellipse([20, 20, 35, 35], fill="red")
                    dibujo.text((45, 22), "REC 1080p", fill="red")
                else:
                    # En lugar de apagarse del todo, muestra "LIVE" en verde de forma estable
                    dibujo.text((25, 22), "LIVE", fill="green")
                
                ahora = datetime.datetime.now().strftime("%H:%M:%S")
                dibujo.text((20, 350), f"UNAHUR - {id_ranura} - {ahora}", fill="white")
                
                self.cola_imagenes.put((id_ranura, direccion_str, imagen_pil))
                
        except (ConnectionResetError, ConnectionError):
            print(f"[{id_ranura}] Conexión terminada.")
        finally:
            socket_cliente.close()
            if direccion_str in self.mapeo_camaras:
                del self.mapeo_camaras[direccion_str]
            self.cola_imagenes.put((id_ranura, direccion_str, "DESCONECTADO"))

    def procesar_cola(self):
        try:
            while True:
                id_ranura, direccion_str, datos = self.cola_imagenes.get_nowait()
                target_label = self.label_cam1 if id_ranura == "Cámara 1" else self.label_cam2
                
                if id_ranura == "Cámara Extra":
                    self.cola_imagenes.task_done()
                    continue
                
                if datos == "DESCONECTADO":
                    target_label.config(image="", text=f"{id_ranura}:\nEsperando conexión...")
                else:
                    imagen_tk = ImageTk.PhotoImage(datos)
                    target_label.config(image=imagen_tk, text="")
                    target_label.image = imagen_tk
                    
                self.cola_imagenes.task_done()
        except queue.Empty:
            pass
        
        self.root.after(30, self.procesar_cola)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServidorMonitoreoGUI(root)
    root.mainloop()
