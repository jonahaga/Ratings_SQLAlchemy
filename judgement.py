from flask import Flask, render_template, redirect, request, session, url_for, flash
import model

app = Flask(__name__)
#this is needed for the session to work
app.secret_key = "shhhhthisisasecret"

@app.route("/")
def index():
    # user_list = model.session.query(model.User).limit(5).all()
    if session.get("email"):
        return "User %s is logged in!" %session['email']
    else:
        return render_template("index.html")

@app.route("/", methods= ["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user_id = model.authenticate(email, password)

    if user_id == False:
        flash("User does not exist. Please register below.")
        return redirect(url_for("register"))
    elif user_id != None:
        flash("You are now logged in!")
        session['id'] = user_id
        return redirect(url_for("view_user", user_id=user_id))
    elif user_id == None:
        flash("Password incorrect.")
        return redirect(url_for("index"))

@app.route("/register")
def register():
   # if session.get("username"):
    return render_template("register.html")  

#when user submits the registration form 
@app.route("/register", methods=["POST"])
def create_account():
    check_password = request.form.get("password_verify")
    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    gender = request.form.get("gender")
    zipcode = request.form.get("zipcode")

    if check_password == password:
        model.create_new_user(email, password, age, gender, zipcode)
        flash("Thanks for registering. Please login below.")
        return redirect(url_for("login"))

# View User Profile
@app.route("/profile/<user_id>")
def view_user(user_id):
    user = model.session.query(model.User).get(user_id)

    if user:
        return render_template("profile.html", user = user)

    return "User not found."

# View Movie Profile
@app.route("/movie_profile/<movie_id>")
#bring in arguments for the specific movie id and the user it was rated by 
def view_movie(movie_id):
    #getting the movie that was selected from users list of movies from profile.html
    movie = model.session.query(model.Movie).get(movie_id)
    ratings = movie.ratings
    rating_nums = []
    user_rating = None
    for r in ratings:
        if r.user_id == session.get('id'):
            user_rating = r
    avg_rating = float(sum(rating_nums))/len(rating_nums)

    # Prediction code: only predict if the user hasn't rated it.
    user = model.session.query(model.User).get(session['id'])
    prediction = None
    if not user_rating:
        prediction = user.predict_rating(movie)
    # End prediction

    return render_template("movie.html", movie=movie, 
            average=avg_rating, user_rating=user_rating,
            prediction=prediction)

@app.route("/rate/<int:movie_id>", methods=["POST"])
def rate_movie(movie_id):
    rating_number = int(request.form['rating'])
    user_id = session.get('id')
    rating = model.session.query(model.Rating).filter_by(user_id=user_id, movie_id=movie_id).first()

    if not rating:
        flash("Rating added", "success")
        rating = model.Rating(user_id=user_id, movie_id=movie_id)
        model.session.add(rating)
    else:
        flash("Rating updated", "success")

    rating.rating = rating_number
    model.session.commit()

    return redirect(url_for("view_movie", movie_id=movie_id))

# User List
@app.route("/user_list")
def user_list():
    user_list = model.session.query(model.User).limit(10).all()
    return render_template("user_list.html", users = user_list)

if __name__ == "__main__":
    app.run(debug = True)