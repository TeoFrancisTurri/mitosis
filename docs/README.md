# Agario Clone

Clon del juego [agar.io](https://agar.io) desarrollado en Python con pygame. Arquitectura cliente-servidor: el servidor maneja toda la lógica del juego y el cliente se encarga exclusivamente del renderizado y la entrada del usuario.

## Requisitos

- Python 3.12+
- pygame 2.6.1

```bash
pip install pygame
```

## Cómo correr

El servidor y el cliente se corren por separado desde la raíz del proyecto.

**Servidor:**
```bash
python -m server.main
```

**Cliente:**
```bash
python -m client.main
```

El servidor escucha en `127.0.0.1:5000` por defecto. Se pueden conectar múltiples clientes.

## Controles

| Tecla | Acción |
|-------|--------|
| Mouse | Dirección de movimiento |
| `Espacio` | Split (dividir célula) |
| `W` | Eject (eyectar masa) |
| `Escape` | Salir de la partida |

## Mecánicas

- **Comer comida:** aumenta la masa de la célula.
- **Comer jugador:** una célula puede comer a otra si tiene al menos 1.3× su masa.
- **Split:** divide cada célula en dos. Máximo 16 células simultáneas.
- **Eject:** lanza una pequeña porción de masa hacia el cursor. Puede alimentar virus.
- **Virus:** al comerlo, la célula explota en múltiples fragmentos. Se alimentan con masa ejectada y se replican al alcanzar cierta masa.
- **Fusión:** las células divididas se fusionan automáticamente después de un tiempo.
- **Zoom:** la cámara se aleja al dividirse en más células y vuelve al fusionarse.

## Estructura del proyecto

```
agario/
├── client/
│   ├── camera/         # Lógica de cámara y zoom
│   ├── config/         # Configuración del cliente (red, UI, cámara)
│   ├── core/           # Game loop principal
│   ├── managers/       # SnapshotManager
│   ├── network/        # Conexión TCP y mensajes al servidor
│   ├── states/         # Estados del juego (menú, jugando, respawn, error)
│   ├── ui/             # Componentes de interfaz reutilizables
│   └── main.py
│
├── server/
│   ├── config/         # Configuración del servidor (jugador, comida, virus, match)
│   ├── entities/       # Cell, Player, Food, Virus
│   ├── managers/       # PlayerManager, FoodManager, VirusManager, CollisionManager
│   ├── match/          # Lógica de partida y tick
│   ├── matchmaking/    # Asignación de jugadores a partidas
│   ├── network/        # Servidor TCP y manejo de mensajes entrantes
│   └── main.py
│
├── shared/
│   ├── config/         # Configuración compartida (mapa, red)
│   └── protocol/       # Tipos de mensajes y campos del protocolo
│
└── docs/
    ├── README.md
    └── PROTOCOL.md
```

## Arquitectura

```
Cliente                          Servidor
  │                                  │
  │──── CONNECT (username) ─────────>│
  │<─── MATCH_FOUND (player_id) ─────│
  │                                  │
  │──── PLAYER_INPUT (dx, dy) ──────>│  ← cada frame
  │<─── GAME_STATE (snapshot) ───────│  ← 30 veces por segundo
  │                                  │
  │      ... jugando ...             │
  │                                  │
  │<─── PLAYER_DEAD (stats) ─────────│
  │──── RESPAWN ────────────────────>│
  │                                  │
  │──── DISCONNECT ─────────────────>│
```

**Flujo del servidor (por tick):**
1. Procesar inputs recibidos de los clientes
2. Actualizar posiciones y velocidades (`PlayerManager`, `FoodManager`, `VirusManager`)
3. Detectar colisiones (`CollisionManager`)
4. Enviar snapshot del estado del mundo a todos los clientes

**Flujo del cliente (por frame):**
1. Enviar dirección del mouse al servidor
2. Recibir y almacenar el último snapshot
3. Renderizar el snapshot con interpolación de cámara y zoom
