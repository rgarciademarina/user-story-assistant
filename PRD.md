# PRD: Asistente de Refinamiento de Historias de Usuario - Prueba de Concepto

## 1. Objetivo

Desarrollar una **Prueba de Concepto (POC)** para validar la viabilidad del **Asistente de Refinamiento de Historias de Usuario** utilizando un modelo LLM con capacidades de visión, aprovechando los recursos locales del desarrollador.

## 2. Alcance

La POC se centrará en:

- Implementación de un flujo de refinamiento básico de historias de usuario en tres pasos.
- Integración con un modelo LLM local (**Llama 3.2:11b**) con capacidades de visión.
- Desarrollo de una interfaz gráfica sencilla utilizando **LangFlow**.
- Conexión a un sistema Jira local para la gestión de historias de usuario.
- Evaluación de la efectividad del modelo y la facilidad de uso de la interfaz.

**Fuera del Alcance:**

- Integraciones con sistemas externos en la nube como Confluence o GitHub.
- Funcionalidades avanzadas de gestión de estado y persistencia.
- Despliegue en entornos de producción o en la nube.

## 3. Características y Funcionalidades

### 3.1. Proceso de Refinamiento

Implementar un flujo de trabajo en tres pasos secuenciales, cada uno requiriendo confirmación del usuario para avanzar:

1. **Mejora de Definición**
   - Refinar la descripción de la historia de usuario.
   - Sugerencias para mejorar la claridad y completitud.

2. **Identificación de Casos Esquinas**
   - Identificar posibles escenarios límite o riesgos.
   - Documentar casos de prueba adicionales.

3. **Estrategia de Testing**
   - Proponer estrategias de pruebas basadas en la historia refinada.
   - Recomendaciones de tipos de tests necesarios.

### 3.2. Integración con Modelo LLM

- **Modelo Utilizado**: Llama 3.2:11b con capacidades de visión.
- **Ejecución Local**: Aprovechar la potencia de la máquina local (RTX 4090, AMD 7800X3D, 64GB DDR5) para correr el modelo sin problemas.
- **Framework**: Utilizar **LangChain** para gestionar la interacción con el modelo LLM.

### 3.3. Interfaz Gráfica

- **Herramienta**: **LangFlow**
- **Características**:
  - Interfaz intuitiva para ingresar y visualizar historias de usuario.
  - Visualización de las recomendaciones generadas por el asistente.
  - Facilitar iteraciones rápidas durante la POC.

### 3.4. Integración con Jira Local

- **Sistema Jira**: Instalación local de Jira para gestión de historias de usuario.
- **Conector Jira**:
  - **Funcionalidades**:
    - Recuperación de historias de usuario desde Jira local.
    - Sincronización básica de estados de historias.
    - Acceso a detalles específicos de cada historia (título, descripción, criterios de aceptación).
  - **Tecnologías**:
    - Utilizar la API REST de Jira para interacción.
    - Librería `jira` para facilitar las llamadas a la API desde Python.
  - **Configuración Inicial**:
    - Configuración de las credenciales de acceso a Jira local.
    - Definición de endpoints y parámetros necesarios para la comunicación.

## 4. Stack Tecnológico

- **Lenguaje de Programación**: Python 3.11
- **LLM**: Llama 3.2:11b (ejecutado localmente)
- **Frameworks**:
  - **LangChain**: Gestión de flujos de trabajo y prompts.
  - **LangFlow**: Desarrollo de la interfaz gráfica.
- **Entorno de Desarrollo**:
  - **Poetry**: Gestión de dependencias y entornos virtuales.
- **Herramientas Adicionales**:
  - **Jira Local**: Instalación local para gestión de historias de usuario.
  - **Librería `jira`**: Interacción con la API de Jira desde Python.

## 5. Infraestructura y Despliegue

### 5.1. Configuración del Entorno Local

