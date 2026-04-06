<p align="center">
  <img width="923" height="284" src="https://github.com/user-attachments/assets/2f31aaf0-5589-48ce-bbbc-8e75407c4956" />
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)
![OS](https://img.shields.io/badge/OS-Linux-orange.svg)

🔥 Evillcode - Modular MITM Framework

Framework modular de ciberseguridad desarrollado en Python para el análisis, monitoreo y simulación de ataques MITM en redes locales.
Permite a estudiantes y profesionales comprender el funcionamiento interno de redes, protocolos y vulnerabilidades en entornos controlados.

📌 Descripción
Evillcode es un framework modular que permite:

* Escaneo de red y descubrimiento de dispositivos activos
* Identificación de direcciones IP, MAC y hostname
* Monitoreo continuo de la red
* Simulación de ataques MITM (Man-In-The-Middle)
* Captura de tráfico HTTP en busca de credenciales (entornos controlados)

Diseñado con un enfoque práctico para aprendizaje en ciberseguridad y redes.


## 🧩 Módulos del framework

- 🔍 Scanner: Descubrimiento de dispositivos en la red
- 🧠 Resolver: Identificación de hostname y MAC
- ⚡ MITM Engine: Suplantación ARP
- 📥 Sniffer: Captura de tráfico HTTP
- 📊 Monitor: Detección de nuevos dispositivos

⚠️ Nota

* Se recomienda ejecutar en sistemas Linux (Kali Linux, Ubuntu).
* Es necesario tener permisos de superusuario (root).
* Asegúrate de tener conexión a internet para instalar dependencias.

Herramientas necesarias

* nmap
* iptables
* python3
* pip

📦 Instalación

Sigue estos pasos para instalar y ejecutar el proyecto correctamente:

🔹 1. Clonar el repositorio

* git clone https://github.com/AlexanderOrtizScript/evillcode.git

* cd evillcode

🔹 2. Instalar dependencias de Python

⚡ Opción rápida (Kali / Ubuntu)

* sudo pip3 install -r requirements.txt --break-system-packages

🧠 Opción recomendada (entorno virtual)

* sudo apt install python3-venv -y

* python3 -m venv venv

* source venv/bin/activate

* pip install -r requirements.txt

⚠️ Nota

En algunas distribuciones Linux (como Kali Linux), la instalación global con pip está restringida.

Por eso se usa --break-system-packages o un entorno virtual.

🔹 3. Instalar herramientas del sistema

* sudo apt update

* sudo apt install -y nmap python3-pip


🔹 4. Ejecutar el programa

* sudo python3 evillcode.py

🚀 Uso

Ejecuta el script con permisos de administrador:

bash

sudo python3 evillcode.py

## 🔄 Flujo del sistema

🖥️ Seleccionar interfaz  
→ 🔍 Escaneo de red  
→ 🎯 Selección de objetivos  
→ ⚡ MITM + Sniffing  
→ 📡 Monitor en tiempo real

## 📁 Estructura del proyecto

## 📁 Estructura del proyecto

```
evillcode/
├── evillcode.py        # Script principal
├── requirements.txt    # Dependencias
├── README.md           # Documentación
├── LICENSE             # Licencia MIT
└── .gitignore          # Archivos ignorados por Git
```


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


