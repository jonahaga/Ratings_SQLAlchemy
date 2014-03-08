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
    email = model.authenticate(email, password)

    print email

    if email == False:
        flash("User does not exist. Please register below.")
        return redirect(url_for("register"))
    elif email != None:
        flash("User authenticated!")
        session['id'] = email
        return redirect(url_for("index"))
    elif email == None:
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

    # Receive form from Register template
    # username = request.form.get("username")
    
    # user_id = model.get_userid_by_name(username)
    # if user_id == None:
    #     username = request.form.get("username")
    #     password = request.form.get("password")
    #     flash("Account successfully created. Please sign in below.")
    #     model.create_account(username, password)
    #     return redirect(url_for("index"))
    # else:
    #     flash("User already exists.")
    #     return redirect(url_for("register"))
   

        model.create_new_user(email, password, age, gender, zipcode)
        return render_template("register.html")

# View User Profile
@app.route("/profile/<user_id>")
def view_user(user_id):
    user_id = model.get_userid_by_email(email)
    ratings = model.get_ratings_by_userid(user_id)
    return render_template("profile.html", ratings = ratings, session = session, user_id = user_id)


if __name__ == "__main__":
    app.run(debug = True)