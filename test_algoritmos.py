#!/usr/bin/env python3
"""
Script de Pruebas - Algoritmos de Detección y Corrección de Errores
Universidad del Valle de Guatemala - CC3067 Redes
"""
import os
import sys
import time
import random
import json
import subprocess
import matplotlib.pyplot as plt
import numpy as np
from crc32Emisor import calculate_crc32

def generar_mensaje_aleatorio(longitud_caracteres):
    """Genera un mensaje aleatorio de la longitud especificada"""
    caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    return ''.join(random.choice(caracteres) for _ in range(longitud_caracteres))

def texto_a_binario(texto):
    """Convierte texto a representación binaria ASCII (8 bits por carácter)"""
    resultado = ""
    for char in texto:
        ascii_binario = format(ord(char), '08b')
        resultado += ascii_binario
    return resultado

def binario_a_texto(binario):
    """Convierte representación binaria ASCII a texto"""
    texto = ""
    for i in range(0, len(binario), 8):
        byte = binario[i:i+8]
        if len(byte) == 8:
            caracter = chr(int(byte, 2))
            texto += caracter
    return texto

def aplicar_ruido(mensaje_bits, tasa_error):
    """Aplica ruido (flips de bits) según la tasa de error especificada"""
    resultado = list(mensaje_bits)
    bits_cambiados = 0
    posiciones_cambiadas = []
    
    for i in range(len(resultado)):
        if random.random() < tasa_error:
            resultado[i] = '1' if resultado[i] == '0' else '0'
            bits_cambiados += 1
            posiciones_cambiadas.append(i)
    
    return ''.join(resultado), bits_cambiados, posiciones_cambiadas

def calcular_crc32(mensaje_bits):
    """Calcula el CRC-32 para un mensaje en bits"""
    mensaje_con_ceros = mensaje_bits + '0' * 32
    crc_value = calculate_crc32(mensaje_con_ceros)
    crc_bits = format(crc_value, '032b')
    return mensaje_bits + crc_bits

def ejecutar_hamming_sender(mensaje_bits):
    """Ejecuta el emisor Hamming mediante Node.js y retorna el mensaje codificado"""
    # Guardar mensaje en un archivo temporal
    with open("temp_test_mensaje.txt", "w") as f:
        f.write(mensaje_bits)
    
    try:
        result = subprocess.run(
            ["node", "-e", 
             f"const {{ hammingSender }} = require('./hammingEmisor.js'); " +
             f"const fs = require('fs'); " +
             f"const mensaje = fs.readFileSync('temp_test_mensaje.txt', 'utf8'); " +
             f"const resultado = hammingSender(mensaje); " + 
             f"console.log(JSON.stringify({{ resultado: resultado }}));"],
            capture_output=True, text=True, check=True
        )
        
        # Extraer resultado del JSON
        resultado_json = json.loads(result.stdout)
        return resultado_json["resultado"]
        
    except Exception as e:
        print(f"Error al llamar a hammingEmisor.js: {e}")
        return None

def verificar_crc32(mensaje_con_crc):
    """Verifica un mensaje con CRC-32 y retorna si es íntegro"""
    # Verificar la integridad calculando el CRC del mensaje completo
    resultado = calculate_crc32(mensaje_con_crc)
    return resultado == 0  # Si el resto es 0, el mensaje es íntegro

def ejecutar_hamming_receiver(mensaje_hamming):
    """Ejecuta el receptor Hamming mediante Python y retorna el resultado"""
    # Guardar mensaje en un archivo temporal
    with open("temp_test_mensaje_hamming.txt", "w") as f:
        f.write(mensaje_hamming)
    
    try:
        result = subprocess.run(
            ["python3", "hammingReceptor.py", "--mensaje", "$(cat temp_test_mensaje_hamming.txt)", "--jsonOutput"],
            capture_output=True, text=True, check=True
        )
        
        # Extraer resultado del JSON
        return json.loads(result.stdout)
        
    except Exception as e:
        print(f"Error al llamar a hammingReceptor.py: {e}")
        return None

def prueba_crc32(mensaje_original, tasa_error):
    """Realiza una prueba con CRC-32 y devuelve los resultados"""
    # Convertir mensaje a binario
    mensaje_binario = texto_a_binario(mensaje_original)
    longitud_original = len(mensaje_binario)
    
    # Calcular CRC-32
    inicio = time.time()
    mensaje_con_crc = calcular_crc32(mensaje_binario)
    tiempo_codificacion = (time.time() - inicio) * 1000  # ms
    
    # Aplicar ruido
    mensaje_con_ruido, bits_cambiados, posiciones = aplicar_ruido(mensaje_con_crc, tasa_error)
    
    # Verificar integridad
    inicio = time.time()
    integridad_ok = verificar_crc32(mensaje_con_ruido)
    tiempo_verificacion = (time.time() - inicio) * 1000  # ms
    
    # Calcular overhead (bits adicionales / bits originales)
    overhead = (len(mensaje_con_crc) - longitud_original) / longitud_original
    
    return {
        "algoritmo": "CRC-32",
        "mensaje_original": mensaje_original,
        "longitud_original_bits": longitud_original,
        "longitud_con_integridad_bits": len(mensaje_con_crc),
        "bits_cambiados": bits_cambiados,
        "posiciones_cambiadas": posiciones,
        "integridad_ok": integridad_ok,
        "tiempo_codificacion_ms": tiempo_codificacion,
        "tiempo_verificacion_ms": tiempo_verificacion,
        "overhead": overhead
    }

