import pytest
from uuid import UUID, uuid4
from unittest.mock import Mock, patch, AsyncMock
from src.llm.service import LLMService, ChatMessageHistory
from src.config.llm_config import LLMConfig
from src.llm.models import Session, ProcessState
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import OllamaLLM

@pytest.fixture
def mock_ollama_llm():
    mock = Mock(spec=OllamaLLM)
    # Configurar el mock para devolver solo las secciones relevantes para cada método
    async def mock_ainvoke(messages):
        prompt = str(messages)
        print(f"\nPrompt recibido:\n{prompt}\n")  # Debug log
        
        if "Historia de Usuario Original:" in prompt:
            response = """**Historia Refinada:**
Historia refinada de prueba
**Cambios Realizados:**
Cambios de prueba"""
        elif "Historia de Usuario Refinada:" in prompt and "Casos Esquina Identificados:" in prompt:
            response = """**Estrategias de Testing Actualizadas:**
- Estrategia 1
- Estrategia 2
**Análisis de Cambios:**
Justificación de prueba"""
        elif "Historia de Usuario Refinada:" in prompt:
            response = """**Casos Esquina Actualizados:**
- Caso 1
- Caso 2
**Análisis de Cambios:**
Análisis de prueba"""
        else:  # testing_strategy
            response = """**Estrategias de Testing Actualizadas:**
- Estrategia 1
- Estrategia 2
**Análisis de Cambios:**
Justificación de prueba"""
        
        print(f"\nRespuesta generada:\n{response}\n")  # Debug log
        return response
    
    mock.ainvoke = AsyncMock(side_effect=mock_ainvoke)
    # Configurar atributos necesarios
    mock.model = "test-model"
    mock.base_url = "http://test-url"
    mock.temperature = 0.7
    return mock

@pytest.fixture
def llm_config(mock_ollama_llm):
    return LLMConfig(
        llm=mock_ollama_llm,
        refinement_prompt_template="Refina la historia: {story}",
        corner_case_prompt_template="Identifica casos esquina: {story}",
        testing_strategy_prompt_template="Propón estrategias: {story}"
    )

@pytest.fixture
def llm_service(llm_config):
    service = LLMService(config=llm_config, llm=llm_config.llm)
    # Asegurarnos de que el servicio use el mock
    service.llm = llm_config.llm
    return service

@pytest.mark.asyncio
async def test_create_session(llm_service):
    """Test la creación de una nueva sesión"""
    session_id = llm_service.create_session()
    assert isinstance(session_id, UUID)
    assert session_id in llm_service._sessions
    assert session_id in llm_service._memories
    assert isinstance(llm_service._memories[session_id], ChatMessageHistory)

@pytest.mark.asyncio
async def test_get_session_with_invalid_id(llm_service):
    """Test el manejo de un ID de sesión inválido"""
    with pytest.raises(ValueError, match="ID de sesión inválido"):
        llm_service._get_session("invalid-id")

@pytest.mark.asyncio
async def test_extract_sections(llm_service):
    """Test la extracción de secciones de una respuesta"""
    response = """**Sección 1:**
Contenido 1
**Sección 2:**
Contenido 2"""
    
    sections = llm_service._extract_sections(response, ["**Sección 1:**", "**Sección 2:**"])
    assert sections == {
        "**Sección 1:**": "Contenido 1",
        "**Sección 2:**": "Contenido 2"
    }

@pytest.mark.asyncio
async def test_extract_sections_missing_marker(llm_service):
    """Test la extracción de secciones cuando falta un marcador"""
    response = """**Sección 1:**
Contenido 1"""
    
    sections = llm_service._extract_sections(response, ["**Sección 1:**", "**Sección 2:**"])
    assert sections == {
        "**Sección 1:**": "Contenido 1",
        "**Sección 2:**": ""
    }

