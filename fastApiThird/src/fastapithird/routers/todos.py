from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from pydantic import BaseModel, Field

from typing import Annotated

from ..database import SessionLocal
from .auth import get_current_user
from ..models import Todos


router = APIRouter(
	prefix='/todo',
	tags=['todos']
)


def get_db():
	db = SessionLocal()
	try: 
		yield db
	finally:
		db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

templates = Jinja2Templates(directory='./src/fastapithird/templates')


class TodoRequest(BaseModel):
	title: str = Field(min_length=1)
	description: str = Field(min_length=1)
	priority: int = Field(gt=0, lt=6)
	complete: bool = Field(default=False)

def redirect_to_login():
	redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
	redirect_response.delete_cookie(key='access_token')
	return redirect_response

### Pages ###
@router.get('/todo-page')
async def render_todo_page(request: Request, db: db_dependency):
	try:
		user = await get_current_user(request.cookies.get('access_token'))
		if user is None:
			return redirect_to_login()
		
		todos = db.query(Todos).filter(Todos.user_id == user.get('id')).all()

		return templates.TemplateResponse('todo.html', {'request': request, 'todos': todos, 'user': user})
	except:
		return redirect_to_login()
	
@router.get('/add-todo-page')
async def render_todo_page(request: Request):
	try:
		user = await get_current_user(request.cookies.get('access_token'))
		if user is None:
			return redirect_to_login()
		
		return templates.TemplateResponse('add-todo.html', {'request': request,'user': user})
	except:
		return redirect_to_login()
	
@router.get('/edit-todo-page/{todo_id}')
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
	try:
		user = await get_current_user(request.cookies.get('access_token'))
		if user is None:
			return redirect_to_login()
		
		todo = db.query(Todos).filter(Todos.id == todo_id).first()

		return templates.TemplateResponse('edit-todo.html', {'request': request,'user': user, 'todo': todo})
	
	except:
		return redirect_to_login()

### Endpoints ###


@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):

	return db.query(Todos).filter(Todos.user_id == user.get('id')).all()


@router.get('/{todo_id}', status_code=status.HTTP_200_OK)
async def get_todo_by_id(user: user_dependency, 
						db: db_dependency, 
						todo_id: int = Path(gt=0)):
	
	todo_model = db.query(Todos).filter(Todos.id == todo_id)\
		.filter(Todos.user_id == user.get('id')).first()
	if todo_model is not None:
		return todo_model
	raise HTTPException(status_code=404, detail='Todo not found')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
					  db: db_dependency, 
					  todo_request: TodoRequest):
	
	todo_model = Todos(**todo_request.model_dump(), user_id=user.get('id'))

	db.add(todo_model)
	db.commit()


@router.put('/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
	user: user_dependency,
	db: db_dependency, 
	todo_request: TodoRequest, 
	todo_id: int = Path(gt=0)
	):

	todo_model = db.query(Todos).filter(Todos.id == todo_id)\
		.filter(Todos.user_id == user.get('id')).first()
	
	if todo_model is None:
		raise HTTPException(status_code=404, detail='Todo not found')
	
	todo_model.title = todo_request.title
	todo_model.description = todo_request.description
	todo_model.priority = todo_request.priority
	todo_model.complete = todo_request.complete

	db.add(todo_model)
	db.commit()


@router.delete('/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
					db: db_dependency, 
					todo_id: int = Path(gt=0)
					):
	
	todo_model = db.query(Todos).filter(Todos.id == todo_id)\
		.filter(Todos.user_id == user.get('id')).first()
	if todo_model is None:
		raise HTTPException(status_code=404, detail='Todo not found')
	
	db.query(Todos).filter(Todos.id == todo_id)\
		.filter(Todos.user_id == user.get('id')).delete()
	db.commit()
