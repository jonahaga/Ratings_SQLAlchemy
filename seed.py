import model
import csv
import datetime

# open a file
# read a line
# parse a line
# create an object
# add the object to a session
# commit
# repeat until done

def load_users(session):
    # use u.user
    # id|age|gender|occupation|zipcode
    # 1|24|M|technician|85711
    with open('seed_data/u.user', 'rb') as f:
        reader = csv.reader(f, delimiter='|')
        for row in reader:
            new_user = model.User(age=int(row[1]), gender=row[2], zipcode=row[4])

            session.add(new_user)
        
    session.commit()

def load_movies(session):
    # use u.item
    with open('seed_data/u.item', 'rb') as f:
        reader = csv.reader(f, delimiter = "|")
        for row in reader:
            date_string = row[2]
            if date_string != "":
                pattern = "%d-%b-%Y"
                formatted_date = datetime.datetime.strptime(date_string, pattern)

            new_movie = model.Movies(name=row[1].decode("latin-1"), released_at=formatted_date, imdb_url=row[3])

            session.add(new_movie)

    session.commit()

def load_ratings(session):
    # use u.data
    with open('seed_data/u.data', 'rb') as f:
        reader = csv.reader(f, delimiter = "\t")
        for row in reader:
            new_rating = model.Ratings(movie_id=row[0], user_id=row[1], rating=row[2])

            session.add(new_rating)

    session.commit()


def main(session):
    # You'll call each of the load_* functions with the session as an argument
    # load_users(session)
    load_movies(session)
    load_ratings(session)

if __name__ == "__main__":
    s = model.connect()
    main(s)
