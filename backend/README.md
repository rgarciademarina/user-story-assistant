# User Story Assistant Backend

Este es el backend del User Story Assistant, una aplicación que ayuda a refinar y mejorar historias de usuario.

## Estructura del Proyecto

```
backend/
├── src/                # Código fuente
│   ├── api/           # Endpoints y rutas de la API
│   ├── config/        # Configuraciones
│   ├── core/          # Lógica de negocio principal
│   ├── llm/           # Servicios de LLM
│   ├── models/        # Modelos de datos
│   └── utils/         # Utilidades
├── tests/             # Tests
│   ├── unit/         # Tests unitarios
│   ├── integration/  # Tests de integración
│   └── mocks/        # Mocks para testing
└── requirements.txt   # Dependencias
```

## Configuración del Entorno

1. Instalar Poetry (si no está instalado):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Instalar dependencias:
```bash
poetry install
```

3. Activar el entorno virtual:
```bash
poetry shell
```

## Ejecutar Tests

```bash
poetry run pytest
```

## Ejecutar el Servidor

```bash
poetry run python src/main.py
