import os
import tokenize
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# This initailizes the Base class to extend all of our objects from
Base = declarative_base()


# 修改这个
class Viewer(Base):
    # The table name
    __tablename__ = 'punch'
    # A primary key column named ID. This will auto-increment in most databases
    id = Column('id', Integer, primary_key=True)
    token = Column('token', String)
    # A String column to store the IP address
    name = Column('name', String)
    email = Column('email', String)
    data = Column('data', String)
    need_daka = Column('need_daka', String)


# A convenience method to save an instance to the database
def save(model):
    session = Session()
    session.add(model)
    session.commit()
    session.close()

# 凑合用吧……
def update(model):
    session = Session()
    # 获取对应的ID
    view = session.query(Viewer).get(model.id)
    # 所以应该怎么正确更新……
    view.token = model.token
    view.name = model.name
    view.email = model.email
    view.data = model.data
    view.need_daka = model.need_daka
    session.commit()
    session.close()


# A convenience method to save an instance to the database
def delete(id):
    session = Session()
    note = session.query(Viewer).get(id)
    session.delete(note)
    session.commit()
    session.close()


def get(model):
    session = Session()
    allmy = session.query(model).all()
    session.close()
    return allmy


def getOne(id):
    session = Session()
    note = session.query(Viewer).get(id)
    session.close()
    return note


# A convenience method to get the count of a specific model's rows in the databse
def count(model):
    session = Session()
    count = session.query(model).count()
    session.close()
    return count


# This URL will build a sqlite database in memory.
# If this is used, nothing needs to be installed
# but nothing will be saved when the file stops running 
inMemoryDatabaseUrl = 'sqlite:///yifudao.db'

# Similar to how we get a port, this gets a Database URL from the environment.
# Many services may inject a DATABASE_URL to use instead. 
# With our list of requirements, only sqlite and postgresql will work
# but we can easily add more dialects using pip later if we need them
databaseUrl = os.environ.get("DATABASE_URL", inMemoryDatabaseUrl)

# This creates a database engine to access the database url provided. 
# Using the echo=True param, we can see the raw SQL output executed for us
engine = create_engine(databaseUrl, echo=True)

# This will create any tables for all objects defined using Base (see Viewer above)
Base.metadata.create_all(bind=engine)

# This defines a sessionmaker for our engine, allowing us to perform statements
# against the database as part of a session. 
Session = sessionmaker(bind=engine)
