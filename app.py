from flask import Flask , render_template,redirect,url_for,session,flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField , PasswordField
from wtforms.validators import DataRequired , Email , ValidationError
import bcrypt
from flask_mysqldb import MySQL


app = Flask(__name__)

#MySql Configiration

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydatabase'
app.secret_key='your_secret_key_here'

mysql = MySQL(app)


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Ragister')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Ragister')


@app.route('/')
def index():

    return render_template('index.html')

@app.route('/register' , methods = ['GET' , 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name , email , password) VALUES(%s , %s , %s)",(name , email ,hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))
    
    return render_template('register.html',form = form)

@app.route('/login', methods=['GET' , 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8') , user[3].encode('utf-8')):
            session['id'] = user[0]
            return redirect(url_for('dashbord'))
        else:
            flash("Login Failed Please Check Your Email And Password")
            return redirect(url_for('login'))    


    return render_template('login.html' ,form=form)

@app.route('/dashbord')
def dashbord():
    if 'id' in session:
        id = session['id']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s",(id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('Dashbord.html',user=user)
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('id' , None)
    flash("You Have Been Logged Out Successfully.")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)