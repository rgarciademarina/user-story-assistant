# User Story Assistant Backend

Backend de la aplicación User Story Assistant, una herramienta basada en IA para refinar y mejorar historias de usuario utilizando Ollama y LLM.

## Características Principales

- Integración con Ollama para procesamiento de lenguaje natural
- Endpoints REST para refinamiento de historias de usuario
- Procesamiento de prompts contextuales
- Análisis de casos esquina
- Generación de estrategias de testing

## Estructura del Proyecto

```
backend/
├── src/                # Código fuente
│   ├── api/           # Endpoints y rutas de la API
│   ├── config/        # Configuraciones
│   ├── core/          # Lógica de negocio principal
│   ├── llm/           # Servicios de LLM
│   │   ├── prompts/   # Gestión de prompts
│   │   ├── config.py  # Configuración del LLM
│   │   ├── instance.py# Instanciación de modelos
│   │   ├── models.py  # Modelos relacionados con LLM
│   │   └── service.py # Servicio principal de LLM
│   ├── models/        # Modelos de datos
│   └── utils/         # Utilidades
├── tests/             # Tests
│   ├── unit/         # Tests unitarios
│   └── api/          # Tests de API
└── pyproject.toml    # Configuración de Poetry y dependencias
```

## Requisitos Previos

- Python 3.10+
- Poetry
- Ollama

## Configuración del Entorno

1. Instalar Poetry (si no está instalado):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Instalar dependencias:
```bash
poetry install
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con la configuración de Ollama
```

## Ejecutar Aplicación

### Modo Desarrollo

```bash
poetry run uvicorn src.main:app --reload --port 8000
```

### Modo Producción

```bash
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Ejecutar Tests

### Tests Unitarios
```bash
poetry run pytest tests/unit
```

### Tests de API
```bash
poetry run pytest tests/api
```

## Desarrollo y Contribución

1. Crear una rama desde `main`
2. Implementar cambios
3. Añadir tests
4. Ejecutar tests localmente
5. Crear Pull Request

## Tecnologías Principales

- FastAPI
- Ollama
- LangChain
- Pydantic
- pytest

## Problemas Comunes

- Asegurarse de que Ollama está ejecutándose
- Verificar la configuración de variables de entorno
- Comprobar la versión de Python

## Licencia

MIT License

Copyright (c) 2024 Raúl García de Marina

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