@pytest.mark.asyncio
async def test_memory_integration(llm_service):
    """Test la integración de la memoria en las conversaciones"""
    session_id = llm_service.create_session()
    memory = llm_service._memories[session_id]
    
    # Simular una conversación
    memory.add_message(HumanMessage(content="¿Cómo estás?"))
    memory.add_message(AIMessage(content="¡Muy bien!"))
    
    messages = memory.messages
    assert len(messages) == 2
    assert isinstance(messages[0], HumanMessage)
    assert isinstance(messages[1], AIMessage)
    assert messages[0].content == "¿Cómo estás?"
    assert messages[1].content == "¡Muy bien!"

@pytest.mark.asyncio
async def test_process_step_error_handling(llm_service):
    """Test el manejo de errores en el procesamiento de pasos"""
    session_id = llm_service.create_session()
    mock_llm = Mock(spec=OllamaLLM)
    mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM Error"))
    llm_service.llm = mock_llm

    with pytest.raises(Exception) as exc_info:
        await llm_service._process_step(
            session_id=session_id,
            prompt_template="Test prompt",
            input_variables={},
            process_state=ProcessState.REFINEMENT,
            extract_markers=[],
            update_session_callback=lambda s, r: None,
            format_interaction=lambda r: ("human", "ai")
        )
    assert str(exc_info.value) == "LLM Error"

@pytest.mark.asyncio
async def test_session_state_management(llm_service):
    """Test el manejo del estado de la sesión"""
    session_id = llm_service.create_session()
    session = llm_service._get_session(session_id)
    
    # Verificar estado inicial
    assert session.state == ProcessState.REFINEMENT
    
    # Simular un proceso
    await llm_service._process_step(
        session_id=session_id,
        prompt_template="Test prompt",
        input_variables={},
        process_state=ProcessState.CORNER_CASES,
        extract_markers=[],
        update_session_callback=lambda s, r: setattr(s, 'state', ProcessState.CORNER_CASES),
        format_interaction=lambda r: ("human", "ai")
    )
    
    # Verificar cambio de estado
    assert session.state == ProcessState.CORNER_CASES

@pytest.mark.asyncio
async def test_extract_section_with_end_marker(llm_service):
    """Test la extracción de una sección con marcador de fin"""
    text = """**Inicio:**
Contenido
**Fin:**
Otro contenido"""
    
    section = llm_service._extract_section(text, "**Inicio:**", "**Fin:**")
    assert section.strip() == "Contenido"

@pytest.mark.asyncio
async def test_extract_section_without_end_marker(llm_service):
    """Test la extracción de una sección sin marcador de fin"""
    text = """**Inicio:**
Contenido
Más contenido"""
    
    section = llm_service._extract_section(text, "**Inicio:**")
    assert section.strip() == "Contenido\nMás contenido"

@pytest.mark.asyncio
async def test_process_step_with_post_processing(llm_service):
    """Test el procesamiento de pasos con post-procesamiento"""
    session_id = llm_service.create_session()
    
    def post_process(sections):
        return {"processed": sections.get("**Sección:**", "")}
    
    result = await llm_service._process_step(
        session_id=session_id,
        prompt_template="Test prompt",
        input_variables={},
        process_state=ProcessState.REFINEMENT,
        extract_markers=["**Sección:**"],
        update_session_callback=lambda s, r: None,
        format_interaction=lambda r: ("human", "ai"),
        post_process_response=post_process
    )
    
    assert "processed" in result

@pytest.mark.asyncio
async def test_add_to_memory(llm_service):
    """Test la adición de mensajes a la memoria"""
    session_id = llm_service.create_session()
    
    await llm_service._add_to_memory(
        session_id=session_id,
        human_message="Pregunta de prueba",
        ai_message="Respuesta de prueba"
    )
    
    memory = llm_service._memories[session_id]
    messages = memory.messages
    
    assert len(messages) == 2
    assert messages[0].content == "Pregunta de prueba"
    assert messages[1].content == "Respuesta de prueba"

