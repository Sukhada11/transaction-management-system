
from flask import Flask, redirect, url_for, request, render_template,session
import pymysql as pb
from flask import json
app = Flask(__name__)
app.secret_key='wef3rf'
db = pb.connect("localhost","root","admin","myonlinebank")
cursor=db.cursor();


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/login', methods=['Get', 'POST'])
def login():
     if request.method == 'POST':
        login  = request.form['login']
        pass1  = request.form['password']


        cursor.execute("SELECT * from users where emailid= '" + login + "' and password='" + pass1 + "'")
        data = cursor.fetchone()
        if data is None:
            message = "Invalid login"
            return render_template('invalid.html')
        else:
            message = "Successful login"
            cursor.execute("SELECT username,id from users where emailid='" + login +"'")
            data = cursor.fetchone()
            session['username'] = data[0]
            session['userid']=data[1]

            return render_template('userhome.html', name=session['username'],id=session['userid'])


@app.route('/signup',methods=['Get','Post'])
def signup():

     if request.method=='POST':
        usrn = request.form['username']
        passw = request.form['password']
        login = request.form['login']


        query = "insert into users(username,emailid,password) values ('%s','%s','%s')"%(usrn,login,passw)
        cursor.execute(query)
        db.commit()
     return render_template('signup.html')

@app.route('/createaccount',methods=['Get','Post'])
def createaccount():


        id=session['userid']
        bal=0
        query = "insert into account(userid,balance) values (%s,%s)"%(id,bal)
        q = "select acno from account ORDER BY acno DESC LIMIT 1 "


        cursor.execute(query)
        cursor.execute(q)
        data=cursor.fetchone();

        no=data[0]
        db.commit()
        return render_template('createaccount.html',no=no, name=session['username'])




@app.route('/transaction',methods=['Get','Post'])
def transaction():
    op=" "
    if request.method=='POST':
        accno = int(request.form['accno'])
        id=session['userid']
        print (accno)
        amount = int(request.form['amount'])
        option = request.form['trans']
        q = "select balance from account where acno = %s " % (accno)
        cursor.execute(q)
        data =cursor.fetchone()
        print(data)
        bal = data[0]
        print (bal)
        if option=='w':
            op="Withdraw"

            if (bal < amount):
                msg = "Insufficient fund in account!"
                return redirect(url_for('failedop'))
            else:
                x= bal - amount
                q = "update account set balance= %s where acno= %s " % (x, accno)
                cursor.execute(q)
                query = "insert into trans(userid,acno,amount,type) values (%s,%s,%s,'%s')" % (id, accno, amount, " withdraw ")
                cursor.execute(query)
                db.commit()
                return redirect(url_for('operationstate'))

        elif option =='d':
            op="Deposite"

            bal = bal + amount
            q = "update account set balance= %s where acno= %s " % (bal, accno)
            cursor.execute(q)
            query = "insert into trans(userid,acno,amount,type) values (%s,%s,%s,'%s')" % (id, accno, amount, " deposite ")
            cursor.execute(query)
            db.commit()
            return redirect(url_for('operationstate'))



    db.commit()
    return render_template('transaction.html',msg=op, name=session['username'])

@app.route('/accountstats')
def accountstats():
    id=int(session['userid'])
    q="select acno,balance from account where userid = %s"%(id)
    cursor.execute(q)
    data=cursor.fetchall()
    print(data)
    print(id)

    return render_template('accountstats.html',data=data, name=session['username'])



@app.route('/mobilerecharge',methods=['Get','Post'])
def mobilerecharge():
    op=" "
    if request.method=='POST':
        accno = int(request.form['accno'])
        mobno = request.form['mobno']
        amount=int(request.form['amount'])
        id=int(session['userid'])
        q = "select balance from account where acno = %s " % (accno)
        cursor.execute(q)
        data = cursor.fetchone()
        print(data)
        bal = data[0]


        if (bal < amount):
            msg = "Insufficient fund in account!"
            return redirect(url_for('failedop'))
        else:
            x = bal - amount
            q = "update account set balance= %s where acno= %s " % (x, accno)
            cursor.execute(q)
            query = "insert into trans(userid,acno,amount,type) values (%s,%s,%s,'%s')" % (id, accno, amount, "mobile recharge")
            cursor.execute(query)
            db.commit()
            return redirect(url_for('operationstate'))
    return render_template('mobilerecharge.html' ,name=session['username'])




@app.route('/fundtransfer',methods=['Get','Post'])
def fundtransfer():

    if request.method=='POST':
        accno1 = int(request.form['accno1'])
        accno2= int(request.form['accno2'])
        amount=int(request.form['amount'])
        id=int(session['userid'])
        q = "select balance from account where acno = %s " % (accno1)
        cursor.execute(q)
        data = cursor.fetchone()

        bal1 = int(data[0])
        q = "select balance from account where acno = %s " % (accno2)
        cursor.execute(q)
        data1 = cursor.fetchone()

        bal2 = int(data1[0])
        print(bal1)
        print(bal2)

        if (bal1 < amount):
            msg = "Insufficient fund in account!"
            return redirect(url_for('failedop'))
        else:
            x = bal1 - amount
            y= bal2 + amount
            q="select userid from account where acno = %s " % (accno1)
            cursor.execute(q)
            z=cursor.fetchone()
            usr1=z[0]
            q = "select userid from account where acno = %s " % (accno2)
            cursor.execute(q)
            z = cursor.fetchone()
            usr2 =z[0]
            q = "update account set balance= %s where acno = %s " % (x, accno1)
            cursor.execute(q)
            query = "insert into trans(userid,acno,amount,type) values (%s,%s,%s,'%s')" % (usr1, accno1, amount, "withdraw")
            cursor.execute(query)
            q = "update account set balance= %s where acno= %s " % (y, accno2)
            query = "insert into trans(userid,acno,amount,type) values (%s,%s,%s,'%s')" % (usr2, accno2, amount, "deposite")
            cursor.execute(query)
            cursor.execute(q)
            db.commit()
            return redirect(url_for('operationstate'))
    return render_template('fundtransfer.html', name=session['username'])












@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def conatact():
    return render_template('contact.html')


@app.route('/try')
def tryme():
    return render_template('try.html')


@app.route('/invalid')
def invalid():
    return redirect(url_for('index'))

@app.route('/operationstate')
def operationstate():

 return render_template('operationstate.html')


@app.route('/failedop')
def failedop():

 return render_template('failedop.html')


@app.route('/mysettings',methods=['Get','Post'])
def mysettings():
    if request.method == 'POST':
        oldpass  = request.form['oldpassword']
        newpass=request.form['newpassword']
        id=int(session['userid'])

        cursor.execute("SELECT * from users where id= %s  and password='%s'" %(id,oldpass))
        data = cursor.fetchone()
        if data is None:
            message = "Invalid login"
            return render_template('invalid.html')
        else:
            message = "Successful login"
            cursor.execute("update users set password = '%s' where id = %s "%(newpass,id))
            db.commit()
            return render_template('operationstate.html')
    return render_template('mysettings.html', name=session['username'])

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/back')
def back():
    return render_template('userhome.html', name=session['username'], id=session['userid'])

@app.route('/feedback')
def feedback():
	return render_template('feedback.html')


if __name__ == '__main__':
	app.run(debug=True)