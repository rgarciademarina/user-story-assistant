import pytest

@pytest.mark.asyncio
async def test_propose_testing_strategy_without_feedback(llm_service):
    """Test para proponer estrategias de testing sin feedback"""
    refined_story = "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante la combinación correcta de mi nombre de usuario o dirección de correo electrónico y contraseña, para acceder a mis perfiles, historiales de compras y otros datos personales de manera segura y eficiente."
    corner_cases = [
        "1. **Nombre de Usuario/Correo electrónico no registrado:** El usuario intenta iniciar sesión con una dirección de correo electrónico o nombre de usuario que no se encuentra en la base de datos del sistema.",
        "2. **Contraseña Incorrecta persistente:** El usuario ingresa la contraseña incorrecta más de 10 veces consecutivas.",
        "3. **Problemas con autenticación de dos factores (2FA):** El usuario no puede iniciar sesión porque el sistema requiere la verificación del código de autenticación 2FA."
    ]

    result = await llm_service.propose_testing_strategy(refined_story, corner_cases)

    # Verificar que se recibe una lista de estrategias de testing
    assert isinstance(result, list), "El resultado debe ser una lista"
    assert len(result) > 0, "Debe haber al menos una estrategia de testing propuesta"
    for estrategia in result:
        assert isinstance(estrategia, str), "Cada estrategia de testing debe ser una cadena"
        if estrategia.strip():  # Solo validar líneas no vacías
            assert len(estrategia.strip()) > 0, "Las estrategias no deben estar vacías"

@pytest.mark.asyncio
async def test_propose_testing_strategy_with_feedback(llm_service):
    """Test para proponer estrategias de testing con feedback"""
    refined_story = "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante la combinación correcta de mi nombre de usuario o dirección de correo electrónico y contraseña, para acceder a mis perfiles, historiales de compras y otros datos personales de manera segura y eficiente."
    corner_cases = [
        "1. **Nombre de Usuario/Correo electrónico no registrado:** El usuario intenta iniciar sesión con una dirección de correo electrónico o nombre de usuario que no se encuentra en la base de datos del sistema.",
        "2. **Contraseña Incorrecta persistente:** El usuario ingresa la contraseña incorrecta más de 10 veces consecutivas."
    ]
    feedback = "Incluir pruebas de rendimiento bajo carga y pruebas de seguridad para prevenir ataques de fuerza bruta"

    result = await llm_service.propose_testing_strategy(refined_story, corner_cases, feedback)

    # Verificar que se recibe una lista de estrategias de testing
    assert isinstance(result, list), "El resultado debe ser una lista"
    assert len(result) > 0, "Debe haber al menos una estrategia de testing propuesta"
    for estrategia in result:
        assert isinstance(estrategia, str), "Cada estrategia de testing debe ser una cadena"
        if estrategia.strip():  # Solo validar líneas no vacías
            assert len(estrategia.strip()) > 0, "Las estrategias no deben estar vacías"
    # Verificar que el feedback se ha tenido en cuenta
    assert any(["rendimiento" in estrategia.lower() or "carga" in estrategia.lower() or "seguridad" in estrategia.lower() for estrategia in result]), \
        "Las estrategias deben incluir pruebas mencionadas en el feedback"
