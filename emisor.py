#!/usr/bin/env python3
"""
Emisor - Arquitectura de Capas con Detección y Corrección de Errores
Universidad del Valle de Guatemala - CC3067 Redes
"""
import socket
import random
import sys
import time
from crc32Emisor import calculate_crc32

# Importamos la función hammingSender desde hammingEmisor.js usando subprocess
# ya que está implementada en JavaScript
import subprocess
import json


class AplicacionLayer:
    """Capa de Aplicación - Solicitar mensaje y algoritmo"""
    
    def solicitar_mensaje(self):
        """Solicita el mensaje a enviar y el algoritmo a utilizar"""
        print("\n----- CAPA DE APLICACIÓN: SOLICITAR MENSAJE -----")
        mensaje = input("Ingrese el mensaje a enviar: ")
        
        print("\nAlgoritmos disponibles:")
        print("1. CRC-32 (Detección)")
        print("2. Hamming (Corrección)")
        algoritmo = input("Seleccione el algoritmo (1 o 2): ")
        
        while algoritmo not in ["1", "2"]:
            print("Opción inválida.")
            algoritmo = input("Seleccione el algoritmo (1 o 2): ")
            
        tasa_error = input("Ingrese la tasa de error (ej: 0.01 para 1 error cada 100 bits): ")
        try:
            tasa_error = float(tasa_error)
            if tasa_error < 0 or tasa_error > 1:
                print("Tasa de error debe estar entre 0 y 1. Usando 0.01")
                tasa_error = 0.01
        except ValueError:
            print("Tasa de error inválida. Usando 0.01")
            tasa_error = 0.01
            
        ip_destino = input("Ingrese la IP de destino (default: 127.0.0.1): ") or "127.0.0.1"
        puerto = input("Ingrese el puerto (default: 8888): ") or "8888"
        try:
            puerto = int(puerto)
        except ValueError:
            print("Puerto inválido. Usando 8888")
            puerto = 8888
            
        return {
            "mensaje": mensaje,
            "algoritmo": "crc32" if algoritmo == "1" else "hamming",
            "tasa_error": tasa_error,
            "ip_destino": ip_destino,
            "puerto": puerto
        }
        
    def mostrar_mensaje(self, mensaje):
        """Muestra información sobre el mensaje enviado"""
        print("\n----- CAPA DE APLICACIÓN: MOSTRAR RESULTADO -----")
        print(f"Mensaje enviado: {mensaje}")


class PresentacionLayer:
    """Capa de Presentación - Codificar mensaje"""
    
    def codificar_mensaje(self, mensaje):
        """Codifica el mensaje en ASCII binario"""
        print("\n----- CAPA DE PRESENTACIÓN: CODIFICAR MENSAJE -----")
        resultado = ""
        
        for char in mensaje:
            # Convertir cada carácter a su código ASCII y luego a binario (8 bits)
            ascii_binario = format(ord(char), '08b')
            resultado += ascii_binario
            print(f"Carácter: '{char}' -> ASCII: {ord(char)} -> Binario: {ascii_binario}")
            
        print(f"Mensaje codificado: {resultado}")
        print(f"Longitud en bits: {len(resultado)}")
        return resultado
        
    def decodificar_mensaje(self, binario):
        """Decodifica el mensaje de ASCII binario a texto"""
        print("\n----- CAPA DE PRESENTACIÓN: DECODIFICAR MENSAJE -----")
        texto = ""
        
        # Procesar cada byte (8 bits)
        for i in range(0, len(binario), 8):
            byte = binario[i:i+8]
            if len(byte) == 8:
                caracter = chr(int(byte, 2))
                texto += caracter
                print(f"Binario: {byte} -> ASCII: {int(byte, 2)} -> Carácter: '{caracter}'")
        
        print(f"Mensaje decodificado: {texto}")
        return texto