def prueba_hamming(mensaje_original, tasa_error):
    """Realiza una prueba con Hamming y devuelve los resultados"""
    # Convertir mensaje a binario
    mensaje_binario = texto_a_binario(mensaje_original)
    longitud_original = len(mensaje_binario)
    
    # Calcular código Hamming
    inicio = time.time()
    mensaje_con_hamming = ejecutar_hamming_sender(mensaje_binario)
    tiempo_codificacion = (time.time() - inicio) * 1000  # ms
    
    if not mensaje_con_hamming:
        return None
    
    # Aplicar ruido
    mensaje_con_ruido, bits_cambiados, posiciones = aplicar_ruido(mensaje_con_hamming, tasa_error)
    
    # Verificar y corregir
    inicio = time.time()
    resultado_hamming = ejecutar_hamming_receiver(mensaje_con_ruido)
    tiempo_verificacion = (time.time() - inicio) * 1000  # ms
    
    if not resultado_hamming:
        return None
    
    # Calcular overhead (bits adicionales / bits originales)
    overhead = (len(mensaje_con_hamming) - longitud_original) / longitud_original
    
    return {
        "algoritmo": "Hamming",
        "mensaje_original": mensaje_original,
        "longitud_original_bits": longitud_original,
        "longitud_con_integridad_bits": len(mensaje_con_hamming),
        "bits_cambiados": bits_cambiados,
        "posiciones_cambiadas": posiciones,
        "error_detectado": resultado_hamming.get("errorDetectado", False),
        "error_corregido": resultado_hamming.get("errorCorregido", False),
        "posicion_error": resultado_hamming.get("posicionError", -1),
        "tiempo_codificacion_ms": tiempo_codificacion,
        "tiempo_verificacion_ms": tiempo_verificacion,
        "overhead": overhead
    }

def realizar_pruebas(longitudes_mensaje, tasas_error, repeticiones=5):
    """Realiza pruebas variando longitud de mensaje y tasa de error"""
    resultados = []
    
    total_pruebas = len(longitudes_mensaje) * len(tasas_error) * repeticiones * 2
    prueba_actual = 0
    
    print(f"Realizando {total_pruebas} pruebas...")
    
    for longitud in longitudes_mensaje:
        for tasa in tasas_error:
            for rep in range(repeticiones):
                prueba_actual += 2
                progreso = (prueba_actual / total_pruebas) * 100
                print(f"Progreso: {progreso:.1f}% - Prueba con longitud {longitud}, tasa {tasa}, repetición {rep+1}/{repeticiones}")
                
                # Generar mensaje aleatorio para esta prueba
                mensaje = generar_mensaje_aleatorio(longitud)
                
                # Prueba con CRC-32
                resultado_crc = prueba_crc32(mensaje, tasa)
                resultados.append(resultado_crc)
                
                # Prueba con Hamming
                resultado_hamming = prueba_hamming(mensaje, tasa)
                if resultado_hamming:
                    resultados.append(resultado_hamming)
    
    return resultados

