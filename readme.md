## Índice

0. [Ficha del proyecto](#0-ficha-del-proyecto)
1. [Descripción general del producto](#1-descripción-general-del-producto)
2. [Instalación y Configuración](#2-instalación-y-configuración)
3. [Arquitectura del sistema](#3-arquitectura-del-sistema)
   - [3.1. Diagrama de arquitectura](#31-diagrama-de-arquitectura)
   - [3.2. Descripción de componentes principales](#32-descripción-de-componentes-principales)
   - [3.3. Descripción de alto nivel del proyecto y estructura de ficheros](#33-descripción-de-alto-nivel-del-proyecto-y-estructura-de-ficheros)
4. [Tests y CI/CD](#4-tests-y-cicd)
   - [4.1. Estado de los Tests](#41-estado-de-los-tests)
   - [4.2. Ejecutar Tests Localmente](#42-ejecutar-tests-localmente)
   - [4.3. Requisitos de Calidad](#43-requisitos-de-calidad)
   - [4.4. Proceso de Pull Request](#44-proceso-de-pull-request)
   - [4.5. GitHub Actions Workflow](#45-github-actions-workflow)
5. [Especificación de la API](#5-especificación-de-la-api)
6. [Historias de usuario](#6-historias-de-usuario)
7. [Tickets de trabajo](#7-tickets-de-trabajo)
8. [Pull requests](#8-pull-requests)
9. [Roadmap](#9-roadmap)

---

## 0. Ficha del proyecto

### **0.1. Autor:**

rgarciademarina

### **0.2. Nombre del proyecto:**

Refinador de Historias de Usuario

### **0.3. Descripción breve del proyecto:**

Un asistente que usará un LLM para ayudar con el proceso de refinamiento de historias de usuario de un equipo de desarrollo.

### **0.4. URL del proyecto:**

[https://github.com/rgarciademarina/user-story-assistant](https://github.com/rgarciademarina/user-story-assistant)

---

## 1. Descripción general del producto

El Asistente de Refinamiento de Historias de Usuario es una herramienta basada en IA que asiste a los equipos de desarrollo en la mejora de sus historias de usuario a través de un proceso guiado de tres pasos. Utiliza Ollama con un modelo LLM configurable mediante variables de entorno, permitiendo flexibilidad en la selección del modelo de lenguaje.

## 2. Instalación y Configuración

Para instrucciones detalladas de instalación y configuración, por favor consulte:

- [Instrucciones del Backend](./backend/README.md)
- [Instrucciones del Frontend](./frontend/README.md)

---

## 3. Arquitectura del sistema

### **3.1. Diagrama de arquitectura**

```mermaid
classDiagram
    class FrontendApp {
        +RefinementFlow
        +ChatMessage
        +store: Pinia
        +handleUserInput()
        +updateStoryState()
    }

    class RefinementFlow {
        -currentStep: string
        -storyData: Object
        +nextStep()
        +previousStep()
        +updateStory()
    }

    class ChatMessage {
        -message: string
        -type: string
        +render()
    }

    class BackendAPI {
        +FastAPI
        +handleRequest()
        +validateInput()
        +processStory()
    }

    class LLMService {
        -model: Llama32
        -prompts: PromptManager
        +generateRefinements()
        +analyzeCornerCases()
        +suggestTests()
    }

    class PromptManager {
        +refinementPrompt: string
        +cornerCasePrompt: string
        +testingPrompt: string
        +getContextualPrompt()
    }

    class DatabaseService {
        +PostgreSQL
        +storeStory()
        +retrieveHistory()
        +updateStatus()
    }

    class JiraIntegration {
        +syncStory()
        +updateTicket()
        +fetchMetadata()
    }

    FrontendApp --> RefinementFlow
    FrontendApp --> ChatMessage
    RefinementFlow ..> BackendAPI: HTTP/REST
    BackendAPI --> LLMService
    LLMService --> PromptManager
    BackendAPI --> DatabaseService
    BackendAPI --> JiraIntegration
```

### **3.2. Descripción de componentes principales**

En esta sección se describen los componentes más importantes del sistema, incluyendo la tecnología utilizada.

#### **LLM Service**

- **Tecnología principal**: Llama 3.2:11b
- **Framework**: LangChain
- **Propósito**: Gestionar la interacción con el modelo de lenguaje para el análisis y generación de sugerencias.
- **Características clave**:
  - Gestión de prompts
  - Control de contexto
  - Manejo de tokens
  - Procesamiento de respuestas

#### **API Service**

- **Framework**: FastAPI
- **Base de datos**: PostgreSQL
- **Propósito**: Proporcionar la interfaz REST para la aplicación.
- **Características clave**:
  - Autenticación y autorización
  - Validación de datos
  - Documentación automática
  - Gestión de sesiones

#### **Conectores**

- **Integraciones**: Jira, GitHub
- **Propósito**: Integración con sistemas existentes para sincronización de datos.
- **Características clave**:
  - Sincronización de historias de usuario
  - Actualización de estados
  - Gestión de webhooks

#### **Frontend**

- **Framework**: Vue.js o React (dependiendo de la elección)
- **Propósito**: Proporcionar una interfaz de usuario interactiva.
- **Características clave**:
  - Interfaz intuitiva
  - Visualización de resultados
  - Feedback en tiempo real

### **3.3. Descripción de alto nivel del proyecto y estructura de ficheros**

El proyecto está organizado en dos componentes principales:

```
user-story-assistant/
├── backend/           # Servidor backend en Python
│   ├── src/          # Código fuente del backend
│   │   ├── api/      # Endpoints y rutas de la API
│   │   ├── config/   # Configuraciones
│   │   ├── core/     # Lógica de negocio principal
│   │   ├── llm/      # Servicios de LLM
│   │   ├── models/   # Modelos de datos
│   │   └── utils/    # Utilidades
│   ├── tests/        # Tests del backend
│   └── README.md     # Documentación del backend
│
├── frontend/         # Cliente frontend en Vue.js
│   ├── src/         # Código fuente del frontend
│   ├── tests/       # Tests del frontend
│   └── README.md    # Documentación del frontend
│
├── docs/            # Documentación general
└── README.md        # Este archivo
```

Esta estructura separa claramente las responsabilidades entre el backend y el frontend, facilitando:
- Desarrollo independiente de cada componente
- Despliegues separados
- Gestión independiente de dependencias
- Equipos trabajando en paralelo

---

## 4. Tests y CI/CD

### **4.1. Estado de los Tests**

- **Tests Unitarios**: Cubren la lógica de negocio y componentes individuales.
- **Tests de Integración**: Verifican la interacción entre componentes y servicios.
- **Tests End-to-End**: Simulan el flujo de usuario completo.

### **4.2. Ejecutar Tests Localmente**

1. **Tests del Backend**:
   ```bash
   cd backend
   poetry run pytest
   ```

2. **Tests del Frontend**:
   ```bash
   cd frontend
   npm run test:unit
   ```

### **4.3. Requisitos de Calidad**

- **Cobertura de Código**: 80% como mínimo.
- **Complejidad Ciclomática**: Menos de 10.

### **4.4. Proceso de Pull Request**

1. **Crear una Rama**: Desde `main`, crea una rama con el nombre del feature o fix.
2. **Desarrollar y Probar**: Implementa el cambio y ejecuta los tests locales.
3. **Crear Pull Request**: En GitHub, crea un PR desde tu rama hacia `main`.
4. **Revisión de Código**: Otro miembro del equipo revisa el código y aprueba.
5. **Merge**: Una vez aprobado, se mergea el PR hacia `main`.

### **4.5. GitHub Actions Workflow**

#### Descripción del Workflow de Integración Continua

El proyecto utiliza GitHub Actions para automatizar la ejecución de tests en cada pull request y push a las ramas principales. El workflow está diseñado para garantizar la calidad del código mediante una serie de pasos automatizados:

1. **Checkout del Código**
   - Descarga la última versión del código del repositorio
   - Prepara el entorno para ejecutar los tests

2. **Configuración del Entorno de Backend**
   - Instala Python en la versión 3.10
   - Configura Poetry para gestión de dependencias
   - Instala todas las dependencias del proyecto de backend
   - Ejecuta los tests de Python utilizando pytest
   - Genera informe de cobertura de código

3. **Configuración del Entorno de Frontend**
   - Instala Node.js versión 20.x
   - Configura npm para gestión de dependencias
   - Instala todas las dependencias del proyecto frontend
   - Ejecuta tests unitarios de Vue.js
   - Genera informe de cobertura de código

4. **Verificación de Cobertura de Código**
   - Analiza los informes de cobertura de backend y frontend
   - Requiere un mínimo del 80% de cobertura de código
   - Almacena los informes de cobertura como artefactos
   - Bloquea la integración si no se alcanza el umbral de cobertura

5. **Desencadenantes del Workflow**
   - Se activa automáticamente en:
     * Pull requests a las ramas `main` y `develop`
     * Pushes directos a `main` y `develop`
   - Permite detectar problemas antes de mergear código

#### Beneficios del Workflow

- **Detección Temprana de Errores**: 
  - Ejecuta tests automáticamente antes de mergear código
  - Identifica problemas de compatibilidad o regresiones

- **Consistencia**: 
  - Asegura que todos los tests pasen en el entorno de desarrollo
  - Mantiene un estándar de calidad en cada contribución

- **Transparencia**: 
  - Muestra el estado de los tests directamente en GitHub
  - Proporciona retroalimentación inmediata a los desarrolladores

- **Calidad de Código**: 
  - Previene la introducción de código que rompa los tests existentes
  - Garantiza un nivel mínimo de cobertura de código
  - Facilita la revisión y mejora continua del proyecto

#### Visualización de Resultados

Los resultados de los tests se pueden ver:
- En la pestaña "Actions" del repositorio de GitHub
- Como checks de status en cada pull request
- Notificaciones por correo en caso de fallos

**Nota**: Para contribuir al proyecto, asegúrate de que todos los tests pasen y se alcance el 80% de cobertura de código antes de crear un pull request.

---

## 5. Especificación de la API

> Detalla los endpoints de la API, métodos soportados, parámetros, respuestas y posibles códigos de estado.

*(Contenido omitido)*

## 6. Historias de usuario

### **Prioridad 1 (Crítica):**
- US-001: Crear Historia de Usuario
- US-002: Crear Proyecto
- US-004: Importar Historia desde Jira
- US-006: Iniciar Refinamiento
- US-007: Ejecutar Paso de Refinamiento

**Prioridad 2 (Importante):**
- US-003: Configurar Integraciones
- US-008: Revisar Casos Esquina
- US-010: Actualizar Historia en Jira

**Prioridad 3 (Deseable):**
- US-005: Crear Historia Manual
- US-009: Generar Recomendaciones de Testing

### **5.8. Ejemplo de Criterios de Aceptación Detallados**

Para US-007: Ejecutar Paso de Refinamiento

**Criterios de Aceptación:**
- LLM respondiendo correctamente
- Prompts funcionando según esperado
- Cache implementado
- Tests de integración pasando

## 7. Tickets de trabajo

> Lista y describe los tickets de trabajo necesarios para el desarrollo del proyecto.

### **6.5. API Core**

#### TECH-008: Endpoints de Proyectos
**Tipo:** Tarea Técnica  
**Prioridad:** Alta  
**Estimación:** 3 puntos  
**Dependencias:** TECH-002, TECH-003

**Descripción:**
- Implementar CRUD de proyectos
- Crear validaciones
- Implementar filtros y búsqueda
- Añadir paginación

#### TECH-009: Endpoints de Historias
**Tipo:** Tarea Técnica  
**Prioridad:** Alta  
**Estimación:** 5 puntos  
**Dependencias:** TECH-004, TECH-008

**Descripción:**
- Implementar CRUD de historias
- Crear sincronización con Jira
- Implementar validaciones
- Añadir búsqueda y filtros

### **6.6. Proceso de Refinamiento**

#### TECH-010: Motor de Refinamiento
**Tipo:** Tarea Técnica  
**Prioridad:** Alta  
**Estimación:** 13 puntos  
**Dependencias:** TECH-007, TECH-009

**Descripción:**
- Implementar máquina de estados
- Crear pipeline de procesamiento
- Implementar análisis de completitud
- Crear detector de casos esquina
- Implementar generador de tests

**Criterios de Aceptación:**
- Pipeline completo funcionando
- Casos esquina detectados correctamente
- Sugerencias de test generadas
- Tests de integración pasando

#### TECH-011: Setup Frontend
**Tipo:** Tarea Técnica  
**Prioridad:** Media  
**Estimación:** 5 puntos  
**Dependencias:** TECH-003

**Descripción:**
- Configurar entorno de desarrollo frontend
- Integrar con backend
- Implementar autenticación de usuarios
- Desarrollar componentes básicos de la interfaz

## 8. Pull requests

> Documenta 3 de las Pull Requests realizadas durante la ejecución del proyecto

**Pull Request 1**

- **Título:** Implementación del servicio LLM
- **Descripción:** Añade el servicio LLM utilizando LangChain y configura las integraciones necesarias.
- **Cambios Principales:**
  - Añadidos archivos en `src/llm/`
  - Configuración de prompts en `src/llm/prompts/`
  - Tests unitarios para el servicio LLM
- **Estado:** Mergeado

**Pull Request 2**

- **Título:** Desarrollo de la Interfaz Gráfica con LangFlow
- **Descripción:** Crea la interfaz gráfica básica utilizando LangFlow para la interacción con el asistente de refinamiento.
- **Cambios Principales:**
  - Añadidos archivos en `src/ui/`
  - Configuración de LangFlow en `src/ui/app.py`
  - Documentación de uso de la interfaz gráfica
- **Estado:** Pendiente

**Pull Request 3**

- **Título:** Integración con Jira Local
- **Descripción:** Implementa el conector para Jira local usando la biblioteca `atlassian-python-api`.
- **Cambios Principales:**
  - Añadidos archivos en `src/integrations/jira/`
  - Configuración de clientes Jira en `src/integrations/jira/client.py`
  - Tests de integración para el conector Jira
- **Estado:** Pendiente

## Interfaz Gráfica con LangFlow

### Instalación

1. **Navega al directorio del frontend:**
    ```bash
    cd src/ui
    ```

2. **Instala las dependencias:**
    ```bash
    npm install
    # o si usas Yarn
    yarn install
    ```

3. **Ejecuta la aplicación:**
    ```bash
    npm run serve
    # o si usas Yarn
    yarn serve
    ```

### Uso

1. **Accede a la interfaz gráfica:**
   Abre tu navegador y ve a `http://localhost:8080` (o el puerto que hayas configurado).

2. **Proceso de Refinamiento:**
   - **Paso 1: Mejora de Definición**
     - Ingresa una historia de usuario en el formulario.
     - Visualiza la historia refinada y confirma para avanzar.
   - **Paso 2: Identificación de Casos Esquinas**
     - Revisa los casos esquinas identificados.
     - Confirma para avanzar.
   - **Paso 3: Estrategia de Testing**
     - Revisa las estrategias de testing recomendadas.
     - Confirma para finalizar el proceso.

### Capturas de Pantalla

![Interfaz de Refinamiento Paso 1](ruta/a/tu/captura_paso1.png)
![Interfaz de Refinamiento Paso 2](ruta/a/tu/captura_paso2.png)
![Interfaz de Refinamiento Paso 3](ruta/a/tu/captura_paso3.png)

## 9. Roadmap

El siguiente roadmap describe las funcionalidades planificadas para futuras versiones del asistente.

### **9.1. Q1 2025**

#### Mejoras Base
- Optimización de prompts y respuestas
- Mejora de la interfaz actual
- Documentación completa
- Corrección de bugs reportados
- Implementación de streaming de respuestas de LLM
  * Mostrar respuestas en tiempo real, similar a ChatGPT
  * Reducir la percepción de latencia para el usuario
  * Mejorar la experiencia de usuario durante el refinamiento
- Optimización de la generación de prompts
- Mejora de la precisión en la identificación de casos esquina

#### Testing y Calidad
- Tests end-to-end con Selenium y Cucumber (BDD)
- Tests de rendimiento con k6
- Monitorización de tiempos de respuesta

#### Autenticación y Persistencia
- Sistema de login con múltiples proveedores
- Persistencia de sesiones
- Gestión de perfiles de usuario
- Control de acceso basado en roles

#### Internacionalización
- Soporte de idiomas (español e inglés)
- Traducción de interfaces
- Gestión de recursos i18n
- Detección automática de idioma

### **9.2. Q2-Q3 2025**

#### Integración y Conectividad
- Sistema RAG para contexto de proyecto desde Jira
- Integración con Confluence para documentación
- Conexión con GitHub para seguimiento de código
- API pública para integraciones personalizadas

#### Personalización
- Configuración flexible de pasos de refinamiento
- Selección de formatos (Gherkin, Given-When-Then, etc.)
- Templates personalizables por equipo
- Configuración de reglas de validación

### **9.3. Q4 2025 - Q1 2026**

#### Análisis y Mejora Continua
- Sistema de feedback para el LLM
- Métricas de calidad de historias
- Dashboard de analytics
- Detección de patrones problemáticos

#### Colaboración en Tiempo Real
- Sesiones multiusuario
- Comentarios y anotaciones
- Sistema de votación
- Historial de cambios con diff

#### Automatización Avanzada
- Generación de diagramas técnicos
- Estimación automática
- Análisis de dependencias
- Detección de duplicados

### **9.4. 2026**

#### Integración con Desarrollo
- Generación de código base
- Sugerencia de tests
- Vinculación con PRs
- Análisis de impacto

#### Gestión del Conocimiento
- Base de conocimiento auto-mantenida
- Captura de decisiones técnicas
- Vinculación con documentación
- Templates evolutivos

#### Calidad y Cumplimiento
- Verificación de compliance
- Chequeo de seguridad
- Validación contra estándares
- Sistema de alertas

#### Experiencia de Usuario
- Interfaz adaptativa según rol/experiencia
- Atajos de teclado personalizables
- Temas visuales y accesibilidad

### **9.5. Priorización y Feedback**

Las prioridades del roadmap se ajustarán según:
- Feedback de usuarios
- Necesidades del mercado
- Viabilidad técnica
- Valor añadido al producto

Para sugerir nuevas funcionalidades o prioridades, por favor:
1. Abre un issue con la etiqueta "feature-request"
2. Describe el caso de uso y beneficios
3. Proporciona ejemplos si es posible