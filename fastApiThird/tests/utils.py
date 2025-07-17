from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import text

from fastapi.testclient import TestClient
import pytest

from fastapithird.database import Base
from fastapithird.main import app
from fastapithird.models import Todos, Users
from fastapithird.routers.auth import bcrypt_context


SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/TestTodoAppDatabase"

test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

def override_get_db():
	db = TestingSessionLocal()
	try: 
		yield db
	finally:
		db.close()

def override_get_current_user():
	return {'username': 'max', 'id': 1, 'role': 'admin'}

client = TestClient(app)

@pytest.fixture
def test_user():
	user = Users(
		email='example@.com',
		username='max',
		first_name='killa',
		last_name='jok',
		hashed_password=bcrypt_context.hash("qwe"),
		is_active=True,
		role='admin',
		phone_number='+996 123-12-34-56'
	)
	db = TestingSessionLocal()
	db.add(user)
	db.commit()
	yield user
	with test_engine.connect() as conn:
		conn.execute(text("DELETE FROM users WHERE id = 1;"))
		conn.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1;"))
		conn.commit()

@pytest.fixture
def test_todo(test_user):
	todo = Todos(
		title='Hello',
		description='python',
		priority=5,
		complete=False,
		user_id=1
	)
	db = TestingSessionLocal()
	db.add(todo)
	db.commit()
	yield todo
	with test_engine.connect() as conn:
		conn.execute(text("DELETE FROM todos;"))
		conn.execute(text("ALTER SEQUENCE todos_id_seq RESTART WITH 1;"))
		conn.commit()