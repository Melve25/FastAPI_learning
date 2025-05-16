from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List, Optional

class Book(BaseModel):
	title: str
	author: str
	category: str

BOOKS: List[Book] = [
	Book(title='Title One', author='Author One', category='game'),
	Book(title='Title Tow', author='Author Tow', category='game'),
	Book(title='Title Three', author='Author Three', category='movie'),
	Book(title='Title Four', author='Author Four', category='movie'),
	Book(title='Title Five', author='Author Five', category='cartoon')
]



app = FastAPI()
	
# NOTE: GET methods

@app.get('/')
async def mainRout() -> Book:
	return {'message': 'Hello World!'}

@app.get('/all_books')
async def get_all_books() -> List[Book]:
	return BOOKS

# path param
@app.get('/all_books/{book_title}')
async def get_book_by_title(book_title: str) -> Book:
	for book in BOOKS:
		if book.title.casefold() == book_title.casefold():
			return book
		
@app.get('/all_books/{book_author}/')
async def get_book_by_author_category_query(
	book_author: str, category: Optional[str] = None
	) -> List[Book]:

	books_to_return = []
	for book in BOOKS:
		if book.author.casefold() == book_author.casefold():
			if category:
				if book.category.casefold() == category.casefold():
					books_to_return.append(book)
			else:
				books_to_return.append(book)
	return books_to_return
		
# query param
@app.get('/all_books/')
async def get_book_by_category_query(category: str) -> List[Book]:
	books_to_return = []
	for book in BOOKS:
		if book.category.casefold() == category.casefold():
			books_to_return.append(book)

	return books_to_return

# NOTE: POST methods

@app.post('/all_books/create_book') 
async def create_book(new_book: Book = Body()) -> None:
	BOOKS.append(new_book)

# NOTE: PUT methods

@app.put('/all_books/update_book')
async def update_book_by_title(updated_book: Book = Body(
		example={
			'title': 'Title One',
			'author': 'Author One',
			'category': 'game'
		}
	)) -> None:
	for i in range(len(BOOKS)):
		if BOOKS[i].title.casefold() == updated_book.title.casefold():
			BOOKS[i] = updated_book.model_dump()

# NOTE: DELETE methods

@app.delete('/all_book/delete_book/{book_title}')
async def delete_book_by_title(book_title: str) -> None:
	for i in range(len(BOOKS)):
		if BOOKS[i].title.casefold() == book_title.casefold():
			BOOKS.pop(i)
			break