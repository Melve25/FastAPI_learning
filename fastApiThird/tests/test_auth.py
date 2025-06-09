from fastapi import status
from datetime import timedelta
from jose import jwt
import pytest
from fastapi import HTTPException

from .utils import *
from fastapithird.main import app
from fastapithird.routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user


app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
	db = TestingSessionLocal()

	authenticated_user = authenticate_user(test_user.username, 'qwe', db)
	assert authenticated_user is not None
	assert authenticated_user.username == test_user.username

	non_existent_user = authenticate_user('wrongUserName','qwe', db)
	assert non_existent_user is False

	wrong_password_user = authenticate_user(test_user.username, 'qwe1', db)
	assert wrong_password_user is False


def test_create_access_token(test_user):
	created_access_token = create_access_token(test_user.username, test_user.id, test_user.role, timedelta(minutes=20))
	
	decoded_token = jwt.decode(created_access_token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

	assert decoded_token['sub'] == test_user.username
	assert decoded_token['id'] == test_user.id
	assert decoded_token['role'] == test_user.role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
	encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
	token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

	user = await get_current_user(token=token)
	assert user == {'username': 'testuser', 'id': 1, 'role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
	encode = {'role': 'user'}
	token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
	
	with pytest.raises(HTTPException) as ex:
		await get_current_user(token=token)

	assert ex.value.status_code == status.HTTP_401_UNAUTHORIZED
	assert ex.value.detail == 'Could not validate user.'
