#!/usr/bin/env python3
"""
Código de Hamming Receptor - Algoritmo de Corrección de Errores
Universidad del Valle de Guatemala - CC3067 Redes
"""

def is_power_of_two(n):
    """Determina si un número es potencia de 2"""
    return n > 0 and (n & (n - 1)) == 0

def calculate_parity_bits(data_length):
    """Calcula el número de bits de paridad necesarios"""
    r = 1
    while data_length + r + 1 > 2**r:
        r += 1
    return r

def hamming_receiver(received_code):
    """
    Receptor de Hamming: Detecta y corrige errores en código Hamming
    Args:
        received_code (str): Código Hamming recibido
    Returns:
        dict: Resultado del procesamiento
    """
    print("=== CÓDIGO DE HAMMING RECEPTOR ===")
    print(f"Código recibido: {received_code}")
    print(f"Longitud recibida: {len(received_code)} bits")
    
    n = len(received_code)
    
    # Convertir a array indexado desde 1
    hamming_array = [0] + [int(bit) for bit in received_code]
    
    print("\nAnálisis de posiciones:")
    for i in range(1, n + 1):
        bit_type = "(P)" if is_power_of_two(i) else "(D)"
        print(f"Posición {i}: {hamming_array[i]} {bit_type}")
    
    # Calcular síndrome de error
    error_position = 0
    parity_checks = []
    
    print("\nVerificación de paridad:")
    
    # Verificar cada bit de paridad
    parity_bit = 1
    while parity_bit <= n:
        parity_value = 0
        positions_checked = []
        
        for i in range(1, n + 1):
            if (i & parity_bit) != 0:
                parity_value ^= hamming_array[i]
                positions_checked.append(i)
        
        print(f"Paridad {parity_bit}: posiciones {positions_checked} -> XOR = {parity_value}")
        parity_checks.append(parity_value)
        
        if parity_value != 0:
            error_position += parity_bit
        
        parity_bit *= 2
    
    print(f"\nSíndrome de error: {error_position}")
    
    # Determinar resultado
    if error_position == 0:
        print("✅ RESULTADO: No se detectaron errores")
        
        # Extraer datos originales (posiciones que no son potencias de 2)
        original_data = ""
        for i in range(1, n + 1):
            if not is_power_of_two(i):
                original_data += str(hamming_array[i])
        
        print(f"Trama original: {original_data}")
        
        return {
            "status": "success",
            "message": original_data,
            "error": False,
            "corrected": False
        }
    
    else:
        print(f"🔧 RESULTADO: Error detectado y corregido en posición {error_position}")
        
        # Corregir el error
        original_bit = hamming_array[error_position]
        hamming_array[error_position] = 1 - hamming_array[error_position]
        corrected_bit = hamming_array[error_position]
        
        print(f"Posición {error_position}: {original_bit} -> {corrected_bit}")
        
        # Extraer datos corregidos
        corrected_data = ""
        for i in range(1, n + 1):
            if not is_power_of_two(i):
                corrected_data += str(hamming_array[i])
        
        print(f"Trama corregida: {corrected_data}")
        
        return {
            "status": "corrected",
            "message": corrected_data,
            "error": True,
            "corrected": True,
            "error_position": error_position,
            "original_bit": original_bit,
            "corrected_bit": corrected_bit
        }

def main():
    """Función principal para probar el receptor Hamming"""
    print("=== RECEPTOR CÓDIGO DE HAMMING ===")
    
    while True:
        try:
            message = input("\nIngrese el código Hamming recibido (o 'quit' para salir): ").strip()
            
            if message.lower() == 'quit':
                break
            
            # Validar que sea binario
            if not all(c in '01' for c in message):
                print("Error: Ingrese solo 0s y 1s")
                continue
            
            if len(message) == 0:
                print("Error: Mensaje vacío")
                continue
            
            # Procesar con Hamming
            result = hamming_receiver(message)
            print("\n" + "="*50)
            
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()