import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import ibm_db
from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=tqf30610;PWD=8puis8ZONsXxj0Vo;", '', '')


@app.route('/email', methods=['GET'])
def email():
    email = request.args.get('email')
    message = Mail(
        from_email='kavinkumarskvp@gmail.com',
        to_emails=email,
        subject='Order Summary',
        html_content='<strong>Your order placed succesfully</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get(
            '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'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
    return render_template("UserWelcome.html")


@app.route('/')
def hello_world():
    return render_template("Login.html")


@app.route('/register')
def signup():
    return render_template("Signup.html")


@app.route('/addProduct')
def addProduct():
    return render_template("AddProducts.html")


@app.route('/storeProduct', methods=['POST'])
def storeProduct():
    name = request.form["name"]
    gender = request.form["gender"]
    query = "INSERT INTO  products VALUES('"+name+"','"+gender+"');"
    ibm_db.exec_immediate(conn, query)
    return redirect(url_for('admin'))


@app.route('/Signup', methods=['POST', 'GET'])
def Signup():
    name = request.form['name']
    email = request.form['email']
    age = request.form['age']
    gender = request.form['gender']
    password = request.form['password']
    query = "INSERT INTO  user VALUES('"+email + \
        "','"+name+"',"+age+",'"+password+"','"+gender+"');"
    ibm_db.exec_immediate(conn, query)
    return render_template("UserWelcome.html")


@app.route('/admin')
def admin():
    query = "Select * from products"
    stmt = ibm_db.exec_immediate(conn, query)
    products = []
    i = 0
    dictionary = ibm_db.fetch_assoc(stmt)
    while dictionary != False:
        products.append(dictionary["NAME"])
        products.append(dictionary["GENDER"])
        print(dictionary)
        dictionary = ibm_db.fetch_assoc(stmt)
    return render_template("ViewProducts.html", len=len(products), products=products)


@app.route('/authLogin', methods=['POST'])
def authLogin():
    password = request.form['password']
    email = request.form['email']
    if email == "admin@admin.com" and password == "ADMIN@FASHION":
        return redirect(url_for('admin'))
    query = "SELECT * FROM user WHERE email =? AND password=?"
    stmt = ibm_db.prepare(conn, query)
    ibm_db.bind_param(stmt, 1, email)
    ibm_db.bind_param(stmt, 2, password)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print(account)
    if account:
        return redirect(url_for('email', email=email))
    else:
        return render_template('login.html', pred="Login unsuccessful. Incorrect username / password !")


if __name__ == '__main__':
    app.run()
