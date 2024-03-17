# main.py
from contextlib import asynccontextmanager
from typing import Optional, Annotated
from todo import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends, HTTPException


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None, index=True)
    age: Optional[int] = Field(default=None, index=True)
    content: str = Field(index=True)
    address: str = Field(default=None, index=True)


# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Todo API with DB",
              version="0.0.1",
              servers=[
                  {
                      # ADD NGROK URL Here Before Creating GPT Action
                      "url": "http://localhost:8000",
                      "description": "Development Server"
                  }
              ])


def get_session():
    with Session(engine) as session:
        yield session


# simple get request to test
@app.get("/")
def read_root():
    return {"Hello World"}


# read all todos from the database
@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos


# create a todo in the database and return it
@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

# update a todo in the database and return it


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: Todo, session: Annotated[Session, Depends(get_session)]):
    todo_query = session.exec(select(Todo).where(Todo.id == todo_id)).first()
    if not todo_query:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_query.name = todo.name
    todo_query.description = todo.description
    todo_query.age = todo.age
    todo_query.content = todo.content
    todo_query.address = todo.address
    session.commit()
    session.refresh(todo_query)
    return todo_query


#     delete a todo from the database and return it
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    todo_query = session.exec(select(Todo).where(Todo.id == todo_id)).first()
    if not todo_query:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo_query)
    session.commit()
    return {"todo successfully deleted"}
