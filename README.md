# Centro de Monitoreo CCTV - Edificio Malvinas Argentinas (UNAHUR)
**Integrantes:**
* Yesica Toloza
* Nair Amira Paz

Este proyecto es el Trabajo Práctico Integrador para la materia **Sistemas Operativos (2C 2026)** de la Universidad Nacional de Hurlingham. Consiste en un sistema de videovigilancia distribuido que simula la transmisión en tiempo real de dos perspectivas distintas del Edificio Malvinas Argentinas mediante **Sockets TCP Concurrentes**.

## 📁 Estructura del Proyecto

El repositorio debe contener los siguientes archivos en la misma carpeta para garantizar su portabilidad:

*   `servidor_monitoreo.py` -> Código del Centro de Monitoreo Central (Servidor).
*   `cliente_camara.py` -> Código unificado e interactivo de las terminales de CCTV (Cliente).
*   `malvinas_1.mp4` -> Grabación de la Cámara 1 (Perspectiva Izquierda - Acceso Principal).
*   `malvinas_2.mp4` -> Grabación de la Cámara 2 (Perspectiva Derecha - Área de Hall).
*   `README.md` -> Guía de uso e instrucciones del repositorio.

## 🛠️ Requisitos e Instalación

El sistema requiere dos librerías externas esenciales para procesar el flujo de video y reconstruir los fotogramas en el servidor. A continuación, se detalla la función de cada una y el comando específico para instalarlas por separado desde la terminal de comandos (PowerShell o CMD):

### 1. Librería OpenCV (`opencv-python`)
Se encarga del procesamiento de video en las terminales de las cámaras. Permite abrir los archivos multimedia del Edificio Malvinas Argentinas, extraer cada fotograma en tiempo real y codificar las imágenes en memoria RAM para poder enviarlas a través del socket de red.
*   **Comando de instalación individual:**
    ```bash
    python -m pip install opencv-python --user
    ```

### 2. Librería Pillow (`Pillow`)
Es la herramienta que utiliza el Centro de Monitoreo Central para la manipión de los mapas de bits. Permite que el servidor tome los bytes puros que ingresan desde la red TCP, interprete el formato gráfico y renderice las imágenes de forma correcta en los paneles de visualización.
*   **Comando de instalación individual:**
    ```bash
    python -m pip install Pillow --user
    ```

## 🚀 Instrucciones de Ejecución

Para simular el entorno concurrente en paralelo, abra tres ventanas de la terminal (PowerShell/CMD) y muévase dentro de la carpeta del proyecto utilizando el comando `cd`. Inicie los scripts en el siguiente orden estricto:

1. **Terminal 1 (Iniciar el Servidor):**
   ```bash
   python servidor_monitoreo.py
   ```
   *El servidor quedará en estado de escucha pasiva en el puerto 5005.*

2. **Terminal 2 (Iniciar Cámara 1):**
   ```bash
   python cliente_camara.py
   ```
   *Seleccione la opción `1` en el menú interactivo para transmitir la perspectiva del Acceso Principal.*

3. **Terminal 3 (Iniciar Cámara 2):**
   ```bash
   python cliente_camara.py
   ```
   *Seleccione la opción `2` en el menú interactivo para transmitir en paralelo la perspectiva del Hall.*

## ⚙️ Conceptos del Sistema Operativo Aplicados
*   **Concurrencia real:** Multiprocesamiento ligero mediante hilos de Kernel (`threading`).
*   **Llamadas al Sistema (SysCalls):** Uso de `socket()`, `bind()`, `listen()`, `accept()`, `sendall()` y `recv()`.
*   **Delimitación de Mensajes:** Protocolo de aplicación con cabecera fija de 4 bytes para evitar el solapamiento de bytes en TCP.
*   **Sincronización de Interfaz:** Mecanismo de IPC local mediante cola segura (`queue.Queue`) y exclusión mutua para evitar condiciones de carrera en el renderizado gráfico.
