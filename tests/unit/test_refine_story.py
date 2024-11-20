import pytest

@pytest.mark.asyncio
async def test_refine_story_without_feedback(llm_service):
    """Test para refinar una historia de usuario sin feedback"""
    session_id = llm_service.create_session()
    user_story = """
    Como usuario quiero poder iniciar sesión 
    para acceder a mi cuenta personal
    """

    result = await llm_service.refine_story(
        session_id=session_id,
        user_story=user_story
    )

    # Verificar que se recibió un diccionario con las claves esperadas
    assert isinstance(result, dict), "El resultado debe ser un diccionario"
    assert 'refined_story' in result, "El resultado debe contener 'refined_story'"
    assert 'refinement_feedback' in result, "El resultado debe contener 'refinement_feedback'"
    
    # Verificar que la historia refinada es una cadena no vacía
    refined_story = result['refined_story']
    assert isinstance(refined_story, str), "La historia refinada debe ser una cadena"
    assert len(refined_story.strip()) > 0, "La historia refinada no debe estar vacía"
    assert "Como usuario" in refined_story, "La historia refinada debe mantener el formato de historia de usuario"
    
    # Verificar que el feedback es una cadena no vacía
    refinement_feedback = result['refinement_feedback']
    assert isinstance(refinement_feedback, str), "El feedback de refinamiento debe ser una cadena"
    assert len(refinement_feedback.strip()) > 0, "El feedback de refinamiento no debe estar vacío"

@pytest.mark.asyncio
async def test_refine_story_with_feedback(llm_service):
    """Test para refinar una historia de usuario con feedback"""
    session_id = llm_service.create_session()
    user_story = """
    Como usuario quiero poder iniciar sesión 
    para acceder a mi cuenta personal
    """
    feedback = "La historia debería especificar el método de autenticación y los datos a los que se accederá"
    
    result = await llm_service.refine_story(
        session_id=session_id,
        user_story=user_story,
        feedback=feedback
    )

    # Verificar que se recibió un diccionario con las claves esperadas
    assert isinstance(result, dict), "El resultado debe ser un diccionario"
    assert 'refined_story' in result, "El resultado debe contener 'refined_story'"
    assert 'refinement_feedback' in result, "El resultado debe contener 'refinement_feedback'"

    # Verificar que la historia refinada es una cadena no vacía
    refined_story = result['refined_story']
    assert isinstance(refined_story, str), "La historia refinada debe ser una cadena"
    assert len(refined_story.strip()) > 0, "La historia refinada no debe estar vacía"
    assert "Como usuario" in refined_story, "La historia refinada debe mantener el formato de historia de usuario"
    assert any(["correo" in line.lower() or "email" in line.lower() or "contraseña" in line.lower() 
               for line in refined_story.split('\n') if line.strip()]), \
        "La historia refinada debe incorporar el feedback sobre el método de autenticación"

    # Verificar que el feedback de refinamiento es una cadena no vacía
    refinement_feedback = result['refinement_feedback']
    assert isinstance(refinement_feedback, str), "El feedback de refinamiento debe ser una cadena"
    assert len(refinement_feedback.strip()) > 0, "El feedback de refinamiento no debe estar vacío"
    assert any(["método de autenticación" in refinement_feedback.lower() or
                "datos" in refinement_feedback.lower()] ), \
        "El feedback de refinamiento debe mencionar los cambios realizados según el feedback proporcionado"