def generar_graficas(resultados, directorio_salida="graficas"):
    """Genera gráficas a partir de los resultados de las pruebas"""
    # Crear directorio de salida si no existe
    os.makedirs(directorio_salida, exist_ok=True)
    
    # Separar resultados por algoritmo
    resultados_crc = [r for r in resultados if r["algoritmo"] == "CRC-32"]
    resultados_hamming = [r for r in resultados if r["algoritmo"] == "Hamming"]
    
    # 1. Gráfica de overhead vs longitud de mensaje
    longitudes_crc = sorted(list(set([r["longitud_original_bits"] for r in resultados_crc])))
    overhead_crc = [np.mean([r["overhead"] for r in resultados_crc if r["longitud_original_bits"] == longitud]) 
                   for longitud in longitudes_crc]
    
    longitudes_hamming = sorted(list(set([r["longitud_original_bits"] for r in resultados_hamming])))
    overhead_hamming = [np.mean([r["overhead"] for r in resultados_hamming if r["longitud_original_bits"] == longitud]) 
                       for longitud in longitudes_hamming]
    
    plt.figure(figsize=(10, 6))
    plt.plot(longitudes_crc, overhead_crc, 'o-', label='CRC-32')
    plt.plot(longitudes_hamming, overhead_hamming, 's-', label='Hamming')
    plt.xlabel('Longitud del mensaje (bits)')
    plt.ylabel('Overhead (bits extra / bits originales)')
    plt.title('Overhead vs Longitud del mensaje')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(directorio_salida, 'overhead_vs_longitud.png'))
    plt.close()
    
    # 2. Gráfica de detección de errores vs tasa de error
    tasas_error = sorted(list(set([r["bits_cambiados"]/r["longitud_con_integridad_bits"] 
                                  for r in resultados_crc])))
    
    tasa_deteccion_crc = []
    tasa_deteccion_hamming = []
    tasa_correccion_hamming = []
    
    for tasa in tasas_error:
        # Para cada tasa, filtramos resultados con tasa similar (tolerancia)
        resultados_crc_tasa = [r for r in resultados_crc if abs(r["bits_cambiados"]/r["longitud_con_integridad_bits"] - tasa) < 0.001]
        deteccion_crc = np.mean([1 if not r["integridad_ok"] else 0 for r in resultados_crc_tasa]) if resultados_crc_tasa else 0
        tasa_deteccion_crc.append(deteccion_crc)
        
        resultados_hamming_tasa = [r for r in resultados_hamming if abs(r["bits_cambiados"]/r["longitud_con_integridad_bits"] - tasa) < 0.001]
        deteccion_hamming = np.mean([1 if r["error_detectado"] else 0 for r in resultados_hamming_tasa]) if resultados_hamming_tasa else 0
        correccion_hamming = np.mean([1 if r["error_corregido"] else 0 for r in resultados_hamming_tasa]) if resultados_hamming_tasa else 0
        tasa_deteccion_hamming.append(deteccion_hamming)
        tasa_correccion_hamming.append(correccion_hamming)
    
    plt.figure(figsize=(10, 6))
    plt.plot(tasas_error, tasa_deteccion_crc, 'o-', label='Detección CRC-32')
    plt.plot(tasas_error, tasa_deteccion_hamming, 's-', label='Detección Hamming')
    plt.plot(tasas_error, tasa_correccion_hamming, '^-', label='Corrección Hamming')
    plt.xlabel('Tasa de error (bits modificados / total bits)')
    plt.ylabel('Tasa de éxito')
    plt.title('Detección y Corrección de Errores vs Tasa de Error')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(directorio_salida, 'deteccion_vs_tasa_error.png'))
    plt.close()
    
    # 3. Gráfica de tiempo de procesamiento vs longitud
    plt.figure(figsize=(10, 6))
    
    # Tiempos de codificación
    tiempo_codificacion_crc = [np.mean([r["tiempo_codificacion_ms"] for r in resultados_crc if r["longitud_original_bits"] == longitud]) 
                             for longitud in longitudes_crc]
    
    tiempo_codificacion_hamming = [np.mean([r["tiempo_codificacion_ms"] for r in resultados_hamming if r["longitud_original_bits"] == longitud]) 
                                 for longitud in longitudes_hamming]
    
    plt.subplot(1, 2, 1)
    plt.plot(longitudes_crc, tiempo_codificacion_crc, 'o-', label='CRC-32')
    plt.plot(longitudes_hamming, tiempo_codificacion_hamming, 's-', label='Hamming')
    plt.xlabel('Longitud del mensaje (bits)')
    plt.ylabel('Tiempo de codificación (ms)')
    plt.title('Tiempo de Codificación vs Longitud')
    plt.legend()
    plt.grid(True)
    
    # Tiempos de verificación
    tiempo_verificacion_crc = [np.mean([r["tiempo_verificacion_ms"] for r in resultados_crc if r["longitud_original_bits"] == longitud]) 
                             for longitud in longitudes_crc]
    
    tiempo_verificacion_hamming = [np.mean([r["tiempo_verificacion_ms"] for r in resultados_hamming if r["longitud_original_bits"] == longitud]) 
                                 for longitud in longitudes_hamming]
    
    plt.subplot(1, 2, 2)
    plt.plot(longitudes_crc, tiempo_verificacion_crc, 'o-', label='CRC-32')
    plt.plot(longitudes_hamming, tiempo_verificacion_hamming, 's-', label='Hamming')
    plt.xlabel('Longitud del mensaje (bits)')
    plt.ylabel('Tiempo de verificación (ms)')
    plt.title('Tiempo de Verificación vs Longitud')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(directorio_salida, 'tiempos_vs_longitud.png'))
    plt.close()
    
    # 4. Resumen de resultados en JSON para análisis posteriores
    with open(os.path.join(directorio_salida, 'resultados.json'), 'w') as f:
        json.dump(resultados, f, indent=2)
    
    print(f"Gráficas guardadas en el directorio '{directorio_salida}'")

def main():
    """Función principal para ejecutar las pruebas"""
    print("=== Test de Algoritmos de Detección y Corrección de Errores ===")
    
    # Configuración de pruebas
    longitudes_mensaje = [10, 20, 50, 100, 200]  # caracteres
    tasas_error = [0.0, 0.001, 0.01, 0.05, 0.1]  # probabilidad de error por bit
    repeticiones = 3  # número de pruebas por configuración
    
    # Ejecutar pruebas
    resultados = realizar_pruebas(longitudes_mensaje, tasas_error, repeticiones)
    
    # Generar gráficas y guardar resultados
    generar_graficas(resultados)
    
    print("Pruebas completadas con éxito.")

if __name__ == "__main__":
    main()
