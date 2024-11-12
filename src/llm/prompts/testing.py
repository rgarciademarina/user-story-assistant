from langchain.prompts import PromptTemplate

testing_strategy_prompt = PromptTemplate(
    template="""
    Eres un experto en desarrollo de software que diseña estrategias de testing para asegurar la calidad del producto.

    Historia de Usuario Refinada:
    {refined_user_story}

    Casos Esquina Identificados:
    {corner_cases}

    Basándote en la historia de usuario refinada y los casos esquina identificados, por favor, propone una estrategia de testing detallada que incluya:
    - Tipos de tests necesarios
    - Herramientas recomendadas
    - Pasos a seguir para asegurar una implementación exitosa

    Responde únicamente con la siguiente sección claramente delimitada:

    **Estrategia de Testing:**
    Aquí va la estrategia de testing sugerida.

    **Fin de Estrategia**

    **Ejemplo de Respuesta:**
    **Estrategia de Testing:**
    - **Tipos de Tests Necesarios:**
      - **Unit Tests:** Para validar funciones individuales dentro del módulo de autenticación.
      - **Integration Tests:** Para asegurar que el módulo de autenticación interactúa correctamente con la base de datos y el servidor de correo.
      - **End-to-End Tests:** Para simular el flujo completo de inicio de sesión desde la interfaz de usuario hasta la autenticación final.
    - **Herramientas Recomendadas:**
      - **PyTest:** Para Unit Tests debido a su sencillez y extensibilidad.
      - **Selenium:** Para End-to-End Tests para automatizar la interacción con el navegador.
      - **Postman:** Para Integration Tests para verificar las API endpoints.
    - **Pasos a Seguir:**
      1. **Configuración del Entorno de Testing:**
         - Instalar todas las dependencias necesarias.
         - Configurar variables de entorno para pruebas.
      2. **Implementación de Unit Tests:**
         - Escribir tests para cada función individual en el módulo de autenticación.
      3. **Desarrollo de Integration Tests:**
         - Escribir tests que verifiquen la interacción entre el módulo de autenticación y otros componentes como la base de datos y el servidor de correo.
      4. **Creación de End-to-End Tests:**
         - Utilizar Selenium para automatizar pruebas que simulen el inicio de sesión desde la interfaz de usuario.
      5. **Integración con CI/CD:**
         - Configurar los pipelines de CI/CD para ejecutar todas las pruebas automáticamente en cada push.
    
    **Fin de Estrategia**
    """,
    input_variables=["refined_user_story", "corner_cases"]
)
