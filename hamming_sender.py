def hamming_sender():
    """
    Esta funcion pide al usuario ingresar una trama de ciertos bits,
      y lo traduce el mensaje para que sea enviado
    """
    mensaje = input("Ingrese el mensaje a enviar (bits): ")

    m = len(mensaje)
    # encontrar el numero de bits de paridad necesararios
    r = 0
    while (2 ** r < m + r + 1):
        r += 1
    print(f"Numero de bits de paridad necesarios: {r}")

    # encontrar el numero de bits para enviar, (el emisor convierte el mensaje a bits necesarios para enviarlos por un medio)
    n = m + r
    print(f"Numero total de bits a enviar: {n}")

    # saber en que posiciones se deben colocar los bits de paridad
    posiciones_paridad = [2**i for i in range(r)]
    print(f"Posiciones de bits de paridad: {posiciones_paridad}")

    # crear una lista para almacenar los bits de paridad y los bits del mensaje
    mensaje_completo = ['0'] * n
    j = 0
    for i in range(1, n + 1):
        if i in posiciones_paridad:
            mensaje_completo[i - 1] = 'p'  # 'p' representa un bit de paridad
        else:
            mensaje_completo[i - 1] = mensaje[j]
            j += 1

    print(f"Mensaje completo inicial: {mensaje_completo[::-1]}")
    for i in range (n):
        if mensaje_completo[i] == 'p':
            # Calcular el valor del bit de paridad
            paridad = 0
            for j in range(1, n + 1):
                if (j & (i + 1)) != 0:
                    paridad ^= int(mensaje_completo[j - 1])
            mensaje_completo[i] = str(paridad)

    print(f"Mensaje completo final: {mensaje_completo[::-1]}")

hamming_sender()

