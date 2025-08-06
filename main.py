from flask import render_template, url_for, request, jsonify, Flask, session, redirect
import requests
import database
import jwt_token_manager
from  auth_mid_layer import token_required
import uuid
import auth_manager


app = Flask(__name__)

app.secret_key = jwt_token_manager.get_secret_key()

session_store = {}
def is_valid_session():
    global session_store
    session_id = session.get('session_id', '')
    if session_id:
        if session_id in session_store:
            return True
        else:
            if session_id in session:
                session.pop(session_id)
            return False
    else:
        return False

def add_in_session_store(session_id, value):
    global session_store

    session['session_id'] = session_id
    session_store[session_id] = value

def clear_session():
    if 'session_id' in session:
        session_id = session['session_id']
        if session_id in session_store:
            session_store.pop(session_id)
    session.clear()



def get_products_list(products_list):
    ret_list = []
    prod_list = products_list["products"]
    for prod_item in prod_list:
        item = {}
        item["title"] = prod_item["title"]
        item["price"] = prod_item["price"]
        item["description"] = prod_item["description"]
        item["image_url"] = prod_item["thumbnail"]

        ret_list.append(item)
    return ret_list



@app.route("/")
@app.route("/home")
def product_list():
    res_cat = requests.get('https://dummyjson.com/products/category-list')
    categories_list = res_cat.json()
    res_prod = requests.get('https://dummyjson.com/products')
    raw_products_list = res_prod.json()
    products_list = get_products_list(raw_products_list)
    is_session_valid = is_valid_session()
    login_user = ''
    if not is_session_valid:
        products_list = products_list[0:5]
    else:
        session_id = session.get('session_id', '')
        if session_id:
            login_user = session_store.get(session_id,'')


    return render_template('products.html', categories_list= categories_list, products_list=products_list, login_user=login_user)


#signup api endpoint.
@app.route("/signup", methods = ['POST'])
def signup_user():
    user_data = request.get_json()

    #user = database.User(username = user_data['username'], password=user_data['password'], address=)
    user = database.User(**user_data)

    mydb = database.Database()
    all_users = mydb.get_all_users()
    if user['username'] in all_users:
        result = {'status': 'error', 'message': 'User already exist'}
    else:
        mydb.create_user(user)
        result = {'status':'success', 'message': 'User created successfully'}

    return jsonify(result)

# Login api endpoint.
@app.route("/login", methods = ['POST'])
def login_user():
    login_data = request.get_json()
    if not login_data:
        result = {'status': 'error', 'message': 'Please provide user details'}
        return jsonify(result)


    # We should dom some validation of login email and password in a real production project but not necessary here.

    mydb = database.Database()
    login_result = mydb.get_login_result(login_data['username'], login_data['password'])

    if not login_result[0]:
        result = {'status': 'error', 'message': login_result[1]}
    else:
        jwt_token = jwt_token_manager.create_jwt_access_token(login_data['username'])
        if not jwt_token:
            result = {'status': 'error', 'message': 'Unexpected error in creating jwt token'}
        else:
            session_id = uuid.uuid4()  # generate an id for current session
            add_in_session_store(session_id, login_data['username'])

            result = {'status': 'success', 'message': 'User login successfully', 'access_token': jwt_token}


    return jsonify(result)

@app.route("/product_detail", methods = ['GET', 'POST'])
@token_required
def product_detail():
    pass

#--------------------------------------
# login page for login through form posting
@app.route("/login_user", methods = ['GET', 'POST'])
def do_login_user():
    if request.method == "GET":
        login_error = ''
        return render_template('login.html', login_error=login_error)

    login_form = request.form

    mydb = database.Database()
    login_result = mydb.get_login_result(login_form['email'], login_form['password'])

    if not login_result[0]:
        clear_session()
        login_error =  login_result[1]
        return render_template('login.html', login_error=login_error)
    else:

        session_id = uuid.uuid4()  # generate an id for current session

        add_in_session_store(session_id, login_form['email'])
        return redirect(url_for("product_list"))


@app.route("/logout")
def logout():
    clear_session()
    return redirect(url_for('product_list'))

#===================================================
"""
This endpoint will redirect user to google authorization url for google email/pass verification. 
"""
@app.route("/googlelogin")
def google_login():

    redirect_url= request.url_root + "logincallback"

    session["state"] = "SomeStateValue"

    authmgr = auth_manager.AuthManager()
    auth_url = authmgr.get_authorization_url(redirect_url, session["state"])

    return redirect(auth_url)

"""
Callback url that will be called by OAuth server(e.g. google) after successful verification of user.  
"""
@app.route("/logincallback")
def logincallback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    prev_state = request.args.get("state")

    authmgr = auth_manager.AuthManager()
    token_reponse = authmgr.get_access_token(code, authorization_response=request.url, redirect_url=request.url_root + "logincallback", state=prev_state)
    userinfo_response = authmgr.get_userinfo(token_reponse)

    if userinfo_response.json().get("email_verified"):

        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
        mydb = database.Database()
        mydb.add_google_login_in_db(users_email)

        session_id = uuid.uuid4()  # generate an id for current session

        add_in_session_store(session_id, users_email)

        return redirect(url_for("product_list"))
    else:
        return "User email not available or not verified by Google.", 400


if __name__ == "__main__":
    #app.run(debug=True)
    print('starting ...')

    app.run(debug=True, use_debugger=False, use_reloader=False, ssl_context="adhoc")