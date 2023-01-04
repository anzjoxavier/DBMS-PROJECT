from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
import json

# MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='ANZ JO'


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/newdbms'
db=SQLAlchemy(app)

# here we will create db models that is tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))

class land(db.Model):
    aid=db.Column(db.Integer,primary_key=True)
    landid=db.Column(db.String(20))
    ownid=db.Column(db.String(20))
    ward=db.Column(db.String(20))
    landmark=db.Column(db.String(20))

class warddetails(db.Model):
    cid=db.Column(db.Integer,primary_key=True)
    ward=db.Column(db.String(100))

class vaccinestatus(db.Model):
    aid=db.Column(db.Integer,primary_key=True)
    ctid=db.Column(db.String(100))
    name=db.Column(db.String(20))
    vstatus=db.Column(db.String(10))
    dov=db.Column(db.String(20))

class Trig(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    ctid=db.Column(db.String(100))
    action=db.Column(db.String(100))
    timestamp=db.Column(db.String(100))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))





class citizen(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    ctid=db.Column(db.String(50))
    sname=db.Column(db.String(50))
    dob=db.Column(db.String(20))
    gender=db.Column(db.String(50))
    ward=db.Column(db.String(50))
    email=db.Column(db.String(50))
    number=db.Column(db.String(12))
    address=db.Column(db.String(100))
    

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/citizendetails')
def citizendetails():
    query=db.engine.execute(f"SELECT * FROM `citizen`") 
    return render_template('citizendetails.html',query=query)

@app.route('/landdetails')
def landdetails():
    query=db.engine.execute(f"SELECT * FROM `land`") 
    return render_template('landdetails.html',query=query)


@app.route('/vaccinedetails')
def vaccinedetails():
    query=db.engine.execute(f"SELECT * FROM `vaccinestatus`") 
    return render_template('vaccinedetails.html',query=query)



@app.route('/triggers')
def triggers():
    query=db.engine.execute(f"SELECT * FROM `trig`") 
    return render_template('triggers.html',query=query)

@app.route('/warddetails',methods=['POST','GET'])
def warddetails():
    if request.method=="POST":
        ward1=request.form.get('wardname')
        query=warddetails.query.filter_by(ward=ward1).first()
        if query:
            flash("WARD ALREADY EXIST","warning")
            return redirect('/warddetails')
        dep=warddetails(ward=ward1)
        db.session.add(dep)
        db.session.commit()
        flash("WARD UPDATED","success")
    return render_template('warddetails.html')

@app.route('/vaccinestatus',methods=['POST','GET'])
def addvaccinestatus():
    query=db.engine.execute(f"SELECT * FROM `citizen`") 
    if request.method=="POST":
        ctid1=request.form.get('ctid')
        name1=citizen.query.filter_by(ctid=ctid1).first()
        name2=vaccinestatus.query.filter_by(ctid=ctid1).first()
        if name2:
            flash("VACCINE STATUS ALREADY UPDATED","warning")
            return redirect('/vaccinestatus')
        vstatus=request.form.get('vacs')
        dov=request.form.get('dov')
        print(vstatus,ctid1)
        vs=vaccinestatus(ctid=ctid1,name=name1.sname,vstatus=vstatus,dov=dov)
        db.session.add(vs)
        db.session.commit()
        flash("VACCINE STATUS UPDATED","warning")

        
    return render_template('vaccine.html',query=query)

@app.route('/search',methods=['POST','GET'])
def search():
    if request.method=="POST":
        ctid=request.form.get('ctid')
        bio=citizen.query.filter_by(ctid=ctid).first()
        vacs=vaccinestatus.query.filter_by(ctid=ctid).first()
        ct1=land.query.filter_by(ownid=ctid).first()
        ct=land.query.filter_by(ownid=ctid)
        return render_template('search.html',bio=bio,vacs=vacs,ct=ct)
        
    return render_template('search.html')

@app.route("/delete/<string:id>",methods=['POST','GET'])
@login_required
def delete(id):
    db.engine.execute(f"DELETE FROM `citizen` WHERE `citizen`.`id`={id}")
    flash("Citizen Deleted Successful","danger")
    return redirect('/citizendetails')

@app.route("/deleteland/<string:id>",methods=['POST','GET'])
@login_required
def deleteland(id):
    db.engine.execute(f"DELETE FROM `land` WHERE `land`.`aid`={id}")
    flash("Land Deleted Successful","danger")
    return redirect('/landdetails')

@app.route("/edit/<string:id>",methods=['POST','GET'])
@login_required
def edit(id):
    ward1=db.engine.execute("SELECT * FROM `warddetails`")
    posts=citizen.query.filter_by(id=id).first()
    if request.method=="POST":
        ctid=request.form.get('ctid')
        sname=request.form.get('sname')
        dob=request.form.get('dob')
        gender=request.form.get('gender')
        ward=request.form.get('ward')
        email=request.form.get('email')
        num=request.form.get('num')
        address=request.form.get('address')
        query=db.engine.execute(f"UPDATE `citizen` SET `ctid`='{ctid}',`sname`='{sname}',`dob`='{dob}',`gender`='{gender}',`ward`='{ward}',`email`='{email}',`number`='{num}',`address`='{address}' WHERE `citizen`.`id`={id}")
        flash("Details Updated","success")
        return redirect('/citizendetails')
    
    return render_template('edit.html',posts=posts,ward1=ward1)

@app.route("/editland/<string:id>",methods=['POST','GET'])
@login_required
def editland(id):
    ward1=db.engine.execute("SELECT * FROM `warddetails`")
    posts=land.query.filter_by(aid=id).first()
    ct=db.engine.execute("SELECT * FROM `citizen`")
    if request.method=="POST":
        landid=request.form.get('landid')
        ownid=request.form.get('ownid')
        wardl=request.form.get('ward')
        lm=request.form.get('lm')
        query=db.engine.execute(f"UPDATE `land` SET `landid`='{landid}',`ownid`='{ownid}',`ward`='{wardl}',`landmark`='{lm}' WHERE `land`.`aid`={id}")
        flash("Land Details Updated","success")
        return redirect('/landdetails')
    
    return render_template('editland.html',posts=posts,ward1=ward1,ct=ct)


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)

        new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encpassword}')")

        # this is method 2 to save data in db
        # newuser=User(username=username,email=email,password=encpassword)
        # db.session.add(newuser)
        # db.session.commit()
        flash("Signup Succes Please Login","success")
        return render_template('login.html')

          

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        username=request.form.get('username')
        password=request.form.get('password')
        user=User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))



