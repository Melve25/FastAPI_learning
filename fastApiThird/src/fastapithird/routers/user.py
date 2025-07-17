from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from typing import Annotated
from pydantic import BaseModel, Field
from passlib.context import CryptContext

from ..database import SessionLocal
from .auth import get_current_user
from ..models import Users


class ChangePass(BaseModel):
	old_pass: str = Field(min_length=1)
	new_pass: str = Field(min_length=1)

class ChangePhoNum(BaseModel):
	new_phone_number: str = Field(min_length=1)

router = APIRouter(
	prefix='/user',
	tags=['user']
)

def get_db():
	db = SessionLocal()
	try: 
		yield db
	finally:
		db.close()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
	
	return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put('/change_pass', status_code=status.HTTP_204_NO_CONTENT)
async def change_pass(
	user: user_dependency, 
	db: db_dependency, 
	password: ChangePass):
	
	user_model = db.query(Users).filter(Users.id == user.get('id')).first()
	if user_model is None:
		raise HTTPException(status_code=404, detail="User not found")
	
	if not bcrypt_context.verify(password.old_pass, user_model.hashed_password):
		raise HTTPException(status_code=401, detail='Old password is wrong')
	
	user_model.hashed_password = bcrypt_context.hash(password.new_pass)

	db.add(user_model)
	db.commit()

@router.put('/change_pho_num', status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number: ChangePhoNum):
	user_model = db.query(Users).filter(Users.id == user.get('id')).first()
	if user_model is None:
		raise HTTPException(status_code=404, detail="User not found")
	
	user_model.phone_number = phone_number.new_phone_number
	db.add(user_model)
	db.commit()

