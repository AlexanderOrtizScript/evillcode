🔥 Evillcode - Modular MITM Framework

Herramienta avanzada de análisis de red desarrollada en Python, enfocada en la detección, monitoreo y manipulación controlada de tráfico dentro de redes locales con fines educativos y de auditoría.


📌 Descripción

Evillcode es un framework modular que permite:

* Escaneo de red y descubrimiento de dispositivos activos
* Identificación de direcciones IP, MAC y hostname
* Monitoreo continuo de la red
* Simulación de ataques MITM (Man-In-The-Middle)
* Captura de tráfico HTTP en busca de credenciales (entornos controlados)

Diseñado con un enfoque práctico para aprendizaje en ciberseguridad y redes.


⚙️ Características

🔍 Escaneo automático de red con nmap
📡 Detección dinámica de interfaces de red
🧠 Identificación de dispositivos en la red
⚡ Suplantación ARP (MITM)
📥 Captura de paquetes en tiempo real
📊 Monitor de nuevos dispositivos conectados
🧩 Arquitectura modular basada en hilos (threads)


🧱 Requisitos

Sistema

* Linux (recomendado: Kali Linux, Ubuntu)
* Permisos de superusuario (root)

Herramientas necesarias

* nmap
* iptables
* python3
* pip

📦 Instalación

Sigue estos pasos para instalar y ejecutar el proyecto correctamente:

🔹 1. Clonar el repositorio

git clone https://github.com/AlexanderOrtizScript/evillcode.git

cd evillcode


🔹 2. Instalar dependencias de Python

pip3 install -r requirements.txt


🔹 3. Instalar herramientas del sistema

sudo apt update

sudo apt install -y nmap python3-pip


🔹 4. Ejecutar el programa

sudo python3 evillcode.py

🚀 Uso

Ejecuta el script con permisos de administrador:

bash

sudo python3 evillcode.py

🧪 Flujo de uso

1. Seleccionar interfaz de red
2. Escanear la red
3. Visualizar dispositivos detectados
4. Seleccionar objetivo(s)
5. Iniciar monitoreo o ataque MITM


📌 Dependencias de Python

* colorama
* pyfiglet
* scapy


⚠️ Aviso Legal

Este proyecto ha sido desarrollado exclusivamente con fines educativos y de auditoría de seguridad.

El uso indebido de esta herramienta en redes sin autorización es ilegal y puede acarrear consecuencias legales.

El autor no se hace responsable por el uso incorrecto del software.


👨‍💻 Autor

Alexander Ortiz
GitHub: https://github.com/AlexanderOrtizScript


⭐ Contribuciones

Las contribuciones son bienvenidas.
Puedes hacer un fork del proyecto y enviar un pull request.


📄 Licencia

Este proyecto está bajo la licencia MIT (puedes cambiarla si lo deseas).


🚀 Estado del proyecto

🟢 En desarrollo activo
Versión actual: 1.0.0