- **Hardware**:
  - **GPU**: NVIDIA RTX 4090
  - **CPU**: AMD Ryzen 7 7800X3D
  - **Memoria**: 64GB DDR5
- **Software**:
  - **Sistema Operativo**: Preferiblemente Linux para mejor compatibilidad.
  - **Poetry**: Instalación para gestión de dependencias.
  - **LangChain & LangFlow**: Instalación a través de Poetry.
  - **Jira Server**: Instalación y configuración local según documentación oficial.

### 5.2. Instalación y Configuración

1. **Clonar el Repositorio**
    ```bash
    git clone https://github.com/rgarciademarina/AI4Devs-finalproject-RGM.git
    cd AI4Devs-finalproject-RGM
    ```

2. **Configurar el Entorno Virtual**
    ```bash
    poetry install
    poetry shell
    ```

3. **Configurar Jira Local**
    - **Descargar e Instalar Jira Server** desde [Atlassian](https://www.atlassian.com/software/jira/download).
    - **Configurar el acceso a la API**:
      - Crear una API Token si es necesario.
      - Definir los permisos adecuados para la aplicación.
    - **Actualizar la configuración del conector en el proyecto** con las credenciales y URLs locales.

4. **Ejecutar el Modelo LLM Localmente**
    ```bash
    # Asumiendo que tienes los pesos del modelo descargados
    python src/llm/run_model.py --model llama-3.2-11b
    ```

5. **Desarrollar la Interfaz con LangFlow**
    ```bash
    langflow run src/ui/app.py
    ```

## 6. Métricas de Éxito

- **Funcionalidad**: El asistente puede procesar historias de usuario y proporcionar mejoras, identificar casos esquina y sugerir estrategias de testing.
- **Rendimiento**: Respuestas generadas en un tiempo razonable (menos de 5 segundos por interacción).
- **Usabilidad**: Interfaz gráfica intuitiva y fácil de usar para los usuarios finales.
- **Integración con Jira**: Capacidad de recuperar y sincronizar historias de usuario desde Jira local.
- **Validación del Modelo**: El modelo Llama 3.2:11b proporciona respuestas precisas y relevantes.

## 7. Limitaciones

- **Alcance Reducido**: La POC se enfoca únicamente en las funcionalidades básicas de refinamiento sin integraciones externas en la nube.
- **Recursos Locales**: Dependencia total en la máquina local del desarrollador para la ejecución del modelo LLM y Jira.
- **Interfaz Básica**: La interfaz gráfica desarrollada con LangFlow es sencilla, enfocada en la validación rápida.
- **Jira Local**: Limitada a la funcionalidad básica de Jira, sin explorar todas las capacidades de la API.

## 8. Consideraciones Futuras

- **Integraciones Externas**: Conectar con Confluence y GitHub para automatizar la extracción y actualización de datos.
- **Despliegue en la Nube**: Migrar la POC a entornos en la nube para escalabilidad y accesibilidad.
- **Mejoras en la Interfaz**: Desarrollar una interfaz más robusta y personalizada basada en feedback de usuarios.
- **Optimización del Modelo**: Ajustar y optimizar el modelo Llama 3.2:11b para mejorar la precisión y eficiencia.
- **Automatización de Jira**: Implementar funcionalidades avanzadas de sincronización y automatización con Jira.

## 9. Riesgos y Mitigaciones

| Riesgo                                    | Impacto       | Mitigación                                       |
|-------------------------------------------|---------------|-------------------------------------------------|
| **Limitaciones de Hardware**             | Alto          | Validar compatibilidad y optimizar uso de recursos.|
| **Complejidad en la Configuración de Jira Local** | Medio      | Documentar claramente los pasos de instalación.   |
| **Tiempo de Desarrollo**                  | Medio         | Dividir tareas en sprints manejables.            |
| **Rendimiento del Modelo**                | Medio         | Implementar técnicas de optimización y caching.  |
| **Usabilidad de la Interfaz**             | Bajo          | Iterar sobre feedback temprano de usuarios.      |

---