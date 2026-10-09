# Entregable 2d · Modelo de datos

## Diagrama entidad-relación

```mermaid
erDiagram
    USUARIO ||--o| REPARTIDOR : "tiene perfil"
    USUARIO ||--o{ HISTORIAL_ESTADOS : "realiza"
    PEDIDO ||--|| ENTREGA : "genera"
    REPARTIDOR ||--o{ ENTREGA : "asignado a"
    ENTREGA ||--o{ INCIDENCIA : "puede tener"
    ENTREGA ||--o{ ALERTA : "puede generar"

    USUARIO {
        int id
        string username
        string password "cifrada"
        string first_name
        string last_name
        string rol "ADMIN|REPARTIDOR"
        string telefono
    }
    REPARTIDOR {
        int id
        int usuario_id
        string vehiculo
        string estado "DISPONIBLE|EN_RUTA|INACTIVO"
    }
    PEDIDO {
        int id
        string cliente
        string telefono
        string direccion
        string notas
        datetime hora_limite
        string estado "RECIBIDO→PREPARANDO→ASIGNADO→ENTREGADO / CANCELADO"
        datetime fecha_registro
    }
    ENTREGA {
        int id
        int pedido_id
        int repartidor_id
        datetime hora_asignacion
        datetime hora_salida
        datetime hora_entrega
        string estado "ASIGNADO→EN_CAMINO→ENTREGADO / INCIDENCIA"
    }
    INCIDENCIA {
        int id
        int entrega_id
        string tipo "CLIENTE_AUSENTE|DIRECCION_INCORRECTA|VEHICULO|TRAFICO|OTRO"
        string descripcion
        datetime fecha
        bool resuelta
        datetime fecha_resolucion
    }
    ALERTA {
        int id
        int entrega_id
        string nivel "RIESGO|RETRASO"
        string mensaje
        datetime fecha
        bool leida
    }
    HISTORIAL_ESTADOS {
        int id
        string entidad "PEDIDO|ENTREGA"
        int entidad_id
        int usuario_id "nulo = automatización"
        string estado_anterior
        string estado_nuevo
        string observacion
        datetime fecha
    }
```

## Reglas de negocio asociadas

1. Un pedido genera **a lo sumo una entrega** (1:1); la entrega se crea al asignar.
2. Transiciones válidas de pedido: `RECIBIDO→PREPARANDO`, `RECIBIDO/PREPARANDO→ASIGNADO`
   (al asignar), `*→ENTREGADO` (al entregarse su entrega), `*→CANCELADO`
   (salvo ya entregado o con entrega en ruta).
3. Transiciones válidas de entrega: `ASIGNADO→EN_CAMINO` (salida),
   `EN_CAMINO→ENTREGADO`, `ASIGNADO/EN_CAMINO→INCIDENCIA` (reporte),
   `INCIDENCIA→EN_CAMINO` (resolución por el administrador).
4. Toda transición escribe en `HISTORIAL_ESTADOS` (usuario, fecha, acción, resultado).
5. La automatización no duplica alertas: existe a lo sumo una alerta **activa**
   por entrega y nivel.
6. La hora límite debe ser futura al registrar el pedido (validación de entrada).
7. El tiempo de entrega se calcula como `hora_entrega − (hora_salida o hora_asignacion)`;
   una entrega es "a tiempo" si `hora_entrega ≤ hora_limite`.