@pytest.mark.asyncio
async def test_refine_story_complete_flow(llm_service):
    """Test el flujo completo de refinamiento de historia"""
    session_id = llm_service.create_session()
    
    # Asegurarnos de que la memoria está inicializada
    llm_service._memories[session_id] = ChatMessageHistory()
    
    result = await llm_service.refine_story(
        session_id=session_id,
        user_story="Historia original",
        feedback="Feedback de prueba"
    )
    
    assert "refined_story" in result
    assert "refinement_feedback" in result
    assert result["refined_story"] == "Historia refinada de prueba"
    assert result["refinement_feedback"] == "Cambios de prueba"
    
    session = llm_service._get_session(session_id)
    assert session.refined_story == result["refined_story"]
    assert len(session.interactions) > 0
    assert session.state == ProcessState.REFINEMENT

@pytest.mark.asyncio
async def test_identify_corner_cases_complete_flow(llm_service):
    """Test el flujo completo de identificación de casos esquina"""
    session_id = llm_service.create_session()
    
    # Asegurarnos de que la memoria está inicializada
    llm_service._memories[session_id] = ChatMessageHistory()
    
    result = await llm_service.identify_corner_cases(
        session_id=session_id,
        refined_story="Historia refinada",
        feedback="Feedback de prueba",
        existing_corner_cases=["Caso previo"]
    )
    
    assert "corner_cases" in result
    assert isinstance(result["corner_cases"], list)
    assert "corner_cases_feedback" in result
    assert result["corner_cases"] == ["- Caso 1", "- Caso 2"]
    assert result["corner_cases_feedback"] == "Análisis de prueba"
    
    session = llm_service._get_session(session_id)
    assert session.corner_cases == result["corner_cases"]
    assert len(session.interactions) > 0

@pytest.mark.asyncio
async def test_propose_testing_strategy_complete_flow(llm_service):
    """Test el flujo completo de propuesta de estrategia de testing"""
    session_id = llm_service.create_session()
    
    # Asegurarnos de que la memoria está inicializada
    llm_service._memories[session_id] = ChatMessageHistory()
    
    result = await llm_service.propose_testing_strategy(
        session_id=session_id,
        refined_story="Historia refinada",
        corner_cases=["Caso 1", "Caso 2"],
        feedback="Feedback de prueba",
        existing_testing_strategies=["Estrategia previa"]
    )
    
    assert "testing_strategies" in result
    assert isinstance(result["testing_strategies"], list)
    assert "testing_feedback" in result
    assert result["testing_strategies"] == ["- Estrategia 1", "- Estrategia 2"]
    assert result["testing_feedback"] == "Justificación de prueba"
    
    session = llm_service._get_session(session_id)
    assert session.testing_strategy == result["testing_strategies"]
    assert len(session.interactions) > 0

@pytest.mark.asyncio
async def test_process_step_with_invalid_session(llm_service):
    """Test el manejo de sesión inválida en process_step"""
    invalid_session_id = uuid4()
    
    with pytest.raises(ValueError, match="Sesión no encontrada"):
        await llm_service._process_step(
            session_id=invalid_session_id,
            prompt_template="Test prompt",
            input_variables={},
            process_state=ProcessState.REFINEMENT,
            extract_markers=[],
            update_session_callback=lambda s, r: None,
            format_interaction=lambda r: ("human", "ai"),
            post_process_response=None
        )

@pytest.mark.asyncio
async def test_process_step_with_failed_post_processing(llm_service):
    """Test el manejo de errores en post-procesamiento"""
    session_id = llm_service.create_session()
    
    def failing_post_process(sections):
        raise Exception("Post-processing error")
    
    with pytest.raises(Exception, match="Post-processing error"):
        await llm_service._process_step(
            session_id=session_id,
            prompt_template="Test prompt",
            input_variables={},
            process_state=ProcessState.REFINEMENT,
            extract_markers=["**Sección:**"],
            update_session_callback=lambda s, r: None,
            format_interaction=lambda r: ("human", "ai"),
            post_process_response=failing_post_process
        )

