import pytest
from uuid import UUID

@pytest.mark.asyncio
async def test_identify_corner_cases_without_feedback(mock_llm_service):
    """Test para identificar casos esquina sin feedback"""
    session_id = mock_llm_service.create_session()
    refined_story = "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal"

    result = await mock_llm_service.identify_corner_cases(
        session_id=session_id,
        refined_story=refined_story
    )

    assert isinstance(result, dict)
    assert 'corner_cases' in result
    assert 'corner_cases_feedback' in result
    
    corner_cases = result['corner_cases']
    assert isinstance(corner_cases, list)
    assert len(corner_cases) > 0
    
    feedback = result['corner_cases_feedback']
    assert isinstance(feedback, str)
    assert len(feedback.strip()) > 0

@pytest.mark.asyncio
async def test_identify_corner_cases_with_feedback(mock_llm_service):
    """Test para identificar casos esquina con feedback"""
    session_id = mock_llm_service.create_session()
    refined_story = "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal"
    feedback = "Considerar casos de seguridad y validación"

    result = await mock_llm_service.identify_corner_cases(
        session_id=session_id,
        refined_story=refined_story,
        feedback=feedback
    )

    assert isinstance(result, dict)
    assert 'corner_cases' in result
    assert 'corner_cases_feedback' in result
    
    corner_cases = result['corner_cases']
    assert isinstance(corner_cases, list)
    assert len(corner_cases) > 0
    
    # Verificar que el feedback se incorporó
    corner_cases_feedback = result['corner_cases_feedback']
    assert isinstance(corner_cases_feedback, str)
    assert len(corner_cases_feedback.strip()) > 0

@pytest.mark.asyncio
async def test_identify_corner_cases_with_existing_cases(mock_llm_service):       
    """Test para identificar casos esquina utilizando casos previos y feedback"""
    session_id = mock_llm_service.create_session()
    refined_story = "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal"
    existing_corner_cases = [
        "1. **Intentos de Inicio de Sesión Fallidos:** El usuario ingresa una contraseña incorrecta repetidamente.",
        "2. **Acceso desde Ubicaciones No Reconocidas:** Intentos de inicio de sesión desde ubicaciones geográficas inusuales."
    ]
    feedback = "Considerar casos de bloqueo de cuenta"

    result = await mock_llm_service.identify_corner_cases(
        session_id=session_id,
        refined_story=refined_story,
        feedback=feedback,
        existing_corner_cases=existing_corner_cases
    )

    assert isinstance(result, dict)
    assert 'corner_cases' in result
    assert 'corner_cases_feedback' in result

    corner_cases = result['corner_cases']
    assert isinstance(corner_cases, list)
    assert len(corner_cases) > 0

    # Verificar que los conceptos clave de los casos existentes están cubiertos
    corner_cases_text = ' '.join(corner_cases).lower()
    
    key_concepts = {
        'intentos fallidos': ['contraseña incorrecta', 'intento fallido', 'fuerza bruta'],
        'ubicaciones': ['ubicación', 'geográfica', 'localización'],
    }
    
    for concept, alternatives in key_concepts.items():
        assert any(alt in corner_cases_text for alt in alternatives), \
            f"Concepto '{concept}' o sus alternativas {alternatives} no encontrados en los casos esquina"

    # Verificar que se agregaron casos relacionados con el bloqueo según el feedback
    assert any('bloqueo' in case.lower() or 'inactividad' in case.lower() for case in corner_cases)

    feedback = result['corner_cases_feedback']
    assert isinstance(feedback, str)
    assert len(feedback.strip()) > 0
