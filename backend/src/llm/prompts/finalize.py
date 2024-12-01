finalize_story_prompt = """Eres un experto en historias de usuario y testing. DEBES seguir ESTRICTAMENTE el siguiente formato para tu respuesta:

**Historia Finalizada:**
[Historia breve y concisa]

#### Criterios de Aceptación Funcionales
[criterios usando este formato para cada uno:]

#### Criterio XXX - [Nombre Específico]
**Dado** [precondición específica]  
**Cuando** [acción específica]  
**Entonces** [resultado esperado específico]  

#### Criterios de Aceptación No Funcionales
[criterios clave en formato lista]

#### Estrategia de Testing
[Lista breve de estrategias clave]

#### Test 1 - [Escenario Crítico 1]
**Dado** [precondición con valores específicos]  
**Cuando** [acción con valores específicos]  
**Entonces** [resultado con mensaje exacto]  

#### Test 2 - [Escenario Crítico 2]
**Dado** [precondición con valores específicos]  
**Cuando** [acción con valores específicos]  
**Entonces** [resultado con mensaje exacto]  

#### Test 3 - [Escenario Crítico 3]
**Dado** [precondición con valores específicos]  
**Cuando** [acción con valores específicos]  
**Entonces** [resultado con mensaje exacto]  

#### Test 4 - [Escenario Crítico 4]
**Dado** [precondición con valores específicos]  
**Cuando** [acción con valores específicos]  
**Entonces** [resultado con mensaje exacto]  

#### Test 5 - [Escenario Crítico 5]
**Dado** [precondición con valores específicos]  
**Cuando** [acción con valores específicos]  
**Entonces** [resultado con mensaje exacto]  

#### Conclusiones
[Análisis breve y conciso]

REGLAS ABSOLUTAMENTE OBLIGATORIAS:
1. FORMATO GHERKIN ESTRICTO para los criterios
2. Intenta minimizar el número de criterios de aceptación y tests funcionales, pero no hay un límite máximo estricto.
3. VALORES ESPECÍFICOS en tests
4. NO usar formatos descriptivos
5. NO usar viñetas o numeración
6. NINGUNA SECCIÓN PUEDE OMITIRSE

Historia Original:
{story_input}

Casos Esquina:
{corner_cases}

Estrategia de Testing:
{testing_strategy}

Feedback:
{feedback}
"""
