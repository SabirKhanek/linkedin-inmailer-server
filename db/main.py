from sqlmodel import SQLModel, create_engine, Session, select
import db.models as models

sqlite_file_name="db.sqlite"
sqlite_url=f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)

