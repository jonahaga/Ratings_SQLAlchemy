from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import correlation

# Scoped Session and session maker help deal with thread safety for multiple users with web apps
engine = create_engine("sqlite:///ratings.db", echo=False)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

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

    def similarity(self, other):
        u_ratings = {}
        paired_ratings = []
        for r in self.ratings:
            u_ratings[r.movie_id] = r

        for r in other.ratings:
            u_r = u_ratings.get(r.movie_id)
            if u_r:
                paired_ratings.append( (u_r.rating, r.rating) )

        if paired_ratings:
            return correlation.pearson(paired_ratings)
        else:
            return 0.0    

    def predict_rating(self, movie):
        ratings = self.ratings
        other_ratings = movie.ratings
        similarities = [ (self.similarity(r.user), r) \
            for r in other_ratings ]
        similarities.sort(reverse = True)
        similarities = [ sim for sim in similarities if sim[0] > 0 ]
        if not similarities:
            return None
        numerator = sum([ r.rating * similarity for similarity, r in similarities ])
        denominator = sum([ similarity[0] for similarity in similarities ])
        return numerator/denominator


class Movie(Base):
    __tablename__= "movies"

    id = Column(Integer, primary_key = True)
    name = Column(String(64), nullable = False)
    released_at = Column(DateTime(timezone = False), nullable = True)
    imdb_url = Column(String(64))

class Rating(Base):
    __tablename__= "ratings"

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'))
    movie_id = Column(Integer, ForeignKey('movies.id'))
    rating = Column(Integer, nullable = False)

    user = relationship("User", backref=backref("ratings", order_by=id))
    movie = relationship("Movie", backref=backref("ratings", order_by=id))

### End class declarations

##functions

def create_new_user(email, password, age, gender, zipcode):
    new_user = User(email=email, password=hash(password), age=age, gender=gender, zipcode=zipcode)
    session.add(new_user)
    session.commit()

def authenticate(email, password):
    user = session.query(User).filter_by(email = email).first()
    
    if user == None:
        return False
    else:
        if hash(password) == int(user.password):
            return int(user.id)
        else:
            return None 

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()