class EnlaceLayer:
    """Capa de Enlace - Calcular y verificar integridad"""
    
    def calcular_integridad(self, mensaje_binario, algoritmo):
        """Calcula la información de integridad según el algoritmo elegido"""
        print(f"\n----- CAPA DE ENLACE: CALCULAR INTEGRIDAD ({algoritmo}) -----")
        
        if algoritmo == "crc32":
            # Usamos el algoritmo CRC-32
            mensaje_con_ceros = mensaje_binario + '0' * 32
            crc_value = calculate_crc32(mensaje_con_ceros)
            crc_bits = format(crc_value, '032b')
            
            mensaje_final = mensaje_binario + crc_bits
            print(f"CRC-32 calculado: {crc_bits}")
            print(f"Mensaje con CRC: {mensaje_final}")
            print(f"Longitud final: {len(mensaje_final)} bits")
            
            return mensaje_final
            
        elif algoritmo == "hamming":
            # Usamos el algoritmo de Hamming llamando al código JavaScript
            # Guardar mensaje binario en un archivo temporal
            with open("temp_mensaje.txt", "w") as f:
                f.write(mensaje_binario)
            
            # Llamar a hammingEmisor.js usando Node.js
            try:
                result = subprocess.run(
                    ["node", "-e", 
                     f"const {{ hammingSender }} = require('./hammingEmisor.js'); " +
                     f"const fs = require('fs'); " +
                     f"const mensaje = fs.readFileSync('temp_mensaje.txt', 'utf8'); " +
                     f"const resultado = hammingSender(mensaje); " + 
                     f"console.log(JSON.stringify({{ resultado: resultado }}));"],
                    capture_output=True, text=True, check=True
                )
                
                # Extraer resultado del JSON
                resultado_json = json.loads(result.stdout)
                mensaje_final = resultado_json["resultado"]
                
                print(f"Mensaje con Hamming: {mensaje_final}")
                print(f"Longitud final: {len(mensaje_final)} bits")
                
                return mensaje_final
                
            except subprocess.CalledProcessError as e:
                print(f"Error al llamar a hammingEmisor.js: {e}")
                print(f"Stdout: {e.stdout}")
                print(f"Stderr: {e.stderr}")
                return mensaje_binario
                
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {e}")
                return mensaje_binario
        
        return mensaje_binario


class RuidoLayer:
    """Simulador de ruido en el canal de transmisión"""
    
    def aplicar_ruido(self, mensaje, tasa_error):
        """Aplica ruido (flips de bits) según la tasa de error especificada"""
        print(f"\n----- CAPA DE RUIDO: APLICAR RUIDO (Tasa: {tasa_error}) -----")
        resultado = list(mensaje)
        bits_cambiados = 0
        
        for i in range(len(resultado)):
            # Generar número aleatorio entre 0 y 1
            if random.random() < tasa_error:
                # Aplicar flip al bit (cambiar 0 por 1 o viceversa)
                resultado[i] = '1' if resultado[i] == '0' else '0'
                bits_cambiados += 1
                print(f"Bit {i} cambiado: {mensaje[i]} -> {resultado[i]}")
        
        mensaje_con_ruido = ''.join(resultado)
        print(f"Total bits cambiados: {bits_cambiados} de {len(mensaje)}")
        print(f"Mensaje con ruido: {mensaje_con_ruido}")
        
        return mensaje_con_ruido


class TransmisionLayer:
    """Capa de Transmisión - Envío y recepción por sockets"""
    
    def enviar_informacion(self, mensaje, ip_destino, puerto):
        """Envía la trama a través de un socket TCP"""
        print(f"\n----- CAPA DE TRANSMISIÓN: ENVIAR INFORMACIÓN -----")
        print(f"Enviando a {ip_destino}:{puerto}")
        print(f"Longitud de la trama: {len(mensaje)} bits")
        
        try:
            # Crear socket TCP
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Conectar al receptor
                s.connect((ip_destino, puerto))
                
                # Enviar la trama
                s.sendall(mensaje.encode('utf-8'))
                print(f"Mensaje enviado exitosamente")
                
                # Esperar confirmación
                confirmacion = s.recv(1024).decode('utf-8')
                print(f"Confirmación recibida: {confirmacion}")
                
                return True
                
        except ConnectionRefusedError:
            print(f"Error: Conexión rechazada. Verifique que el receptor esté ejecutándose.")
        except Exception as e:
            print(f"Error al enviar: {e}")
            
        return False


def main():
    """Función principal para el emisor"""
    print("\n============= EMISOR - ARQUITECTURA DE CAPAS =============")
    
    aplicacion = AplicacionLayer()
    presentacion = PresentacionLayer()
    enlace = EnlaceLayer()
    ruido = RuidoLayer()
    transmision = TransmisionLayer()
    
    while True:
        try:
            # Solicitar mensaje y algoritmo (Aplicación)
            datos = aplicacion.solicitar_mensaje()
            
            if datos["mensaje"].lower() == "quit":
                print("Saliendo del emisor...")
                break
                
            # Codificar mensaje (Presentación)
            mensaje_binario = presentacion.codificar_mensaje(datos["mensaje"])
            
            # Calcular integridad (Enlace)
            mensaje_con_integridad = enlace.calcular_integridad(mensaje_binario, datos["algoritmo"])
            
            # Aplicar ruido (Simulador de ruido)
            mensaje_con_ruido = ruido.aplicar_ruido(mensaje_con_integridad, datos["tasa_error"])
            
            # Enviar información (Transmisión)
            transmision.enviar_informacion(mensaje_con_ruido, datos["ip_destino"], datos["puerto"])
            
            # Mostrar resultado (Aplicación)
            aplicacion.mostrar_mensaje(datos["mensaje"])
            
            print("\n" + "="*60)
            
        except KeyboardInterrupt:
            print("\nSaliendo del emisor...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
