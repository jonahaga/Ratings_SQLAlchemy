from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

ENGINE = None
Session = None

Base = declarative_base()

### Class declarations go here

#this is nonstandard use of python class attributes... this is for SQLAlchemy only
# if nullable = true it's optional, it can be left blank
#the datatypes in the following are for SQL Alchemy only
class User(Base):
    __tablename__= "users"

    id = Column(Integer, primary_key = True)
    email = Column(String(64), nullable = True)
    password = Column(String(64), nullable = True)
    age = Column(Integer, nullable = True)
    gender = Column(String(8), nullable = True)
    zipcode = Column (String(15), nullable = True)

class Movies(Base):
    __tablename__= "movies"

    id = Column(Integer, primary_key = True)
    name = Column(String(64), nullable = False)
    released_at = Column(DateTime(timezone = False), nullable = True)
    imdb_url = Column(String(64))

class Ratings(Base):
    __tablename__= "ratings"

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    rating = Column(Integer, nullable = False)

    user = relationship("User", backref=backref("ratings", order_by=id))

### End class declarations

def connect():
    global ENGINE
    global Session

    ENGINE = create_engine("sqlite:///ratings.db", echo=True)
    Session = sessionmaker(bind=ENGINE)

    return Session()

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
