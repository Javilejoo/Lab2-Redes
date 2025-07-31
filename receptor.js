#!/usr/bin/env node

/**
 * Receptor - Arquitectura de Capas con Detección y Corrección de Errores
 * Universidad del Valle de Guatemala - CC3067 Redes
 */
const net = require('net');
const fs = require('fs');
const { execSync } = require('child_process');
const { crc32Receiver } = require('./crc32Receptor.js');

// Puerto en el que escuchar las conexiones
const PUERTO = 8888;

/**
 * Capa de Aplicación
 * Servicios: mostrar_mensaje
 */
class AplicacionLayer {
    /**
     * Muestra el mensaje recibido al usuario
     * @param {string} mensaje - Mensaje decodificado
     * @param {boolean} hayError - Indica si hubo errores no corregibles
     */
    mostrar_mensaje(mensaje, hayError) {
        console.log("\n----- CAPA DE APLICACIÓN: MOSTRAR MENSAJE -----");
        
        if (hayError) {
            console.log("ERROR: Se detectaron errores que no pudieron ser corregidos.");
            console.log("El mensaje puede estar corrupto.");
        } else {
            console.log("Mensaje recibido correctamente:");
            console.log(mensaje);
        }
    }
}

/**
 * Capa de Presentación
 * Servicios: decodificar_mensaje
 */
class PresentacionLayer {
    /**
     * Decodifica un mensaje de ASCII binario a texto
     * @param {string} binario - Mensaje en formato ASCII binario
     * @param {boolean} hayError - Indica si hubo errores no corregibles
     * @returns {string} Mensaje decodificado o cadena vacía si hay errores
     */
    decodificar_mensaje(binario, hayError) {
        console.log("\n----- CAPA DE PRESENTACIÓN: DECODIFICAR MENSAJE -----");
        
        // Si hay errores y no se pueden corregir, no decodificamos
        if (hayError) {
            console.log("No se puede decodificar debido a errores no corregibles.");
            return "";
        }
        
        let texto = "";
        
        // Procesar cada byte (8 bits)
        for (let i = 0; i < binario.length; i += 8) {
            const byte = binario.slice(i, i + 8);
            if (byte.length === 8) {
                const caracter = String.fromCharCode(parseInt(byte, 2));
                texto += caracter;
                console.log(`Binario: ${byte} -> ASCII: ${parseInt(byte, 2)} -> Carácter: '${caracter}'`);
            }
        }
        
        console.log(`Mensaje decodificado: ${texto}`);
        return texto;
    }
}

/**
 * Capa de Enlace
 * Servicios: verificar_integridad, corregir_mensaje
 */
