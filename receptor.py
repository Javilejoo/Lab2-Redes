#!/usr/bin/env python3
"""
Receptor con Arquitectura de Capas - Laboratorio 2 Segunda Parte
Universidad del Valle de Guatemala - CC3067 Redes
Implementa la arquitectura de capas para el receptor
"""

import sys
import os
import subprocess

# Importar los algoritmos existentes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from hammingReceptor import hamming_receiver

class CapaAplicacion:
    """Capa de Aplicación: Interacción con el usuario y manejo de mensajes"""
    
    def solicitar_mensaje(self):
        """Solicita un mensaje codificado para recibir"""
        mensaje = input("Ingrese el mensaje codificado recibido: ")
        print(f"[APLICACIÓN] Mensaje codificado recibido: '{mensaje}'")
        return mensaje
        
    def mostrar_mensaje(self, mensaje):
        """Muestra el mensaje decodificado al usuario"""
        print(f"[APLICACIÓN] Mensaje final: '{mensaje}'")
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
    
    def verificar_integridad(self, mensaje_recibido):
        """Verifica la integridad del mensaje recibido"""
        print(f"[ENLACE] Verificando integridad con método {self.metodo_deteccion}")
        
        if self.metodo_deteccion == 'crc32':
            try:
                # Llamar al receptor de CRC-32 usando Node.js
                process = subprocess.run(['node', 'crc32Receptor.js', mensaje_recibido], 
                                       capture_output=True, text=True)
                resultado = process.stdout.strip()
                
                if "No se detectaron errores" in resultado:
                    print("[ENLACE] ✅ CRC-32: Integridad verificada")
                    # Extraer el mensaje original (sin el CRC)
                    datos = mensaje_recibido[:-32]  # Quitar los 32 bits del CRC
                    return True, datos
                else:
                    print("[ENLACE] ❌ CRC-32: Error de integridad detectado")
                    return False, None
                
            except Exception as e:
                print(f"[ENLACE] Error al verificar con CRC-32: {e}")
                return False, None
        
        # Si no se especificó un método válido, asumir que no hay errores
        print("[ENLACE] Método no implementado, asumiendo mensaje íntegro")
        return True, mensaje_recibido
    
    def corregir_mensaje(self, mensaje_con_errores):
        """Corrige errores en el mensaje si es posible"""
        print(f"[ENLACE] Intentando corregir errores con método {self.metodo_correccion}")
        
        if self.metodo_correccion == 'hamming':
            try:
                # Usar la implementación del receptor Hamming
                resultado = hamming_receiver(mensaje_con_errores)
                
                if resultado["status"] == "success":
                    print("[ENLACE] ✅ Hamming: No se detectaron errores")
                    return True, resultado["message"]
                    
                elif resultado["status"] == "corrected":
                    print(f"[ENLACE] 🔧 Hamming: Error corregido en posición {resultado['error_position']}")
                    return True, resultado["message"]
                    
                else:
                    print("[ENLACE] ❌ Hamming: Error no corregible detectado")
                    return False, None
                    
            except Exception as e:
                print(f"[ENLACE] Error al corregir con Hamming: {e}")
                return False, None
                
        # Si no se especificó un método válido, no podemos corregir
        print("[ENLACE] Método de corrección no implementado")
        return False, None

def main():
    """Función principal para probar el receptor con arquitectura de capas"""
    print("=== RECEPTOR CON ARQUITECTURA DE CAPAS ===")
    
    # Inicializar las capas
    aplicacion = CapaAplicacion()
    presentacion = CapaPresentacion()
    enlace = CapaEnlace(metodo_deteccion='crc32', metodo_correccion='hamming')
    
    while True:
        try:
            # Recibir mensaje codificado (simulado con entrada del usuario)
            mensaje_codificado = aplicacion.solicitar_mensaje()
            
            if mensaje_codificado.lower() == 'quit':
                break
            
            # Verificar integridad del mensaje
            integridad_ok, mensaje_verificado = enlace.verificar_integridad(mensaje_codificado)
            
            if not integridad_ok:
                print("[RECEPTOR] ❌ Mensaje descartado por error de integridad")
                print("="*50)
                continue
                
            # Si hay errores pero son corregibles, intentar corregir
            if self.metodo_correccion != 'none':
                correccion_ok, mensaje_corregido = enlace.corregir_mensaje(mensaje_verificado)
                if correccion_ok:
                    mensaje_verificado = mensaje_corregido
            
            # Decodificar el mensaje (convertir de binario a texto)
            mensaje_decodificado = presentacion.decodificar_mensaje(mensaje_verificado)
            
            # Mostrar el mensaje final
            aplicacion.mostrar_mensaje(mensaje_decodificado)
            
            print("\n[RECEPTOR] Procesamiento completado:")
            print(f"   - Recibido: {mensaje_codificado}")
            print(f"   - Verificado: {mensaje_verificado}")
            print(f"   - Decodificado: {mensaje_decodificado}")
            print("="*50)
            
        except KeyboardInterrupt:
            print("\nSaliendo del receptor...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
