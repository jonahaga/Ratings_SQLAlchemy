from flask import Flask, render_template, redirect, request, session, url_for, flash, g
import model

app = Flask(__name__)
app.secret_key = "shhhhthisisasecret"

@app.teardown_request
def shutdown_session(exception = None):
    model.session.remove()

@app.before_request
def load_user_id():
    g.user_id = session.get("user_id")

@app.route("/")
def index():
    if g.user_id:
        return redirect(url_for("view_user", user_id = g.user_id))
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
        session['user_id'] = user_id
        return redirect(url_for("view_user", user_id=user_id))
    elif user_id == None:
        flash("Password incorrect.")
        return redirect(url_for("index"))

@app.route("/register")
def register():
    if g.user_id:
        return redirect(url_for("view_user", user_id = g.user_id))
    return render_template("register.html")  

@app.route("/register", methods=["POST"])
def create_account():
    check_password = request.form["password_verify"]
    email = request.form["email"]
    password = request.form["password"]
    age = request.form["age"]
    gender = request.form["gender"]
    zipcode = request.form["zipcode"]

    if check_password == password:
        model.create_new_user(email, password, age, gender, zipcode)
        flash("Thanks for registering. Please login below.")
        return redirect(url_for("login"))

@app.route("/search", methods=["GET"])
def display_search():
    return render_template("search.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.form['query']
    movies = model.session.query(model.Movie).\
        filter(model.Movie.name.ilike("%" + query + "%")).\
        limit(20).all()

    return render_template("results.html", movies=movies)

# View User Profile
@app.route("/profile/<user_id>")
def view_user(user_id):
    user = model.session.query(model.User).get(user_id)

    if user:
        return render_template("profile.html", user = user)

    return "User not found."

# View Movie Profile
@app.route("/movie_profile/<movie_id>")
def view_movie(movie_id):
    movie = model.session.query(model.Movie).get(movie_id)
    ratings = movie.ratings
    rating_nums = []
    user_rating = None
    for r in ratings:
        if r.user_id == session.get('user_id'):
            user_rating = r
        rating_nums.append(r.rating)
    avg_rating = float(sum(rating_nums))/len(rating_nums)

    prediction = None
    if g.user_id:
        if not user_rating:
            user = model.session.query(model.User).get(g.user_id) 
            prediction = int(user.predict_rating(movie))

    return render_template("movie_profile.html", movie=movie, 
            average=avg_rating, user_rating=user_rating,
            prediction=prediction)

@app.route("/rate/<int:movie_id>", methods=["POST"])
def rate_movie(movie_id):
    rating_number = int(request.form['rating'])
    rating = model.session.query(model.Rating).filter_by(user_id=g.user_id, movie_id=movie_id).first()

    if not rating:
        flash("Rating added", "success")
        rating = model.Rating(user_id=g.user_id, movie_id=movie_id)
        model.session.add(rating)
    else:
        flash("Rating updated", "success")

    rating.rating = rating_number
    model.session.commit()

    return redirect(url_for("view_movie", movie_id=movie_id))

# User List
@app.route("/user_list")
def user_list():
    user_list = model.session.query(model.User).limit(50).all()
    return render_template("user_list.html", users = user_list)

@app.route("/logout")
def logout():
    del session['user_id']
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug = True)