# Logging Pipeline.

Implementado en Python.

Implementa un patron cliente-servidor para enviar y recibir logs desde clientes. El servidor opera en modo multi-thread para poder sopotar requests concurrentes y aun asi mantener un estado consistente de los logs.


## Development

TBD.

## Correr tests

Formato de logs enviados desde el cliente.

1. Emision de logs

 ```json
 {
     "app_id": "msteams",
     "message": "Hey, this app is running fine!",
     "tags": ["testing", "python"],
     "timestamp": "2021-09-26"
 }
 ```

2. Consulta de logs

Formato `AppId (string)`, `From, To (date)`, `tag (string)` y `pattern (string)`.

 ```json
 {
     "app_id": "msteams",
     "from": "2021-09-26",
     "to": "2021-09-26",
     "tag": "python",
     "pattern": "^this should be a regex.\*"
 }
 ```
