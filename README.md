# Logging Pipeline.

Implementado en Python.

Implementa un patron cliente-servidor para enviar y recibir logs desde clientes. El servidor opera en modo multi-thread para poder soportar requests concurrentes y aun asi mantener un estado consistente de los logs.

Este codigo ejercita fuertemente el acceso concurrente a recursos compartidos por lo que se usan distintas tecnicas de sincronizacion (locks, semaforos, etc) para asegurar la integridad de los datos y evitar condiciones de carrera.

### Almacenamiento de logs

Los logs son archivados en archivos de texto plano junto con metadata (hora, tags). Generando una carpeta por cada una de las aplicaciones (`app_id`) que luego pueden ser consultadas a traves de operaciones de lectura.


### Protocolo de comunicacion

El protocolo de comunicacion entre el cliente y el servidor es un protocolo custom basado en TCP y un payload en formato JSON.

El texto es enviado en formato plano sin ningun tipo de compresion o cifrado. El largo del mensaje es un numero entero que indica el largo del payload en bytes, seguido de un separador (en este caso, el caracter `|`) y luego el payload en formato JSON.


```
<largo del mensaje><separador><payload en formato JSON>

e.g.

124|{"app_id": "msteams", "message": "Hey, this app is running fine!", "tags": ["testing", "python"], "timestamp": "2021-09-26"}
```

## Development

TBD.

## Correr tests

Para comprobar y ejercitar el soporte para concurrencia en el servidor se han implementado una serie de scripts que corren tests de carga y concurrencia. Estos scripts simulan el comportamiento de multiples clientes enviando logs al servidor de manera concurrente.
