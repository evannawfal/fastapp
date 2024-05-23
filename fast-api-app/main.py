from fastapi import FastAPI
import databases
import sqlalchemy

DATABASE_URL = "postgresql://my_user:my_password@db:5432/my_database"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

app = FastAPI()

# Example table definition
notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("completed", sqlalchemy.Boolean),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def read_root():
    query = notes.select()
    results = await database.fetch_all(query)
    return results


@app.post("/notes/")
async def create_note(text: str, completed: bool = False):
    query = notes.insert().values(text=text, completed=completed)
    last_record_id = await database.execute(query)
    return {**{"id": last_record_id}, "text": text, "completed": completed}