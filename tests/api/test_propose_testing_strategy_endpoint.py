import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.mark.asyncio
async def test_propose_testing_strategy_endpoint(llm_service):
    """Test para el endpoint de propuesta de estrategias de testing con feedback"""
    refined_story = "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante la combinación correcta de mi nombre de usuario o dirección de correo electrónico y contraseña, para acceder a mis perfiles, historiales de compras y otros datos personales de manera segura y eficiente."
    corner_cases = [
        "1. **Nombre de Usuario/Correo electrónico no registrado:** El usuario intenta iniciar sesión con una dirección de correo electrónico o nombre de usuario que no se encuentra en la base de datos del sistema.",
        "2. **Contraseña Incorrecta persistente:** El usuario ingresa la contraseña incorrecta más de 10 veces consecutivas, lo que bloquea temporalmente su acceso al sistema.",
        "3. **Problemas con autenticación de dos factores (2FA):** El usuario no puede iniciar sesión porque el sistema requiere la verificación del código de autenticación 2FA, pero el dispositivo del usuario no es compatible o no tiene el código disponible.",
        "4. **Bloqueo de cuenta por seguridad:** La cuenta del usuario está bloqueada temporalmente debido a inactividad prolongada o actividad sospechosa, lo que impide su acceso hasta que se complete el proceso de desbloqueo.",
        "5. **Compatibilidad con navegadores antiguos:** El sistema no es compatible con ciertos navegadores antiguos o versiones obsoletas, lo que limita la funcionalidad del inicio de sesión para algunos usuarios."
    ]
    
    payload = {
        'story': refined_story,
        'corner_cases': corner_cases,
        'feedback': 'Incluir pruebas de rendimiento bajo carga y pruebas de seguridad para prevenir ataques de fuerza bruta'
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test/api") as client:
        response = await client.post("/propose_testing_strategy", json=payload)
        assert response.status_code == 200, f"Se esperaba el código de estado 200, pero se obtuvo {response.status_code}"
        
        response_json = response.json()
        assert "testing_strategies" in response_json, "Falta la clave 'testing_strategies' en la respuesta"
        
        testing_strategies = response_json["testing_strategies"]
        assert isinstance(testing_strategies, list), "El valor de 'testing_strategies' debe ser una lista"
        assert len(testing_strategies) > 0, "La lista de 'testing_strategies' no debe estar vacía"
        
        for estrategia in testing_strategies:
            assert isinstance(estrategia, str), "Cada estrategia de testing debe ser una cadena"
            if estrategia.strip():  # Solo validar líneas no vacías
                assert len(estrategia.strip()) > 0, "Las estrategias no deben estar vacías"
        
        # Verificar que el feedback se ha tenido en cuenta
        assert any(["rendimiento" in estrategia.lower() or 
                   "carga" in estrategia.lower() or 
                   "seguridad" in estrategia.lower() for estrategia in testing_strategies if estrategia.strip()]), \
            "Las estrategias deben incluir pruebas mencionadas en el feedback"