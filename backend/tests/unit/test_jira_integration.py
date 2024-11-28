import pytest
from unittest.mock import patch, MagicMock
import os
from fastapi import HTTPException
from src.api.routes.jira_integration import get_jira_story, JiraStoryResponse
from src.dependencies import override_llm_service

@pytest.fixture(autouse=True)
def disable_llm_service():
    """Desactiva el servicio LLM para todos los tests"""
    override_llm_service(None)
    yield

@pytest.mark.asyncio
async def test_get_jira_story_success():
    """Test para obtener una historia de Jira exitosamente"""
    mock_issue = {
        'fields': {
            'summary': 'STORYASIS-1: Implementar login',
            'description': 'Como usuario quiero iniciar sesión'
        }
    }

    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.issue.return_value = mock_issue
        MockJira.return_value = mock_jira

        # Configurar variables de entorno
        os.environ['JIRA_URL'] = 'http://test-jira.com'
        os.environ['JIRA_TOKEN'] = 'test-token'

        result = await get_jira_story("STORYASIS-1")
        
        assert isinstance(result, JiraStoryResponse)
        assert result.title == "STORYASIS-1: Implementar login"
        assert result.description == "Como usuario quiero iniciar sesión"
        mock_jira.issue.assert_called_once_with("STORYASIS-1")

@pytest.mark.asyncio
async def test_get_jira_story_no_description():
    """Test para obtener una historia de Jira sin descripción"""
    mock_issue = {
        'fields': {
            'summary': 'STORYASIS-1: Implementar login'
        }
    }

    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.issue.return_value = mock_issue
        MockJira.return_value = mock_jira

        # Configurar variables de entorno
        os.environ['JIRA_URL'] = 'http://test-jira.com'
        os.environ['JIRA_TOKEN'] = 'test-token'

        result = await get_jira_story("STORYASIS-1")
        
        assert isinstance(result, JiraStoryResponse)
        assert result.title == "STORYASIS-1: Implementar login"
        assert result.description == ""

@pytest.mark.asyncio
async def test_get_jira_story_with_empty_description():
    """Test para obtener una historia de Jira con descripción vacía"""
    mock_issue = {
        'fields': {
            'summary': 'STORYASIS-1: Implementar login',
            'description': ''
        }
    }

    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.issue.return_value = mock_issue
        MockJira.return_value = mock_jira

        # Configurar variables de entorno
        os.environ['JIRA_URL'] = 'http://test-jira.com'
        os.environ['JIRA_TOKEN'] = 'test-token'

        result = await get_jira_story("STORYASIS-1")
        
        assert isinstance(result, JiraStoryResponse)
        assert result.title == "STORYASIS-1: Implementar login"
        assert result.description == ""

@pytest.mark.asyncio
async def test_get_jira_story_connection_error():
    """Test para manejar errores de conexión con Jira"""
    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.issue.side_effect = Exception("Connection error")
        MockJira.return_value = mock_jira

        # Configurar variables de entorno
        os.environ['JIRA_URL'] = 'http://test-jira.com'
        os.environ['JIRA_TOKEN'] = 'test-token'

        with pytest.raises(HTTPException) as exc_info:
            await get_jira_story("STORYASIS-1")
        assert exc_info.value.status_code == 500
        assert "Error al conectar con Jira" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_jira_story_missing_env_vars():
    """Test para manejar variables de entorno faltantes"""
    with patch.dict(os.environ, clear=True):
        with pytest.raises(HTTPException) as exc_info:
            await get_jira_story("STORYASIS-1")
        assert exc_info.value.status_code == 500
        assert "Error al conectar con Jira" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_jira_story_with_complex_description():
    """Test para manejar descripciones con formato complejo"""
    mock_issue = {
        'fields': {
            'summary': 'STORYASIS-2: Implementar dashboard',
            'description': '''
            Como usuario administrador quiero:
            
            - Ver estadísticas de uso
            - Generar reportes
            
            Criterios de aceptación:
            * Dashboard responsive
            * Gráficos interactivos
            '''
        }
    }

    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.issue.return_value = mock_issue
        MockJira.return_value = mock_jira

        # Configurar variables de entorno
        os.environ['JIRA_URL'] = 'http://test-jira.com'
        os.environ['JIRA_TOKEN'] = 'test-token'

        result = await get_jira_story("STORYASIS-2")
        
        assert isinstance(result, JiraStoryResponse)
        assert result.title == "STORYASIS-2: Implementar dashboard"
        assert "Como usuario administrador" in result.description
        assert "Criterios de aceptación" in result.description

@pytest.mark.asyncio
async def test_get_jira_story_with_html_description():
    """Test para manejar descripciones con formato HTML"""
    mock_issue = {
        'fields': {
            'summary': 'STORYASIS-3: Integrar sistema de pagos',
            'description': '''
            <h2>Requisitos de integración</h2>
            <ul>
                <li>Soporte para tarjetas de crédito</li>
                <li>Integración con <strong>PayPal</strong></li>
            </ul>
            '''
        }
    }

    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.issue.return_value = mock_issue
        MockJira.return_value = mock_jira

        # Configurar variables de entorno
        os.environ['JIRA_URL'] = 'http://test-jira.com'
        os.environ['JIRA_TOKEN'] = 'test-token'

        result = await get_jira_story("STORYASIS-3")
        
        assert isinstance(result, JiraStoryResponse)
        assert result.title == "STORYASIS-3: Integrar sistema de pagos"
        assert "Requisitos de integración" in result.description
        assert "Soporte para tarjetas de crédito" in result.description

@pytest.mark.asyncio
async def test_get_jira_story_invalid_id_format():
    """Test para manejar IDs de historia con formato inválido"""
    with pytest.raises(HTTPException) as exc_info:
        await get_jira_story("INVALID_FORMAT")
    
    assert exc_info.value.status_code == 404
    assert "ID de historia inválido" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_jira_story_with_additional_jira_fields():
    """Test para manejar respuestas de Jira con campos adicionales"""
    mock_issue = {
        'fields': {
            'summary': 'STORYASIS-4: Implementar autenticación',
            'description': 'Flujo de autenticación',
            'priority': {'name': 'High'},
            'status': {'name': 'In Progress'},
            'assignee': {'displayName': 'John Doe'}
        }
    }

    with patch('src.api.routes.jira_integration.Jira') as MockJira:
        mock_jira = MagicMock()
        mock_jira.issue.return_value = mock_issue
        MockJira.return_value = mock_jira

        # Configurar variables de entorno
        os.environ['JIRA_URL'] = 'http://test-jira.com'
        os.environ['JIRA_TOKEN'] = 'test-token'

        result = await get_jira_story("STORYASIS-4")
        
        assert isinstance(result, JiraStoryResponse)
        assert result.title == "STORYASIS-4: Implementar autenticación"
        assert result.description == "Flujo de autenticación"
