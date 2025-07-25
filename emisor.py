#!/usr/bin/env python3
"""
Emisor con Arquitectura de Capas - Laboratorio 2 Segunda Parte
Universidad del Valle de Guatemala - CC3067 Redes
Implementa la arquitectura de capas para el emisor
"""

import random
import sys
import os

# Importar los algoritmos existentes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from crc32Emisor import crc32_sender, calculate_crc32

class CapaAplicacion:
    """Capa de Aplicación: Interacción con el usuario y manejo de mensajes"""
    
    def solicitar_mensaje(self):
        """Solicita un mensaje al usuario y lo retorna"""
        mensaje = input("Ingrese un mensaje para enviar: ")
        print(f"[APLICACIÓN] Mensaje ingresado: '{mensaje}'")
        return mensaje
        
    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje al usuario"""
        print(f"[APLICACIÓN] Mensaje recibido: '{mensaje}'")
        return mensaje

class CapaPresentacion:
    """Capa de Presentación: Codificación y decodificación de mensajes"""
    
    def codificar_mensaje(self, mensaje):
        """Codifica un mensaje de texto a binario"""
        # Convierte cada carácter a su representación binaria de 8 bits
        mensaje_binario = ''.join(format(ord(c), '08b') for c in mensaje)
        print(f"[PRESENTACIÓN] Mensaje codificado: {mensaje_binario}")
        return mensaje_binario
        
    def decodificar_mensaje(self, mensaje_binario):
        """Decodifica un mensaje binario a texto"""
        # Agrupa los bits en bytes (8 bits) y convierte cada grupo a un carácter
        mensaje = ""
        for i in range(0, len(mensaje_binario), 8):
            byte = mensaje_binario[i:i+8]
            if len(byte) == 8:  # Asegurarse de que tenemos 8 bits
                mensaje += chr(int(byte, 2))
        print(f"[PRESENTACIÓN] Mensaje decodificado: '{mensaje}'")
        return mensaje

class CapaEnlace:
    """Capa de Enlace: Manejo de integridad y corrección de errores"""
    
    def __init__(self, metodo_deteccion='crc32', metodo_correccion='hamming'):
        """
        Inicializa la capa de enlace con métodos de detección y corrección
        
        Args:
            metodo_deteccion: 'crc32' o 'fletcher'
            metodo_correccion: 'hamming' o 'none'
        """
        self.metodo_deteccion = metodo_deteccion
        self.metodo_correccion = metodo_correccion
        print(f"[ENLACE] Inicializado con detección: {metodo_deteccion}, corrección: {metodo_correccion}")
    
    def calcular_integridad(self, mensaje_binario):
        """Aplica el algoritmo de detección/corrección al mensaje"""
        print(f"[ENLACE] Calculando integridad con método {self.metodo_deteccion}")
        
        if self.metodo_deteccion == 'crc32':
            # Usar implementación CRC-32 existente
            mensaje_con_crc = crc32_sender(mensaje_binario)
            return mensaje_con_crc
        elif self.metodo_deteccion == 'hamming' and self.metodo_correccion == 'hamming':
            # Para usar Hamming como método de detección y corrección
            # Importar dinámicamente para evitar problemas de dependencias circulares
            try:
                # Intentar importar la versión JavaScript a través de una llamada externa
                import subprocess
                result = subprocess.run(['node', 'hammingEmisor.js', mensaje_binario], 
                                      capture_output=True, text=True)
                mensaje_con_hamming = result.stdout.strip()
                print(f"[ENLACE] Mensaje con Hamming: {mensaje_con_hamming}")
                return mensaje_con_hamming
            except Exception as e:
                print(f"[ENLACE] Error al usar Hamming: {e}")
                # Si falla, devolver el mensaje original
                return mensaje_binario
        
        # Si no se especificó un método válido, devolver el mensaje original
        print("[ENLACE] Método no implementado, devolviendo mensaje sin modificar")
        return mensaje_binario

def simular_ruido(mensaje_binario, tasa_error=0.01):
    """
    Simula ruido en el canal alterando bits aleatoriamente
    
    Args:
        mensaje_binario: Mensaje en formato binario
        tasa_error: Probabilidad de que un bit sea alterado (0.01 = 1%)
    
    Returns:
        Mensaje con bits potencialmente alterados
    """
    mensaje_con_ruido = list(mensaje_binario)
    bits_alterados = []
    
    for i in range(len(mensaje_con_ruido)):
        if random.random() < tasa_error:
            # Invertir el bit (0->1, 1->0)
            bit_original = mensaje_con_ruido[i]
            mensaje_con_ruido[i] = '1' if mensaje_con_ruido[i] == '0' else '0'
            bits_alterados.append((i, bit_original, mensaje_con_ruido[i]))
    
    if bits_alterados:
        print(f"[CANAL] ⚠️ Se alteraron {len(bits_alterados)} bits:")
        for pos, original, nuevo in bits_alterados:
            print(f"   - Posición {pos}: {original} → {nuevo}")
    else:
        print("[CANAL] No se alteró ningún bit durante la transmisión")
    
    return ''.join(mensaje_con_ruido)

def main():
    """Función principal para probar el emisor con arquitectura de capas"""
    print("=== EMISOR CON ARQUITECTURA DE CAPAS ===")
    
    # Inicializar las capas
    aplicacion = CapaAplicacion()
    presentacion = CapaPresentacion()
    # Por defecto usamos CRC-32 como método de detección
    enlace = CapaEnlace(metodo_deteccion='crc32')
    
    while True:
        try:
            # Capa de Aplicación - Solicitar mensaje
            mensaje = aplicacion.solicitar_mensaje()
            
            if mensaje.lower() == 'quit':
                break
                
            # Capa de Presentación - Codificar mensaje
            mensaje_binario = presentacion.codificar_mensaje(mensaje)
            
            # Capa de Enlace - Calcular integridad
            mensaje_con_integridad = enlace.calcular_integridad(mensaje_binario)
            
            # Simular canal con ruido
            tasa_error = float(input("Ingrese la tasa de error para el canal (0.0 - 1.0): "))
            mensaje_transmitido = simular_ruido(mensaje_con_integridad, tasa_error)
            
            print("\n[EMISOR] Mensaje preparado para transmisión:")
            print(f"   - Original: {mensaje}")
            print(f"   - Codificado: {mensaje_binario}")
            print(f"   - Con integridad: {mensaje_con_integridad}")
            print(f"   - Transmitido (con ruido): {mensaje_transmitido}")
            print("="*50)
            
            # En una implementación real, aquí enviaríamos el mensaje al receptor
            
        except KeyboardInterrupt:
            print("\nSaliendo del emisor...")
            break
        except Exception as e:
            print(f"Error: {e}")
            
if __name__ == "__main__":
    main()
