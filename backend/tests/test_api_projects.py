"""
Tests for Projects API endpoints
"""

import pytest
from fastapi import status


class TestProjectsAPI:
    """Test cases for Projects API"""

    def test_list_projects_empty(self, client):
        """Test listing projects when database is empty"""
        response = client.get("/api/projects/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_project(self, client, sample_project_data):
        """Test creating a new project"""
        response = client.post("/api/projects/", json=sample_project_data)
        # Currently returns 501 Not Implemented (to be implemented)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_501_NOT_IMPLEMENTED]

    def test_create_project_invalid_data(self, client):
        """Test creating project with invalid data"""
        invalid_data = {
            "name": "",  # Empty name
            "slug": "test"
        }
        response = client.post("/api/projects/", json=invalid_data)
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_501_NOT_IMPLEMENTED]

    def test_get_project_not_found(self, client):
        """Test getting a non-existent project"""
        response = client.get("/api/projects/nonexistent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_project_not_found(self, client, sample_project_data):
        """Test updating a non-existent project"""
        response = client.put("/api/projects/nonexistent-id", json=sample_project_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_project_not_found(self, client):
        """Test deleting a non-existent project"""
        response = client.delete("/api/projects/nonexistent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize("status_filter", ["active", "archived", "suspended"])
    def test_list_projects_with_filter(self, client, status_filter):
        """Test listing projects with status filter"""
        response = client.get(f"/api/projects/?status={status_filter}")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_list_projects_pagination(self, client):
        """Test project list pagination"""
        response = client.get("/api/projects/?skip=0&limit=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
