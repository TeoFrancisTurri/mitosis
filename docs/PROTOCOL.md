# Protocolo de Red

## Transporte

- **Protocolo:** TCP
- **Host:** `127.0.0.1`
- **Puerto:** `5000`
- **Encoding:** UTF-8
- **Formato:** JSON separado por newline (`\n`)
- **Buffer:** 4096 bytes

Cada mensaje es un objeto JSON en una sola línea terminada en `\n`. Todos los mensajes tienen el campo `type` que identifica el tipo.

---

## Mensajes Cliente → Servidor

### `CONNECT`
Enviado al conectarse. Registra al jugador en una partida.

```json
{
  "type": "CONNECT",
  "username": "Player"
}
```

### `PLAYER_INPUT`
Enviado cada frame con la dirección del mouse normalizada.

```json
{
  "type": "PLAYER_INPUT",
  "direction_x": 0.71,
  "direction_y": -0.71
}
```


### `SPLIT`
Divide todas las células del jugador que tengan masa suficiente.

```json
{ "type": "SPLIT" }
```

### `EJECT`
Eyecta una porción de masa desde cada célula en la dirección actual.

```json
{ "type": "EJECT" }
```

### `RESPAWN`
Solicita reencarnar después de morir.

```json
{ "type": "RESPAWN" }
```

### `DISCONNECT`
Notifica al servidor que el cliente se desconecta voluntariamente.

```json
{ "type": "DISCONNECT" }
```

---

## Mensajes Servidor → Cliente

### `MATCH_FOUND`
Enviado tras `CONNECT`. Confirma que el jugador fue asignado a una partida.

```json
{
  "type": "MATCH_FOUND",
  "player_id": 3
}
```

### `GAME_STATE`
Enviado 30 veces por segundo con el estado completo del mundo visible.

```json
{
  "type": "GAME_STATE",
  "tick": 120,
  "snapshot": {
    "players": [ ... ],
    "foods":   [ ... ],
    "viruses": [ ... ],
    "leaderboard": [ ... ]
  }
}
```

### `PLAYER_DEAD`
Enviado cuando el jugador pierde todas sus células.

```json
{
  "type": "PLAYER_DEAD",
  "stats": {
    "food_eaten": 42,
    "cells_eaten": 1,
    "highest_mass": 380,
    "leaderboard_time": 15.3,
    "top_position": 2,
    "time_alive": 87.4
  }
}
```

### `DISCONNECT`
Enviado por el servidor cuando cierra la conexión de forma forzada.

```json
{ "type": "DISCONNECT" }
```

---

## Formato del Snapshot

### Célula de jugador (`players`)

Cada jugador puede tener múltiples células (tras hacer split). Cada célula es un objeto independiente con el mismo `id`.

```json
{
  "id": 3,
  "username": "Teo",
  "x": 1042.5,
  "y": 873.1,
  "radius": 35,
  "mass": 78.4,
  "color": [80, 160, 255]
}
```

### Comida (`foods`)

```json
{
  "id": 17,
  "x": 500.0,
  "y": 300.0,
  "radius": 5,
  "mass": 3,
  "color": [255, 80, 80]
}
```

La comida ejectada (`W`) tiene velocidad inicial y se mueve hasta detenerse. Es funcionalmente idéntica a la comida normal para el cliente.

### Virus (`viruses`)

```json
{
  "id": 2,
  "x": 750.0,
  "y": 400.0,
  "radius": 40,
  "color": [33, 210, 0]
}
```

### Leaderboard (`leaderboard`)

Lista de los 5 jugadores con más masa, ordenados de mayor a menor. Incluye al jugador local aunque no esté en el top 5.

```json
[
  { "id": 1, "username": "Alpha", "position": 1 },
  { "id": 3, "username": "Teo",   "position": 2 }
]
```

