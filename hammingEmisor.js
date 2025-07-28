#!/usr/bin/env node
/**
 * Código de Hamming Emisor - Algoritmo de Corrección de Errores
 * Universidad del Valle de Guatemala - CC3067 Redes
 * Implementa código de Hamming (n,m) donde m + r + 1 <= 2^r
 */

const readline = require('readline');

/**
 * Calcula el número de bits de paridad necesarios
 */
function calculateParityBits(dataLength) {
    let r = 1;
    while (dataLength + r + 1 > Math.pow(2, r)) {
        r++;
    }
    return r;
}

/**
 * Determina si una posición es una potencia de 2 (posición de paridad)
 */
function isPowerOfTwo(n) {
    return n > 0 && (n & (n - 1)) === 0;
}

/**
 * Emisor de Hamming: Codifica el mensaje con bits de paridad
 */
function hammingSender(dataBits) {
    console.log("--------------CÓDIGO DE HAMMING EMISOR--------------");
    console.log(`Mensaje original: ${dataBits}`);
    console.log(`Longitud del mensaje: ${dataBits.length} bits`);
    
    const m = dataBits.length;
    const r = calculateParityBits(m);
    const n = m + r;
    
    console.log(`Bits de datos (m): ${m}`);
    console.log(`Bits de paridad necesarios (r): ${r}`);
    console.log(`Longitud total (n): ${n}`);
    console.log(`Verificación: m + r + 1 = ${m + r + 1} <= 2^r = ${Math.pow(2, r)}`);
    
    // Crear array para el código Hamming
    const hammingCode = new Array(n + 1); // Índice 1-based
    
    // Insertar bits de datos en posiciones que no son potencias de 2
    let dataIndex = 0;
    for (let i = 1; i <= n; i++) {
        if (isPowerOfTwo(i)) {
            hammingCode[i] = 0; // Inicializar bits de paridad
        } else {
            hammingCode[i] = parseInt(dataBits[dataIndex]);
            dataIndex++;
        }
    }
    
    console.log("\nPosiciones después de insertar datos:");
    for (let i = 1; i <= n; i++) {
        const type = isPowerOfTwo(i) ? "(P)" : "(D)";
        console.log(`Posición ${i}: ${hammingCode[i]} ${type}`);
    }
    
    // Calcular bits de paridad
    for (let parityPos = 1; parityPos <= n; parityPos *= 2) {
        let parityValue = 0;
        
        console.log(`\nCalculando paridad para posición ${parityPos}:`);
        const positions = [];
        
        for (let i = 1; i <= n; i++) {
            if ((i & parityPos) !== 0 && i !== parityPos) {
                parityValue ^= hammingCode[i];
                positions.push(i);
            }
        }
        
        console.log(`Posiciones verificadas: ${positions.join(', ')}`);
        console.log(`XOR de valores: ${parityValue}`);
        
        hammingCode[parityPos] = parityValue;
    }
    
    // Crear cadena final
    const finalCode = hammingCode.slice(1).join('');
    
    console.log("\nCódigo Hamming final:");
    for (let i = 1; i <= n; i++) {
        const type = isPowerOfTwo(i) ? "(P)" : "(D)";
        console.log(`Posición ${i}: ${hammingCode[i]} ${type}`);
    }
    
    console.log(`\nMensaje codificado: ${finalCode}`);
    console.log(`Longitud final: ${finalCode.length} bits`);
    
    return finalCode;
}

/**
 * Función principal
 */
function main() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    
    console.log("--------------EMISOR CÓDIGO DE HAMMING--------------");
    
    function askForInput() {
        rl.question("\nIngrese la trama en binario (o 'quit' para salir): ", (input) => {
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
                // Procesar con Hamming
                const result = hammingSender(message);
                console.log(`\n RESULTADO FINAL: ${result}`);
                console.log("=".repeat(50));
                
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

module.exports = { hammingSender, calculateParityBits, isPowerOfTwo };