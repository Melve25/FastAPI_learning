from fastapi import status

from fastapithird.models import Todos
from fastapithird.main import app
from fastapithird.routers.todos import get_db, get_current_user

from .utils import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# NOTE: get methods tests
def test_read_all_authenticated(test_todo):
	response = client.get('/todo')
	assert response.status_code == status.HTTP_200_OK
	assert response.json() == [{
		'title': 'Hello', 
		'description': 'python',
		'priority': 5,
		'complete': False, 
		'user_id': 1,
		'id': 1}]
	
def test_read_todo_by_id(test_todo):
	response = client.get('/todo/1')
	assert response.status_code == status.HTTP_200_OK
	assert response.json() == {
		'title': 'Hello', 
		'description': 'python',
		'priority': 5,
		'complete': False, 
		'user_id': 1,
		'id': 1}
	
def test_read_todo_by_id_not_found(test_todo):
	response = client.get('/todo/999')
	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert response.json() == {'detail': 'Todo not found'}


# NOTE: post methods tests
def test_create_todo(test_todo):
	request_data = {
		'title': 'new hello',
		'description': 'new new new',
		'priority': 4,
		'complete': False
	}
	response = client.post('/todo', json=request_data)
	assert response.status_code == status.HTTP_201_CREATED

	db = TestingSessionLocal()
	model = db.query(Todos).filter(Todos.id == 2).first()
	assert model.title == request_data.get('title')
	assert model.description == request_data.get('description')
	assert model.priority == request_data.get('priority')
	assert model.complete == request_data.get('complete')
	db.close()


# NOTE: put methods tests
def test_update_todo(test_todo):
	request_data = {
		'title': 'update hello',
		'description': 'update',
		'priority': 3,
		'complete': False
	}
	response = client.put('/todo/1', json=request_data)
	assert response.status_code == status.HTTP_204_NO_CONTENT
	
	db = TestingSessionLocal()
	model = db.query(Todos).filter(Todos.id == 1).first()
	assert model.title == request_data.get('title')
	assert model.description == request_data.get('description')
	assert model.priority == request_data.get('priority')
	assert model.complete == request_data.get('complete')
	db.close()

def test_update_todo_not_found(test_todo):
	request_data = {
		'title': 'update hello',
		'description': 'update',
		'priority': 3,
		'complete': False
	}
	response = client.put('/todo/999', json=request_data)

	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert response.json() == {'detail': 'Todo not found'}

# NOTE: delete methods tests
def test_delete_todo(test_todo):
	response = client.delete('/todo/1')

	assert response.status_code == status.HTTP_204_NO_CONTENT

	db = TestingSessionLocal()
	model = db.query(Todos).filter(Todos.id == 1).first()
	assert model is None
	db.close()

def test_delete_todo_not_found(test_todo):
	response = client.delete('/todo/999')

	assert response.status_code == status.HTTP_404_NOT_FOUND
	assert response.json() == {'detail': 'Todo not found'}