@app.route('/addcitizen',methods=['POST','GET'])
@login_required
def addcitizen():
    ward1=db.engine.execute("SELECT * FROM `warddetails`")
    if request.method=="POST":
        ctid=request.form.get('ctid')
        sname=request.form.get('sname')
        dob=request.form.get('dob')
        gender=request.form.get('gender')
        ward=request.form.get('ward')
        email=request.form.get('email')
        num=request.form.get('num')
        address=request.form.get('address')
        query=db.engine.execute(f"INSERT INTO `citizen` (`ctid`,`sname`,`dob`,`gender`,`ward`,`email`,`number`,`address`) VALUES ('{ctid}','{sname}','{dob}','{gender}','{ward}','{email}','{num}','{address}')")
    

        flash("Citizen Added Successfully","info")


    return render_template('citizen.html',ward1=ward1)



@app.route('/addland',methods=['POST','GET'])
@login_required
def addland():
    ward1=db.engine.execute("SELECT * FROM `warddetails`")
    query=db.engine.execute(f"SELECT * FROM `citizen`") 
    if request.method=="POST":
        landid=request.form.get('landid')
        name2=land.query.filter_by(landid=landid).first()
        if name2:
            flash("LAND ALREADY EXIST","warning")
            return redirect('/addland')
        ownid=request.form.get('oid')
        lm=request.form.get('lm')
        wardl=request.form.get('wardl')
        query1=db.engine.execute(f"INSERT INTO `land` (`landid`,`ownid`,`ward`,`landmark`) VALUES ('{landid}','{ownid}','{wardl}','{lm}')")    
        flash("Land Details Added Successfully","info")

    return render_template('land.html',ward1=ward1,query=query)


@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My database is not Connected'


app.run(debug=True)    



