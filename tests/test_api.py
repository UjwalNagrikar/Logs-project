import pytest
from api.search_api import app, LogSearchAPI
from unittest.mock import Mock, patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestSearchAPI:
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    @patch('api.search_api.requests.post')
    def test_search_logs(self, mock_post, client):
        """Test log search functionality"""
        # Mock OpenSearch response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'hits': {
                'total': {'value': 1},
                'hits': [
                    {
                        '_source': {
                            'timestamp': '2023-10-10T13:55:36Z',
                            'level': 'ERROR',
                            'message': 'Test error message'
                        }
                    }
                ]
            }
        }
        mock_post.return_value = mock_response
        
        response = client.get('/api/search?q=error&level=ERROR')
        assert response.status_code == 200
        data = response.get_json()
        assert 'hits' in data
    
    def test_search_with_invalid_params(self, client):
        """Test search with invalid parameters"""
        response = client.get('/api/search?limit=invalid')
        assert response.status_code == 500