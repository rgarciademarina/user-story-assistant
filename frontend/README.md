# User Story Assistant Frontend

Frontend de la aplicación User Story Assistant, una herramienta basada en IA para refinar y mejorar historias de usuario utilizando Ollama y Vue.js.

## Características Principales

- Interfaz moderna y responsiva
- Integración con backend basado en Ollama
- Refinamiento de historias de usuario mediante IA
- Visualización interactiva de resultados
- Soporte para múltiples modelos LLM

## Estructura del Proyecto

```
frontend/
├── public/            # Recursos públicos
├── src/               # Código fuente
│   ├── assets/        # Recursos estáticos
│   ├── components/    # Componentes Vue
│   ├── styles/        # Estilos globales
│   ├── views/         # Vistas de la aplicación
│   ├── store/         # Gestión de estado
│   ├── App.vue        # Componente raíz de Vue
│   └── main.js        # Punto de entrada de la aplicación
├── tests/             # Tests
├── node_modules/      # Dependencias
├── package.json       # Configuración de dependencias
├── babel.config.js    # Configuración de Babel
├── vue.config.js      # Configuración de Vue
└── wdio.*.conf.js     # Configuraciones de WebdriverIO
```

## Requisitos Previos

- Node.js 20.x
- npm
- Backend de User Story Assistant en ejecución

## Configuración del Entorno

1. Instalar dependencias:
```bash
npm install
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con la URL del backend
```

## Ejecutar Aplicación

### Modo Desarrollo

```bash
npm run serve
```

### Compilar para Producción

```bash
npm run build
```

## Ejecutar Tests

### Tests Unitarios
```bash
npm run test:unit
```

### Tests End-to-End
```bash
npm run test:e2e
```

## Desarrollo y Contribución

1. Crear una rama desde `main`
2. Implementar cambios
3. Añadir tests
4. Ejecutar tests localmente
5. Crear Pull Request

## Tecnologías Principales

- Vue.js 3
- Vuex
- Axios
- Tailwind CSS
- Vite

## Problemas Comunes

- Verificar configuración de variables de entorno
- Asegurarse de que el backend está en ejecución
- Comprobar versión de Node.js

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

### Configuración Personalizada
Consultar [Referencia de Configuración de Vue CLI](https://cli.vuejs.org/config/).