class EnlaceLayer {
    /**
     * Verifica la integridad del mensaje recibido y corrige errores si es posible
     * @param {string} mensaje - Mensaje binario con información de integridad
     * @param {string} algoritmo - Algoritmo utilizado (crc32 o hamming)
     * @returns {Object} Objeto con el mensaje original y si hubo errores no corregibles
     */
    verificar_integridad(mensaje, algoritmo) {
        console.log(`\n----- CAPA DE ENLACE: VERIFICAR INTEGRIDAD (${algoritmo}) -----`);
        
        // Información de la verificación
        let resultado = {
            mensaje_original: "",    // Mensaje sin la información de integridad
            hubo_errores: false,     // ¿Se detectaron errores?
            errores_corregidos: false, // ¿Se pudieron corregir los errores?
            hay_error_no_corregible: false  // ¿Quedaron errores sin corregir?
        };
        
        if (algoritmo === "crc32") {
            // Algoritmo CRC-32 para detección de errores
            console.log("Verificando con CRC-32...");
            
            // Los últimos 32 bits son el CRC
            const datos = mensaje.slice(0, -32);
            const crc_recibido = mensaje.slice(-32);
            
            console.log(`Datos: ${datos}`);
            console.log(`CRC recibido: ${crc_recibido}`);
            
            // Verificar la integridad usando la función de crc32Receptor.js
            const verificacion = crc32Receiver(mensaje);
            
            resultado.mensaje_original = datos;
            resultado.hubo_errores = !verificacion.integridadOk;
            resultado.hay_error_no_corregible = resultado.hubo_errores; // CRC-32 no corrige
            
            console.log(`Integridad: ${verificacion.integridadOk ? "OK" : "ERROR"}`);
            
            if (resultado.hubo_errores) {
                console.log("Se detectaron errores en los datos (CRC no coincide).");
                console.log("CRC-32 no puede corregir errores, solo detectarlos.");
            } else {
                console.log("No se detectaron errores en los datos.");
            }
            
        } else if (algoritmo === "hamming") {
            // Algoritmo de Hamming para corrección de errores
            console.log("Verificando con código Hamming...");
            
            // Guardar mensaje en un archivo temporal para llamar al script Python
            fs.writeFileSync("temp_mensaje_receptor.txt", mensaje);
            
            try {
                // Llamar a hammingReceptor.py usando Python
                const salida = execSync(
                    'python3 hammingReceptor.py --mensaje "$(cat temp_mensaje_receptor.txt)" --jsonOutput',
                    { encoding: 'utf8' }
                );
                
                // Parsear el resultado JSON
                const resultadoHamming = JSON.parse(salida);
                
                resultado.mensaje_original = resultadoHamming.mensajeOriginal;
                resultado.hubo_errores = resultadoHamming.errorDetectado;
                resultado.errores_corregidos = resultadoHamming.errorCorregido;
                resultado.hay_error_no_corregible = resultadoHamming.errorDetectado && !resultadoHamming.errorCorregido;
                
                if (resultado.hubo_errores) {
                    if (resultado.errores_corregidos) {
                        console.log(`Se detectó un error en la posición ${resultadoHamming.posicionError} y fue corregido.`);
                    } else {
                        console.log("Se detectaron múltiples errores que no pudieron ser corregidos.");
                    }
                } else {
                    console.log("No se detectaron errores en los datos.");
                }
                
            } catch (error) {
                console.error("Error al ejecutar hammingReceptor.py:", error.message);
                resultado.hay_error_no_corregible = true;
            }
        }
        
        return resultado;
    }
    
    /**
     * Intenta corregir errores en el mensaje si el algoritmo lo permite
     * @param {Object} resultado - Resultado de la verificación
     * @returns {string} Mensaje corregido o original según corresponda
     */
    corregir_mensaje(resultado) {
        console.log("\n----- CAPA DE ENLACE: CORREGIR MENSAJE -----");
        
        if (!resultado.hubo_errores) {
            console.log("No se detectaron errores, no es necesario corregir.");
            return resultado.mensaje_original;
        }
        
        if (resultado.errores_corregidos) {
            console.log("Errores corregidos exitosamente.");
            return resultado.mensaje_original;
        }
        
        console.log("No fue posible corregir todos los errores.");
        return resultado.mensaje_original;
    }
}

/**
 * Capa de Transmisión
 * Servicios: recibir_informacion
 */
class TransmisionLayer {
    constructor() {
        this.server = null;
    }
    
    /**
     * Inicializa el servidor para recibir información
     * @param {Function} callback - Función a llamar cuando se reciba información
     */
    recibir_informacion(callback) {
        console.log("\n----- CAPA DE TRANSMISIÓN: RECIBIR INFORMACIÓN -----");
        console.log(`Iniciando servidor en el puerto ${PUERTO}...`);
        
        this.server = net.createServer((socket) => {
            console.log(`Cliente conectado: ${socket.remoteAddress}:${socket.remotePort}`);
            
            // Buffer para ir acumulando los datos
            let buffer = "";
            
            // Evento para recibir datos
            socket.on('data', (data) => {
                const chunk = data.toString();
                buffer += chunk;
                console.log(`Recibidos ${chunk.length} bits`);
            });
            
            // Cuando se cierra la conexión, procesamos el mensaje completo
            socket.on('end', () => {
                console.log(`Conexión cerrada. Mensaje completo recibido (${buffer.length} bits).`);
                
                // Solicitar al cliente que indique qué algoritmo se utilizó
                const algoritmo = process.argv[2] || promptAlgoritmo();
                
                // Enviar mensaje de confirmación antes de procesar
                socket.write("Mensaje recibido", () => {
                    // Llamar al callback con el mensaje y el algoritmo
                    callback(buffer, algoritmo);
                });
            });
            
            // Manejar errores de conexión
            socket.on('error', (err) => {
                console.error(`Error de conexión: ${err.message}`);
            });
        });
        
        // Iniciar el servidor
        this.server.listen(PUERTO, () => {
            console.log(`Servidor escuchando en el puerto ${PUERTO}`);
        });
        
        // Manejar errores del servidor
        this.server.on('error', (err) => {
            console.error(`Error del servidor: ${err.message}`);
            if (err.code === 'EADDRINUSE') {
                console.error(`El puerto ${PUERTO} está en uso. Intente con otro puerto.`);
            }
        });
    }
    
