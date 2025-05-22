from typing import List, Optional

from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

from datetime import datetime

app = FastAPI()

class Book(BaseModel):
	id: Optional[int] = Field(description='ID is not needed on create', default=None)
	title: str = Field(min_length=3)
	author: str = Field(min_length=1)
	description: str = Field(min_length=1, max_length=100)
	rating: int = Field(gt=-1, lt=11)
	published_date: Optional[int] = Field(gt=1999, lt=2025, description='Date gets on today', default= None)

	model_config = {
		'json_schema_extra': {
			'example':{
				'title': 'A new book',
				'author': 'max',
				'description': 'A new book description',
				'rating': 10
			}
		}
	}


BOOKS: List[Book] = [
	Book(id=1, title='Title One', author='Author One', description='game', rating=5, published_date=2013),
	Book(id=2, title='Title Tow', author='Author One', description='game', rating=7, published_date=2013),
	Book(id=3, title='Title Three', author='Author Three', description='movie', rating=5, published_date=2012),
	Book(id=4, title='Title Four', author='Author Three', description='movie', rating=10, published_date=2009),
	Book(id=5, title='Title Five', author='Author Five', description='cartoon', rating=4, published_date=2001)
]

# NOTE: get methods

@app.get('/books', response_model=List[Book], status_code=status.HTTP_200_OK)
async def get_all_books() -> List[Book]:
	return BOOKS


@app.get('/books/{book_id}', response_model=Book, status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: int = Path(gt=0)) -> Book:
	for book in BOOKS:
		if book.id == book_id:
			return book
	raise HTTPException(status_code=404, detail='item not found')
		

@app.get('/books/{publish_date}', response_model=List[Book], status_code=status.HTTP_200_OK)
async def get_book_by_date(published_date: int = Path(gt=1999, lt=2025)) -> List[Book]:
	books_to_return = []

	for book in BOOKS:
		if book.published_date == published_date:
			books_to_return.append(book)
	return books_to_return

@app.get('/books/', response_model=List[Book], status_code=status.HTTP_200_OK)
async def get_books_by_rating(rating: int = Query(gt=0, lt=11)) -> List[Book]:
	books_to_return = []
	for book in BOOKS:
		if book.rating == rating:
			books_to_return.append(book)

	return books_to_return



# NOTE: post methods
@app.post('/create-book', response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(book_request: Book) -> Book:
	book = get_book_published_date(find_book_id(book_request))
	BOOKS.append(book)
	return book
	

# NOTE: put methods
@app.put('/books/update_book', status_code=status.HTTP_204_NO_CONTENT)
async def update_book_by_id(update_book: Book):
	book_changed = False
	for i in range(len(BOOKS)):
		if BOOKS[i].id == update_book.id:
			BOOKS[i] = update_book
			book_changed = True 
			return 
	if not book_changed: 
		raise HTTPException(status_code=404, detail='item not found')

# NOTE: delete methods
@app.delete('/books/{book-id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_by_id(book_id: int = Path(gt=0)) -> None:
	book_changed = False
	for i in range(len(BOOKS)):
		if BOOKS[i].id == book_id:
			BOOKS.pop(i)
			book_changed = True 
			return
	if not book_changed: 
		raise HTTPException(status_code=404, detail='item not found')

# NOTE: func to use in app
def get_book_published_date(book:Book) -> Book:
	today = datetime.today()
	book.published_date = int(today.strftime("%Y"))
	return book

def find_book_id(book: Book) -> Book:
	book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
	return book