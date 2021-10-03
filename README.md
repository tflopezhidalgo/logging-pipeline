# Protocolo

Mensajes desde el cliente:

 - Agregado de logs: Los clientes envían `AppId (string)`, `message (string)`, `logTags (lista)` y `timestamp (date)`.
 - Consulta de logs: Los clientes envían `AppId (string)`, `From, To (date)`, `tag (string)` y `pattern (string)`.

Clientes envian JSON:

 Para agregar logs
 
 ```json
 {
     "operation": "append",
     "app": "msteams",
     "message": "this is a test log",
     "tags": ["testing", "python"],
     "timestamp": "2021-09-26"
 }
 ```

 Para consulta

 ```json
 {
     "operation": "filter",
     "app": "msteams",
     "from": "2021-09-26",
     "to": "2021-09-26",
     "tag": "python",
     "pattern": "^this should be a regex.\*"
 }
 ```
