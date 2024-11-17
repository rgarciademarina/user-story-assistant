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

    # Verificar que se recibió una cadena refinada
    assert isinstance(result, str), "El resultado debe ser una cadena"
    assert len(result.strip()) > 0, "El resultado no debe estar vacío"
    assert "Como usuario" in result, "La historia refinada debe mantener el formato de historia de usuario"
    # Verificar que el feedback se ha tenido en cuenta (solo en líneas no vacías)
    assert any(["correo" in line.lower() or "email" in line.lower() or "contraseña" in line.lower() 
               for line in result.split('\n') if line.strip()]), \
        "La historia refinada debe incorporar el feedback sobre el método de autenticación"

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

    # Verificar que se recibió una cadena refinada
    assert isinstance(result, str), "El resultado debe ser una cadena"
    assert len(result.strip()) > 0, "El resultado no debe estar vacío"
    assert "Como usuario" in result, "La historia refinada debe mantener el formato de historia de usuario"
    assert any(["correo" in line.lower() or "email" in line.lower() or "contraseña" in line.lower() 
               for line in result.split('\n') if line.strip()]), \
        "La historia refinada debe incorporar el feedback sobre el método de autenticación"