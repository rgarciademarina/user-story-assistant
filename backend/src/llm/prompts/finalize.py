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
[EXACTAMENTE 8 tests usando este formato para cada uno:]

#### Test XXX - [Nombre Específico con Valores]
**Dado** [precondición con valores específicos]  
**Cuando** [acción con valores específicos]  
**Entonces** [resultado con mensaje exacto]  

#### Conclusiones
[Análisis breve y conciso]

REGLAS OBLIGATORIAS:
1. DEBES usar el formato Gherkin (**Dado**, **Cuando**, **Entonces**) para TODOS los criterios y tests
2. DEBES incluir MÁXIMO 5 criterios de aceptación
3. DEBES incluir MÁXIMO 8 tests funcionales
4. DEBES incluir valores específicos en los tests (usuarios, contraseñas, mensajes exactos)
5. NO uses formatos descriptivos o narrativos
6. NO uses viñetas o numeración para criterios o tests
7. NO omitas ninguna sección

Historia Original:
{story_input}

Casos Esquina:
{corner_cases}

Estrategia de Testing:
{testing_strategy}

Feedback:
{feedback}
"""
