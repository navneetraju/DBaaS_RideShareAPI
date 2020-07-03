from flask import Flask, render_template,\
jsonify,request,abort,redirect
import requests
from datetime import datetime
from flask_mysqldb import MySQL

def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True

app= Flask(__name__)

app.config['MYSQL_HOST']	 = 'db_user' 
app.config['MYSQL_USER']	 = 'user'
app.config['MYSQL_PASSWORD']     = '123'
app.config['MYSQL_DB'] 		 = 'user_data'
app.config['MYSQL_PORT'] = 3306;

mysql=MySQL(app)

#Users={}
Rides={}
rideId=0
avail=[]

@app.route("/api/v1/_count")
def count():
		cur=mysql.connection.cursor()
		cur.execute("SELECT count FROM counter")
		l = cur.fetchall()
		print(l)
		mysql.connection.commit()
		cur.close()
		return jsonify(l[0]),200

@app.route("/api/v1/_count",methods=["DELETE"])
def reset():
		cur=mysql.connection.cursor()
		cur.execute("UPDATE counter SET count = 0")
		mysql.connection.commit()
		cur.close()
		return jsonify(),200

@app.route("/api/v1/users", methods=["POST","DELETE"])
def adduser1():
	cur=mysql.connection.cursor()
	cur.execute("UPDATE counter SET count = count + 1")
	mysql.connection.commit()
	cur.close()
	return jsonify(),405


@app.route("/api/v1/users", methods=["PUT","GET"])
def adduser():
	cur=mysql.connection.cursor()
	cur.execute("UPDATE counter SET count = count + 1")
	mysql.connection.commit()
	cur.close()

	if(request.method == 'PUT'):
		Users={}
		user=request.get_json()["username"]
		passw=request.get_json()["password"]
		check={"type":1,"user":user}
		Users["value"]=[user,passw]
		Users["type"]=1
		send=requests.post('http://52.4.146.61:80/api/v1/db/read',json=check)
#		return jsonify(send);
		res=send.json()
		cur=mysql.connection.cursor()
		#cur.execute("UPDATE counter SET count = count + 1")
		mysql.connection.commit()
		cur.close()
		if(len(res['val'])!= 0):
			return jsonify("firstone"),400
		else:
			check=is_sha1(passw)
			if check:
				send1=requests.post('http://52.4.146.61:80/api/v1/db/write',json=Users)
				if(send1.status_code==200):
					return jsonify(),201
				else:
					return jsonify(),400
			else:
				return jsonify(),400	
	if(request.method == 'GET'):
		Users={}
		check={"type":5,"user":Users}
		send=requests.post('http://52.4.146.61:80/api/v1/db/read',json=check)
		res=send.json()
		cur=mysql.connection.cursor()
		#cur.execute("UPDATE counter SET count = count + 1")
		mysql.connection.commit()
		cur.close()
		return jsonify(res['val']),200
	else:
		cur=mysql.connection.cursor()
		#cur.execute("UPDATE counter SET count = count + 1")
		mysql.connection.commit()
		cur.close()
		return jsonify(),405


@app.route("/api/v1/users/<username>", methods=["DELETE"])
def deluser(username):
	cur=mysql.connection.cursor()
	cur.execute("UPDATE counter SET count = count + 1")
	mysql.connection.commit()
	cur.close()
	if(request.method == 'DELETE'):
		check={"type":1,"user":username}
		send={}
		send["type"]=2
		send["value"]=username
		rec=requests.post('http://52.4.146.61:80/api/v1/db/read',json=check)
		res=rec.json()
		cur=mysql.connection.cursor()
		#cur.execute("UPDATE counter SET count = count + 1")
		mysql.connection.commit()
		cur.close()
		if(len(res['val'])== 0):
			return jsonify(),400
		else:
			cur=mysql.connection.cursor()
			#cur.execute("UPDATE counter SET count = count + 1")
			mysql.connection.commit()
			cur.close()
			sent=requests.post('http://52.4.146.61:80/api/v1/db/write',json=send)
			if(sent.status_code == 400):
				return jsonify(),400
			else:
				return jsonify(),200
	else:
		return jsonify(),405

@app.route("/api/v1/users/<username>", methods=["PUT","POST","GET"])
def deluser1(username):
	cur=mysql.connection.cursor()
	cur.execute("UPDATE counter SET count = count + 1")
	mysql.connection.commit()
	cur.close()
	return jsonify(),405

if __name__ =="__main__":
	app.run(debug=True)
