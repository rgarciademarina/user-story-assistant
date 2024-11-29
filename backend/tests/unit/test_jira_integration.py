import pytest
from unittest.mock import patch, MagicMock
import os
from src.api.routes.jira_integration import update_or_create_jira_story, get_jira_story, JiraStoryUpdateRequest, JiraStoryResponse
from fastapi import HTTPException

@pytest.fixture
def mock_env_vars():
    """Configurar variables de entorno para las pruebas"""
    original_env = {
        'JIRA_URL': os.getenv('JIRA_URL'),
        'JIRA_TOKEN': os.getenv('JIRA_TOKEN'),
        'JIRA_PROJECT_KEY': os.getenv('JIRA_PROJECT_KEY')
    }
    
    os.environ['JIRA_URL'] = 'http://test-jira.com'
    os.environ['JIRA_TOKEN'] = 'test-token'
    os.environ['JIRA_PROJECT_KEY'] = 'TEST'
    
    yield
    
    # Restaurar variables originales
    for key, value in original_env.items():
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value

@pytest.fixture(autouse=True)
def disable_llm_service():
    """Desactiva el servicio LLM para todos los tests"""
    from src.dependencies import override_llm_service
    override_llm_service(None)
    yield

class TestJiraIntegration:
    """Tests unitarios para la integración con Jira"""

    @pytest.mark.asyncio
    async def test_validate_story_id_format(self):
        """Probar validación del formato de story_id"""
        valid_ids = ['TEST-123', 'PROJ-1', 'ABC-999']
        invalid_ids = ['TEST123', 'test-123', 'TEST-abc', 'TEST_123', '']

        # Probar IDs válidos
        for valid_id in valid_ids:
            request = JiraStoryUpdateRequest(title="Test Story", story_id=valid_id)
            assert request.story_id == valid_id

        # Probar IDs inválidos
        for invalid_id in invalid_ids:
            with pytest.raises(HTTPException) as exc:
                request = JiraStoryUpdateRequest(title="Test Story", story_id=invalid_id)
                await update_or_create_jira_story(request)
            assert exc.value.status_code == 400
            assert "ID de historia inválido" in str(exc.value.detail)

    @pytest.mark.asyncio
    async def test_missing_env_vars(self):
        """Probar manejo de variables de entorno faltantes"""
        env_vars_to_remove = ['JIRA_URL', 'JIRA_TOKEN', 'JIRA_PROJECT_KEY']
        
        # Guardar valores originales
        original_values = {key: os.environ.get(key) for key in env_vars_to_remove}
        
        # Probar cada combinación de variables faltantes
        for key in env_vars_to_remove:
            # Restaurar todas las variables
            for k, v in original_values.items():
                if v is not None:
                    os.environ[k] = v
            
            # Eliminar una variable específica
            if key in os.environ:
                del os.environ[key]
            
            with pytest.raises(HTTPException) as exc:
                request = JiraStoryUpdateRequest(title="Test Story")
                await update_or_create_jira_story(request)
            assert exc.value.status_code == 500
            assert "Configuración incompleta" in str(exc.value.detail)

        # Restaurar variables originales
        for key, value in original_values.items():
            if value is not None:
                os.environ[key] = value

    @pytest.mark.asyncio
    @patch('src.api.routes.jira_integration.Jira')
    async def test_create_story_success(self, mock_jira_class, mock_env_vars):
        """Probar creación exitosa de historia"""
        mock_jira = MagicMock()
        mock_jira.create_issue.return_value = {'key': 'TEST-123'}
        mock_jira_class.return_value = mock_jira

        request = JiraStoryUpdateRequest(
            title="Nueva Historia",
            description="Descripción de prueba"
        )
        
        response = await update_or_create_jira_story(request)
        
        assert response.story_id == 'TEST-123'
        assert response.action == 'created'
        mock_jira.create_issue.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.api.routes.jira_integration.Jira')
    async def test_update_story_success(self, mock_jira_class, mock_env_vars):
        """Probar actualización exitosa de historia"""
        mock_jira = MagicMock()
        mock_jira.update_issue_field.return_value = None
        mock_jira_class.return_value = mock_jira

        request = JiraStoryUpdateRequest(
            title="Historia Actualizada",
            description="Nueva descripción",
            story_id="TEST-456"
        )
        
        response = await update_or_create_jira_story(request)
        
        assert response.story_id == 'TEST-456'
        assert response.action == 'updated'
        mock_jira.update_issue_field.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.api.routes.jira_integration.Jira')
    async def test_get_story_success(self, mock_jira_class, mock_env_vars):
        """Probar obtención exitosa de historia"""
        mock_issue = {
            'fields': {
                'summary': 'Test Story',
                'description': 'Test Description'
            }
        }
        
        mock_jira = MagicMock()
        mock_jira.issue.return_value = mock_issue
        mock_jira_class.return_value = mock_jira

        response = await get_jira_story('TEST-789')
        
        assert isinstance(response, JiraStoryResponse)
        assert response.title == 'Test Story'
        assert response.description == 'Test Description'
        mock_jira.issue.assert_called_once_with('TEST-789')

    @pytest.mark.asyncio
    @patch('src.api.routes.jira_integration.Jira')
    async def test_get_story_not_found(self, mock_jira_class, mock_env_vars):
        """Probar manejo de historia no encontrada"""
        mock_jira = MagicMock()
        mock_jira.issue.side_effect = Exception("Issue Does Not Exist")
        mock_jira_class.return_value = mock_jira

        with pytest.raises(HTTPException) as exc:
            await get_jira_story('TEST-999')
        
        assert exc.value.status_code == 404
        assert "Historia no encontrada" in str(exc.value.detail)

    @pytest.mark.asyncio
    @patch('src.api.routes.jira_integration.Jira')
    async def test_jira_api_errors(self, mock_jira_class, mock_env_vars):
        """Probar manejo de errores de la API de Jira"""
        mock_jira = MagicMock()
        mock_jira.create_issue.side_effect = Exception("API Error")
        mock_jira_class.return_value = mock_jira

        with pytest.raises(HTTPException) as exc:
            request = JiraStoryUpdateRequest(title="Test Story")
            await update_or_create_jira_story(request)
        
        assert exc.value.status_code == 500
        assert "Error al crear historia" in str(exc.value.detail)