    /**
     * Cierra el servidor
     */
    cerrar() {
        if (this.server) {
            this.server.close();
            console.log("Servidor cerrado.");
        }
    }
}

/**
 * Solicita al usuario que indique el algoritmo utilizado
 * @returns {string} Nombre del algoritmo ("crc32" o "hamming")
 */
function promptAlgoritmo() {
    console.log("\nIndique el algoritmo utilizado por el emisor:");
    console.log("1. CRC-32");
    console.log("2. Hamming");
    
    const readline = require('readline-sync');
    const opcion = readline.question("Seleccione (1 o 2): ");
    
    if (opcion === "1") {
        return "crc32";
    } else if (opcion === "2") {
        return "hamming";
    } else {
        console.log("Opción inválida. Usando CRC-32 por defecto.");
        return "crc32";
    }
}

/**
 * Función principal
 */
function main() {
    console.log("\n============= RECEPTOR - ARQUITECTURA DE CAPAS =============");
    
    // Verificar si se especificó el algoritmo como argumento
    let algoritmoSeleccionado = null;
    if (process.argv.length > 2) {
        const arg = process.argv[2].toLowerCase();
        if (arg === "crc32" || arg === "hamming") {
            algoritmoSeleccionado = arg;
            console.log(`Algoritmo seleccionado por línea de comandos: ${algoritmoSeleccionado}`);
        }
    }
    
    // Si no se especificó por línea de comandos, preguntar al usuario
    if (!algoritmoSeleccionado) {
        algoritmoSeleccionado = promptAlgoritmo();
    }
    
    // Inicializar las capas
    const transmision = new TransmisionLayer();
    const enlace = new EnlaceLayer();
    const presentacion = new PresentacionLayer();
    const aplicacion = new AplicacionLayer();
    
    console.log(`\nReceptor configurado para usar el algoritmo: ${algoritmoSeleccionado}`);
    console.log("Esperando mensajes...");
    
    // Iniciar la recepción de mensajes
    transmision.recibir_informacion((mensaje, algoritmo) => {
        console.log(`\nMensaje recibido (${mensaje.length} bits) usando ${algoritmoSeleccionado}`);
        
        try {
            // Verificar integridad (Enlace)
            const resultadoVerificacion = enlace.verificar_integridad(mensaje, algoritmoSeleccionado);
            
            // Corregir errores si es posible (Enlace)
            const mensajeProcesado = enlace.corregir_mensaje(resultadoVerificacion);
            
            // Decodificar mensaje (Presentación)
            const mensajeDecodificado = presentacion.decodificar_mensaje(
                mensajeProcesado, 
                resultadoVerificacion.hay_error_no_corregible
            );
            
            // Mostrar mensaje al usuario (Aplicación)
            aplicacion.mostrar_mensaje(
                mensajeDecodificado, 
                resultadoVerificacion.hay_error_no_corregible
            );
            
        } catch (error) {
            console.error("Error al procesar el mensaje:", error);
        }
        
        console.log("\n" + "=".repeat(60));
        console.log("Esperando nuevo mensaje...");
    });
    
    // Manejar señal de interrupción (Ctrl+C)
    process.on('SIGINT', () => {
        console.log("\nCerrando receptor...");
        transmision.cerrar();
        process.exit(0);
    });
}

// Iniciar el programa
main();
