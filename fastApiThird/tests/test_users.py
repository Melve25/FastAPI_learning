from fastapi import status

from .utils import *
from fastapithird.main import app
from fastapithird.routers.user import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
	response = client.get('/user')
	assert response.status_code == status.HTTP_200_OK
	assert response.json()['username'] == 'max'
	assert response.json()['email'] == 'example@.com'
	assert response.json()['first_name'] == 'killa'
	assert response.json()['last_name'] == 'jok'
	assert response.json()['role'] == 'admin'
	assert response.json()['phone_number'] == '+996 123-12-34-56'

def test_change_password_success(test_user):
	response = client.put('/user/change_pass', json={'old_pass': 'qwe', 'new_pass': 'qwer'})

	assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid(test_user):
	response = client.put('/user/change_pass', json={'old_pass': 'e2', 'new_pass': 'qwer'})

	assert response.status_code == status.HTTP_401_UNAUTHORIZED
	assert response.json() == {'detail': 'Old password is wrong'}

def test_change_phone_number_success(test_user):
	response = client.put('/user/change_pho_num', json={'new_phone_number': '12345'})
	assert response.status_code == status.HTTP_204_NO_CONTENT