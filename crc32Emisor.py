#!/usr/bin/env python3
"""
CRC-32 Emisor - Algoritmo de Detección de Errores
Universidad del Valle de Guatemala - CC3067 Redes
"""

def crc32_table():
    """Genera la tabla CRC-32 usando el polinomio estándar IEEE 802.3"""
    # Polinomio CRC-32 IEEE 802.3: 0x04C11DB7
    polynomial = 0x04C11DB7
    table = []
    
    for i in range(256):
        crc = i << 24
        for j in range(8):
            if crc & 0x80000000:
                crc = (crc << 1) ^ polynomial
            else:
                crc = crc << 1
            crc &= 0xFFFFFFFF
        table.append(crc)
    
    return table

def calculate_crc32(data_bits):
    """
    Calcula el CRC-32 de una cadena de bits
    Args:
        data_bits (str): Cadena binaria de datos
    Returns:
        int: Valor CRC-32
    """
    # Convertir bits a bytes
    # Agregar padding si es necesario para completar bytes
    while len(data_bits) % 8 != 0:
        data_bits = '0' + data_bits
    
    # Convertir a bytes
    data_bytes = []
    for i in range(0, len(data_bits), 8):
        byte_str = data_bits[i:i+8]
        data_bytes.append(int(byte_str, 2))
    
    # Calcular CRC-32
    table = crc32_table()
    crc = 0xFFFFFFFF  # Valor inicial
    
    for byte in data_bytes:
        tbl_idx = ((crc >> 24) ^ byte) & 0xFF
        crc = ((crc << 8) ^ table[tbl_idx]) & 0xFFFFFFFF
    
    return crc ^ 0xFFFFFFFF  # Inversión final

def crc32_sender(message_bits):
    """
    Emisor CRC-32: Agrega el checksum CRC-32 al mensaje
    Args:
        message_bits (str): Mensaje en binario
    Returns:
        str: Mensaje + CRC-32 en binario
    """
    print(f"=== CRC-32 EMISOR ===")
    print(f"Mensaje original: {message_bits}")
    print(f"Longitud del mensaje: {len(message_bits)} bits")
    
    # Asegurar que el mensaje tenga al menos 32 bits
    if len(message_bits) < 32:
        padding_needed = 32 - len(message_bits)
        message_bits = '0' * padding_needed + message_bits
        print(f"Mensaje con padding: {message_bits}")
    
    # Calcular CRC-32
    crc_value = calculate_crc32(message_bits)
    crc_bits = format(crc_value, '032b')  # CRC-32 siempre 32 bits
    
    # Mensaje final: datos originales + CRC-32
    final_message = message_bits + crc_bits
    
    print(f"CRC-32 calculado: {crc_value} (decimal)")
    print(f"CRC-32 en binario: {crc_bits}")
    print(f"Mensaje final: {final_message}")
    print(f"Longitud final: {len(final_message)} bits")
    
    return final_message

def main():
    """Función principal para probar el emisor CRC-32"""
    print("=== EMISOR CRC-32 ===")
    
    while True:
        try:
            message = input("\nIngrese la trama en binario (o 'quit' para salir): ").strip()
            
            if message.lower() == 'quit':
                break
            
            # Validar que sea binario
            if not all(c in '01' for c in message):
                print("Error: Ingrese solo 0s y 1s")
                continue
            
            if len(message) == 0:
                print("Error: Mensaje vacío")
                continue
            
            # Procesar con CRC-32
            result = crc32_sender(message)
            print(f"\n>>> RESULTADO FINAL: {result}")
            
        except KeyboardInterrupt:
            print("\nSaliendo...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()