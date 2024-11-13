import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.fixture
def sample_story():
    return {
        "story": "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal"
    }

def test_refine_story(sample_story):
    response = client.post("/refine_story", json=sample_story)
    assert response.status_code == 200
    assert "refined_story" in response.json()
    assert isinstance(response.json()["refined_story"], str)

def test_identify_corner_cases(sample_story):
    # Primero refinar la historia
    refine_response = client.post("/refine_story", json=sample_story)
    refined_story = refine_response.json()["refined_story"]

    response = client.post("/identify_corner_cases", json={"story": refined_story})
    assert response.status_code == 200
    assert "corner_cases" in response.json()
    assert isinstance(response.json()["corner_cases"], list)

def test_propose_testing_strategy(sample_story):
    # Primero refinar la historia
    refine_response = client.post("/refine_story", json=sample_story)
    refined_story = refine_response.json()["refined_story"]

    # Identificar casos esquinas
    corner_cases_response = client.post("/identify_corner_cases", json={"story": refined_story})
    corner_cases = corner_cases_response.json()["corner_cases"]

    # Proponer estrategias de testing
    response = client.post("/propose_testing_strategy", json={"story": refined_story, "corner_cases": corner_cases})
    assert response.status_code == 200
    assert "testing_strategies" in response.json()
    assert isinstance(response.json()["testing_strategies"], list)
