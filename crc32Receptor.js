#!/usr/bin/env node
/**
 * CRC-32 Receptor - Algoritmo de Detección de Errores
 * Universidad del Valle de Guatemala - CC3067 Redes
 */

const readline = require('readline');

/**
 * Genera la tabla CRC-32 usando el polinomio estándar IEEE 802.3
 */
function generateCRC32Table() {
    const polynomial = 0x04C11DB7; // Polinomio CRC-32 IEEE 802.3
    const table = new Array(256);
    
    for (let i = 0; i < 256; i++) {
        let crc = i << 24;
        for (let j = 0; j < 8; j++) {
            if (crc & 0x80000000) {
                crc = (crc << 1) ^ polynomial;
            } else {
                crc = crc << 1;
            }
            crc = crc >>> 0; // Mantener como unsigned 32-bit
        }
        table[i] = crc;
    }
    
    return table;
}

/**
 * Calcula el CRC-32 de una cadena de bits
 */
function calculateCRC32(dataBits) {
    // Agregar padding si es necesario para completar bytes
    while (dataBits.length % 8 !== 0) {
        dataBits = '0' + dataBits;
    }
    
    // Convertir a bytes
    const dataBytes = [];
    for (let i = 0; i < dataBits.length; i += 8) {
        const byteStr = dataBits.substr(i, 8);
        dataBytes.push(parseInt(byteStr, 2));
    }
    
    // Calcular CRC-32
    const table = generateCRC32Table();
    let crc = 0xFFFFFFFF; // Valor inicial
    
    for (const byte of dataBytes) {
        const tblIdx = ((crc >>> 24) ^ byte) & 0xFF;
        crc = ((crc << 8) ^ table[tblIdx]) >>> 0;
    }
    
    return (crc ^ 0xFFFFFFFF) >>> 0; // Inversión final
}

/**
 * Receptor CRC-32: Verifica la integridad del mensaje
 */
function crc32Receiver(receivedMessage) {
    console.log("--------------CRC-32 RECEPTOR--------------");
    console.log(`Mensaje recibido: ${receivedMessage}`);
    console.log(`Longitud recibida: ${receivedMessage.length} bits`);
    
    if (receivedMessage.length < 32) {
        console.log("Error: Mensaje demasiado corto para contener CRC-32");
        return;
    }
    
    // Separar datos y CRC-32 para mostrar información
    const dataLength = receivedMessage.length - 32;
    const dataPart = receivedMessage.substr(0, dataLength);
    const receivedCRC = receivedMessage.substr(dataLength, 32);
    
    console.log(`Datos extraídos: ${dataPart}`);
    console.log(`CRC-32 recibido: ${receivedCRC}`);
    
    // Para verificar: calculamos el CRC del mensaje completo
    // Si el mensaje no tiene errores, el resultado debería ser 0
    const verificationCRC = calculateCRC32(receivedMessage);
    console.log(`CRC de verificación: ${verificationCRC} (decimal)`);
    
    // Alternativamente, podemos comparar el CRC recibido con el calculado de los datos
    const calculatedCRC = calculateCRC32(dataPart + '0'.repeat(32));
    const calculatedCRCBits = calculatedCRC.toString(2).padStart(32, '0');
    console.log(`CRC calculado: ${calculatedCRCBits}`);
    
    // Verificar si hay errores (dos métodos)
    const method1 = (verificationCRC === 0);
    const method2 = (receivedCRC === calculatedCRCBits);
    
    if (method2) {
        console.log("RESULTADO: No se detectaron errores");
        console.log(`Trama original: ${dataPart}`);
        return {
            status: "success",
            message: dataPart,
            error: false
        };
    } else {
        console.log("RESULTADO: Se detectaron errores - Trama descartada");
        console.log("El CRC-32 recibido no coincide con el calculado");
        return {
            status: "error",
            message: null,
            error: true,
            details: "CRC-32 no coincide"
        };
    }
}

/**
 * Función principal
 */
function main() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    
    console.log("=== RECEPTOR CRC-32 ===");
    
    function askForInput() {
        rl.question("\nIngrese el mensaje recibido (o 'quit' para salir): ", (input) => {
            const message = input.trim();
            
            if (message.toLowerCase() === 'quit') {
                rl.close();
                return;
            }
            
            // Validar que sea binario
            if (!/^[01]+$/.test(message)) {
                console.log("Error: Ingrese solo 0s y 1s");
                askForInput();
                return;
            }
            
            if (message.length === 0) {
                console.log("Error: Mensaje vacío");
                askForInput();
                return;
            }
            
            try {
                // Procesar con CRC-32
                const result = crc32Receiver(message);
                console.log("\n" + "=".repeat(50));
                
                askForInput();
            } catch (error) {
                console.log(`Error: ${error.message}`);
                askForInput();
            }
        });
    }
    
    askForInput();
}

if (require.main === module) {
    main();
}

module.exports = { crc32Receiver, calculateCRC32 };