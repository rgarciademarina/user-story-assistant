import pytest

@pytest.mark.asyncio
async def test_identify_corner_cases_without_feedback(llm_service):
    """Test para identificar casos esquina sin feedback"""
    session_id = llm_service.create_session()
    refined_story = "Como usuario quiero..."

    result = await llm_service.identify_corner_cases(
        session_id=session_id,
        refined_story=refined_story
    )

    # Verificar que se recibió un diccionario con las claves esperadas
    assert isinstance(result, dict), "El resultado debe ser un diccionario"
    assert 'corner_cases' in result, "El resultado debe contener 'corner_cases'"
    assert 'corner_cases_feedback' in result, "El resultado debe contener 'corner_cases_feedback'"

    # Verificar que los casos esquina son una lista no vacía
    corner_cases = result['corner_cases']
    assert isinstance(corner_cases, list), "Los casos esquina deben ser una lista"
    assert len(corner_cases) > 0, "Debe haber al menos un caso esquina identificado"

    # Verificar que el feedback es una cadena no vacía
    corner_cases_feedback = result['corner_cases_feedback']
    assert isinstance(corner_cases_feedback, str), "El feedback debe ser una cadena"
    assert len(corner_cases_feedback.strip()) > 0, "El feedback no debe estar vacío"

@pytest.mark.asyncio
async def test_identify_corner_cases_with_feedback(llm_service):
    """Test para identificar casos esquina con feedback"""
    session_id = llm_service.create_session()
    refined_story = "Como usuario quiero..."
    feedback = "Considerar casos de autenticación de dos factores y bloqueos por inactividad"

    result = await llm_service.identify_corner_cases(
        session_id=session_id,
        refined_story=refined_story,
        feedback=feedback
    )

    # Verificar que se recibió un diccionario con las claves esperadas
    assert isinstance(result, dict), "El resultado debe ser un diccionario"
    assert 'corner_cases' in result, "El resultado debe contener 'corner_cases'"
    assert 'corner_cases_feedback' in result, "El resultado debe contener 'corner_cases_feedback'"

    # Verificar que los casos esquina son una lista no vacía
    corner_cases = result['corner_cases']
    assert isinstance(corner_cases, list), "Los casos esquina deben ser una lista"
    assert len(corner_cases) > 0, "Debe haber al menos un caso esquina identificado"

    # Verificar que el feedback es una cadena no vacía y contiene referencias al feedback proporcionado
    corner_cases_feedback = result['corner_cases_feedback']
    assert isinstance(corner_cases_feedback, str), "El feedback debe ser una cadena"
    assert len(corner_cases_feedback.strip()) > 0, "El feedback no debe estar vacío"

@pytest.mark.asyncio
async def test_identify_corner_cases_with_existing_cases(llm_service):
    """Test para identificar casos esquina utilizando casos previos y feedback"""
    session_id = llm_service.create_session()
    refined_story = "Como usuario quiero..."
    existing_corner_cases = [
        "1. Intentos de inicio de sesión fallidos.",
        "2. Acceso desde ubicaciones no reconocidas."
    ]
    feedback = "Considerar casos de autenticación de dos factores y bloqueos por inactividad"

    result = await llm_service.identify_corner_cases(
        session_id=session_id,
        refined_story=refined_story,
        feedback=feedback,
        existing_corner_cases=existing_corner_cases
    )

    # Verificar que se recibió un diccionario con las claves esperadas
    assert isinstance(result, dict), "El resultado debe ser un diccionario"
    assert 'corner_cases' in result, "El resultado debe contener 'corner_cases'"
    assert 'corner_cases_feedback' in result, "El resultado debe contener 'corner_cases_feedback'"

    # Verificar que los casos esquina son una lista no vacía
    corner_cases = result['corner_cases']
    assert isinstance(corner_cases, list), "Los casos esquina deben ser una lista"
    assert len(corner_cases) > 0, "Debe haber al menos un caso esquina identificado"

    # Verificar que el feedback es una cadena no vacía y contiene referencias al feedback proporcionado
    corner_cases_feedback = result['corner_cases_feedback']
    assert isinstance(corner_cases_feedback, str), "El feedback debe ser una cadena"
    assert len(corner_cases_feedback.strip()) > 0, "El feedback no debe estar vacío"
    assert any(keyword in corner_cases_feedback.lower() for keyword in ["autenticación de dos factores", "inactividad"]), \
        "El feedback debe mencionar los cambios relacionados con el feedback proporcionado"

    # Verificar que los casos esquina incluyen las nuevas consideraciones
    assert any("autenticación de dos factores" in case.lower() for case in corner_cases), \
        "Los casos esquina deben incluir consideraciones sobre autenticación de dos factores"