@pytest.mark.asyncio
async def test_service_initialization():
    """Test la inicialización del servicio con configuración"""
    mock_llm = Mock(spec=OllamaLLM)
    mock_llm.model = "test-model"
    mock_llm.base_url = "http://test-url"
    mock_llm.temperature = 0.7
    
    config = LLMConfig(
        llm=mock_llm,
        refinement_prompt_template="Template 1",
        corner_case_prompt_template="Template 2",
        testing_strategy_prompt_template="Template 3"
    )
    
    service = LLMService(config=config, llm=mock_llm)
    assert service.llm == mock_llm
    assert service._sessions == {}
    assert service._memories == {}

@pytest.mark.asyncio
async def test_extract_section_with_non_string_input(llm_service):
    """Test la extracción de sección con entrada no string."""
    # Test con un número
    result = llm_service._extract_section(123, "start", "end")
    assert result == "123"
    
    # Test con None
    result = llm_service._extract_section(None, "start", "end")
    assert result == "None"
    
    # Test con objeto
    class TestObj:
        def __str__(self):
            return "test_object"
    result = llm_service._extract_section(TestObj(), "start", "end")
    assert result == "test_object"

@pytest.mark.asyncio
async def test_extract_section_error_handling(llm_service):
    """Test el manejo de errores en extract_section."""
    # Test con texto vacío
    result = llm_service._extract_section("", "start", "end")
    assert result == ""
    
    # Test con marcadores None
    result = llm_service._extract_section("text", None, None)
    assert result == ""
    
    # Test con marcadores vacíos
    result = llm_service._extract_section("text", "", "")
    assert result == "text"

@pytest.mark.asyncio
async def test_add_to_memory_edge_cases(llm_service):
    """Test casos extremos de add_to_memory."""
    session_id = llm_service.create_session()
    
    # Test con mensajes vacíos
    await llm_service._add_to_memory(session_id, "", "")
    memory = llm_service._memories[session_id]
    assert len(memory.messages) == 2
    assert isinstance(memory.messages[0], HumanMessage)
    assert isinstance(memory.messages[1], AIMessage)
    assert memory.messages[0].content == ""
    assert memory.messages[1].content == ""
    
    # Test con mensajes muy largos
    long_message = "x" * 10000
    await llm_service._add_to_memory(session_id, long_message, long_message)
    memory = llm_service._memories[session_id]
    assert len(memory.messages) == 4
    assert memory.messages[2].content == long_message
    assert memory.messages[3].content == long_message
    
    # Test con sesión inválida
    with pytest.raises(KeyError):
        await llm_service._add_to_memory(uuid4(), "test", "test")

@pytest.mark.asyncio
async def test_service_cleanup(llm_service):
    """Test la limpieza de recursos del servicio."""
    # Crear algunas sesiones y memorias
    session_id1 = llm_service.create_session()
    session_id2 = llm_service.create_session()
    
    # Añadir algunos mensajes
    await llm_service._add_to_memory(session_id1, "test1", "test1")
    await llm_service._add_to_memory(session_id2, "test2", "test2")
    
    # Verificar que hay datos antes de cerrar
    assert len(llm_service._memories) == 2
    assert len(llm_service._sessions) == 2
    
    # Verificar que los mensajes se guardaron correctamente
    assert len(llm_service._memories[session_id1].messages) == 2
    assert len(llm_service._memories[session_id2].messages) == 2
    
    # Cerrar el servicio
    await llm_service.close()
    
    # Verificar que se limpiaron los recursos
    assert len(llm_service._memories) == 0
    # Las sesiones deberían mantenerse para referencia
    assert len(llm_service._sessions) == 2
