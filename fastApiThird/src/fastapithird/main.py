from fastapi import FastAPI

import fastapithird.models as models
from .database import engine
from .routers import auth, todos, admin, user

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.get('/healthy')
def health_check():
	return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)


