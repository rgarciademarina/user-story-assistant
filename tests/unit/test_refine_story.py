import pytest
from uuid import uuid4

@pytest.mark.asyncio
async def test_refine_story_without_feedback(mock_llm_service):
    """Test para refinar una historia de usuario sin feedback"""
    session_id = mock_llm_service.create_session()
    user_story = "Como usuario quiero poder iniciar sesión"

    result = await mock_llm_service.refine_story(
        session_id=session_id,
        user_story=user_story
    )

    assert isinstance(result, dict)
    assert 'refined_story' in result
    assert 'refinement_feedback' in result
    
    refined_story = result['refined_story']
    assert isinstance(refined_story, str)
    assert len(refined_story.strip()) > 0
    
    feedback = result['refinement_feedback']
    assert isinstance(feedback, str)
    assert len(feedback.strip()) > 0

@pytest.mark.asyncio
async def test_refine_story_with_feedback(mock_llm_service):
    """Test para refinar una historia de usuario con feedback"""
    session_id = mock_llm_service.create_session()
    user_story = "Como usuario quiero poder iniciar sesión"
    feedback = "Especificar el propósito del inicio de sesión"

    result = await mock_llm_service.refine_story(
        session_id=session_id,
        user_story=user_story,
        feedback=feedback
    )

    assert isinstance(result, dict)
    assert 'refined_story' in result
    assert 'refinement_feedback' in result
    
    refined_story = result['refined_story']
    assert isinstance(refined_story, str)
    assert len(refined_story.strip()) > 0
    
    # Verificar que el feedback se incorporó
    refinement_feedback = result['refinement_feedback']
    assert isinstance(refinement_feedback, str)
    assert len(refinement_feedback.strip()) > 0

@pytest.mark.asyncio
async def test_refine_story_with_existing_story(mock_llm_service):
    """Test para refinar una historia de usuario con una versión previa y feedback"""
    session_id = mock_llm_service.create_session()
    user_story = "Como usuario quiero poder iniciar sesión"
    feedback = "Agregar detalles sobre el método de autenticación"

    # Primera refinación
    result1 = await mock_llm_service.refine_story(
        session_id=session_id,
        user_story=user_story,
        feedback=feedback
    )

    # Segunda refinación con feedback adicional
    feedback2 = "Especificar también el nivel de seguridad requerido"
    result2 = await mock_llm_service.refine_story(
        session_id=session_id,
        user_story=result1['refined_story'],
        feedback=feedback2
    )

    assert isinstance(result2, dict)
    assert 'refined_story' in result2
    assert 'refinement_feedback' in result2
    
    refined_story = result2['refined_story']
    assert isinstance(refined_story, str)
    assert len(refined_story.strip()) > 0
    
    refinement_feedback = result2['refinement_feedback']
    assert isinstance(refinement_feedback, str)
    assert len(refinement_feedback.strip()) > 0