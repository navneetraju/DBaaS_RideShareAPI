from flask import Flask, render_template,\
jsonify,request,abort,redirect
import requests
from datetime import datetime
from flask_mysqldb import MySQL
import docker

app= Flask(__name__)

@app.route("/api/v1/db/write",methods=["POST","DELETE","PUT"])
def write():
	dic=request.get_json()
	connection=pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel=connection.channel()
    channel.queue_declare(queue='writeQ',durable=True)
   	channel.basic_publish(
            exchange='',
            routing_key='writeQ',
            body=dic,
            properties=pika.BasicProperties(
                    delivery_mode=2,
            ))	
	connection.close()

@app.route("/api/v1/db/read",methods=["POST","GET"])
def read():
	dic=request.get_json()
	connection=pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel=connection.channel()
    channel.queue_declare(queue='readQ',durable=True)
	channel.basic_publish(
            exchange='',
            routing_key='readQ',
            body=dic,
            properties=pika.BasicProperties(
                    delivery_mode=2,
            ))	
	connection.close()

@app.route("/api/v1/crash/master",methods=["POST","GET"])
def kill():
    client=docker.from_env()
    #todo

@app.route("/api/v1/crash/slave",methods=["POST","GET"])
def kill():
    client=docker.from_env()
    #todo

@app.route("/api/v1/worker/list",methods=["POST","GET"])
def list():
    client=docker.from_env()
    lis=client.list()
    return(jsonify(lis))

if __name__ =="__main__":
	app.run(debug=True)