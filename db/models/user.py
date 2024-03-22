from sqlmodel import SQLModel, Field, Relationship, JSON, Column

class User(SQLModel, table=True):
    username: str =  Field(default=None, primary_key=True)
    password: str = Field(default=None)

    cookie: dict = Field(default_factory=dict , sa_column=Column(JSON)) 

