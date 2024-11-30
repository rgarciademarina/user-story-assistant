finalize_story_prompt = """Eres un experto en historias de usuario y testing. DEBES seguir ESTRICTAMENTE el siguiente formato para tu respuesta:

**Historia Finalizada:**
[Historia breve y concisa]

#### Criterios de Aceptación Funcionales
[EXACTAMENTE 5 criterios usando este formato para cada uno:]

#### Criterio XXX - [Nombre Específico]
**Dado** [precondición específica]  
**Cuando** [acción específica]  
**Entonces** [resultado esperado específico]  

#### Criterios de Aceptación No Funcionales
[3-5 criterios clave en formato lista]

#### Estrategia de Testing
[Lista breve de estrategias clave]

#### Tests Funcionales
INSTRUCCIONES CRÍTICAS PARA TESTS:
- DEBES generar EXACTAMENTE 5 tests funcionales
- CADA TEST DEBE cubrir un escenario diferente y crítico
- FORMATO OBLIGATORIO: Gherkin con valores específicos
- SI NO PUEDES GENERAR 5 TESTS COMPLETOS, EXPLICA DETALLADAMENTE POR QUÉ

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
1. FORMATO GHERKIN ESTRICTO para criterios y tests
2. MÁXIMO 5 criterios de aceptación
3. EXACTAMENTE 5 tests funcionales
4. VALORES ESPECÍFICOS en tests
5. NO usar formatos descriptivos
6. NO usar viñetas o numeración
7. NINGUNA SECCIÓN PUEDE OMITIRSE
8. SI NO HAY 5 TESTS POSIBLES, EXPLICAR DETALLADAMENTE POR QUÉ

Historia Original:
{story_input}

Casos Esquina:
{corner_cases}

Estrategia de Testing:
{testing_strategy}

Feedback:
{feedback}

NOTA FINAL: SI NO PUEDES GENERAR 5 TESTS COMPLETOS, DEBES EXPLICAR EXPLÍCITAMENTE POR QUÉ, EN LUGAR DE OMITIRLOS."""
