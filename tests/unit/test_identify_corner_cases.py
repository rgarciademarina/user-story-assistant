import pytest

@pytest.mark.asyncio
async def test_identify_corner_cases_without_feedback(llm_service):
    """Test para identificar casos esquina sin feedback"""
    refined_story = "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante la combinación correcta de mi nombre de usuario o dirección de correo electrónico y contraseña, para acceder a mis perfiles, historiales de compras y otros datos personales de manera segura y eficiente."

    result = await llm_service.identify_corner_cases(refined_story)

    # Verificar que se recibe una lista de casos esquina
    assert isinstance(result, list), "El resultado debe ser una lista"
    assert len(result) > 0, "Debe haber al menos un caso esquina identificado"
    for caso in result:
        assert isinstance(caso, str), "Cada caso esquina debe ser una cadena"
        if caso.strip():  # Solo validar líneas no vacías
            assert len(caso.strip()) > 0, "Los casos esquina no deben estar vacíos"

@pytest.mark.asyncio
async def test_identify_corner_cases_with_feedback(llm_service):
    """Test para identificar casos esquina con feedback"""
    refined_story = "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante la combinación correcta de mi nombre de usuario o dirección de correo electrónico y contraseña, para acceder a mis perfiles, historiales de compras y otros datos personales de manera segura y eficiente."
    feedback = "Considerar también casos de autenticación de dos factores y bloqueos de cuenta por inactividad"

    result = await llm_service.identify_corner_cases(refined_story, feedback)

    # Verificar que se recibe una lista de casos esquina
    assert isinstance(result, list), "El resultado debe ser una lista"
    assert len(result) > 0, "Debe haber al menos un caso esquina identificado"
    for caso in result:
        assert isinstance(caso, str), "Cada caso esquina debe ser una cadena"
        if caso.strip():  # Solo validar líneas no vacías
            assert len(caso.strip()) > 0, "Los casos esquina no deben estar vacíos"
    # Verificar que el feedback se ha tenido en cuenta
    assert any(["2fa" in caso.lower() or "dos factores" in caso.lower() or "inactividad" in caso.lower() for caso in result if caso.strip()]), \
        "Los casos esquina deben incluir escenarios mencionados en el feedback"
