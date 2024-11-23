import pytest
from uuid import UUID

@pytest.mark.asyncio
async def test_propose_testing_strategy_without_feedback(llm_service):
    """Test para proponer estrategias de testing sin feedback"""
    session_id = llm_service.create_session()
    refined_story = "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal"
    corner_cases = [
        "1. **Intentos de Inicio de Sesión Fallidos:** El usuario ingresa una contraseña incorrecta repetidamente.",
        "2. **Acceso desde Ubicaciones No Reconocidas:** Intentos de inicio de sesión desde ubicaciones geográficas inusuales."
    ]

    result = await llm_service.propose_testing_strategy(
        session_id=session_id,
        refined_story=refined_story,
        corner_cases=corner_cases
    )

    assert isinstance(result, dict)
    assert 'testing_strategies' in result
    assert 'testing_feedback' in result
    
    strategies = result['testing_strategies']
    assert isinstance(strategies, list)
    assert len(strategies) > 0
    
    feedback = result['testing_feedback']
    assert isinstance(feedback, str)
    assert len(feedback.strip()) > 0

@pytest.mark.asyncio
async def test_propose_testing_strategy_with_feedback(llm_service):
    """Test para proponer estrategias de testing con feedback"""
    session_id = llm_service.create_session()
    refined_story = "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal"
    corner_cases = [
        "1. **Intentos de Inicio de Sesión Fallidos:** El usuario ingresa una contraseña incorrecta repetidamente.",
        "2. **Acceso desde Ubicaciones No Reconocidas:** Intentos de inicio de sesión desde ubicaciones geográficas inusuales."
    ]
    feedback = "Agregar pruebas de rendimiento y seguridad"

    result = await llm_service.propose_testing_strategy(
        session_id=session_id,
        refined_story=refined_story,
        corner_cases=corner_cases,
        feedback=feedback
    )

    assert isinstance(result, dict)
    assert 'testing_strategies' in result
    assert 'testing_feedback' in result
    
    strategies = result['testing_strategies']
    assert isinstance(strategies, list)
    assert len(strategies) > 0
    
    # Verificar que el feedback se incorporó
    testing_feedback = result['testing_feedback']
    assert isinstance(testing_feedback, str)
    assert len(testing_feedback.strip()) > 0

@pytest.mark.asyncio
async def test_propose_testing_strategy_with_existing_strategies(llm_service):
    """Test para proponer estrategias de testing con estrategias existentes y feedback"""
    session_id = llm_service.create_session()
    refined_story = "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal"
    corner_cases = [
        "1. **Intentos de Inicio de Sesión Fallidos:** El usuario ingresa una contraseña incorrecta repetidamente.",
        "2. **Acceso desde Ubicaciones No Reconocidas:** Intentos de inicio de sesión desde ubicaciones geográficas inusuales."
    ]
    existing_testing_strategies = [
        "1. **Pruebas de Validación de Credenciales:** Verificar el comportamiento del sistema con diferentes combinaciones de usuario/contraseña.",
        "2. **Pruebas de Seguridad Básicas:** Validar el manejo de sesiones y tokens de autenticación."
    ]
    feedback = "Agregar pruebas de rendimiento bajo carga"

    result = await llm_service.propose_testing_strategy(
        session_id=session_id,
        refined_story=refined_story,
        corner_cases=corner_cases,
        feedback=feedback,
        existing_testing_strategies=existing_testing_strategies
    )

    assert isinstance(result, dict)
    assert 'testing_strategies' in result
    assert 'testing_feedback' in result
    
    strategies = result['testing_strategies']
    assert isinstance(strategies, list)
    assert len(strategies) > 0

    # Verificar que los conceptos clave de las estrategias existentes están cubiertos
    strategies_text = ' '.join(strategies).lower()
    
    # Lista de conceptos con sus alternativas
    key_concepts = {
        'credenciales': ['credencial', 'contraseña', 'usuario'],
        'autenticación': ['autenticar', 'acceso', 'iniciar sesión'],
        'seguridad': ['seguro', 'protección', 'vulnerabilidad'],
        'sesiones': ['sesión', 'token', 'acceso simultáneo']
    }
    
    for concept, alternatives in key_concepts.items():
        assert any(alt in strategies_text for alt in alternatives), \
            f"Concepto '{concept}' o sus alternativas {alternatives} no encontrados en las estrategias"

    # Verificar que se agregaron pruebas de rendimiento según el feedback
    assert any('rendimiento' in s.lower() or 'carga' in s.lower() for s in strategies)

    feedback = result['testing_feedback']
    assert isinstance(feedback, str)
    assert len(feedback.strip()) > 0