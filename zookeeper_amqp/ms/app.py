import pika
import time
import mysql.connector
import json
import threading
import docker
import os
import docker
import requests
import socket



def callback(ch, method, properties, body):
    print(body)
    body1=body
    dic = json.loads(body)
    print(dic["type"])
    print(dic["value"][0])
    if(dic["type"]==1):
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        cur.execute("INSERT INTO users(username,password) VALUES (%s,%s)",(dic["value"][0],dic["value"][1]))
        print("done")
        sql.commit() 
        sql.close()
    if(dic["type"]==2):
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        sql="DELETE FROM users WHERE username=%s"
        val=[dic["value"],]
        cur.execute(sql,val)
        mysql.commit()
        sql.close()
    if(dic["type"]==3):
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        try:
            cur.execute("INSERT INTO rides(username,_timestamp,source,destination) VALUES (%s,%s,%s,%s)",(dic["ride"][0],dic["ride"][1],dic["ride"][2],dic["ride"][3]))
        except:
            return {'val':400}
        mysql.commit()
        sql.close()
    if(dic["type"]==4):
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        try:
            cur.execute("INSERT INTO urides values(%s, %s)",(dic['ride'][0], dic['ride'][1]))
        except:
            return {'val':400}
        mysql.commit()
        sql.close()
    if(dic["type"]==5):
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        try:
            cur.execute("DELETE FROM rides WHERE rideId = %s",(dic['ride'][0],))
        except:
            return {'val':400}
        mysql.commit()
        sql.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(dic)
    connectionsy = pika.BlockingConnection(pika.ConnectionParameters(host='rmq'))
    channelsy = connectionsy.channel()
    channelsy.exchange_declare(exchange='syncq', exchange_type='fanout')
    channelsy.basic_publish(exchange='syncq', routing_key='', body=body1)
    connectionsy.close()
    print("------------------------Master Done Writting----------------------------")


#read
def callback1(ch,method,properties,body):	
    dic=body.decode('utf-8')
    dic=json.loads(dic)
    if(dic["type"]==1):
        print("-----GOT TYPE 1-----")
        cur=mydb.cursor()
        print(dic["user"])
        qury="SELECT * FROM users WHERE username="+dic["user"]
        cur.execute(qury)
        res=cur.fetchall()
        mydb.commit()

    if(dic["type"]==2):
        print("-----GOT TYPE 2-----")
        cur=mydb.cursor()
        #qry="SELECT * FROM rides WHERE source="+dic["ride"][0]+""
        cur.execute("SELECT * FROM rides WHERE source=%s AND destination=%s",(dic["ride"][0],dic["ride"][1]))
        res=cur.fetchall()
        mydb.commit()

    if(dic["type"]==3):
        print("-----GOT TYPE 3-----")
        cur=mydb.cursor()
        cur.execute("SELECT * FROM rides WHERE rideId=%s",(dic["ride"]))
        res=cur.fetchall()
        mydb.commit()

    if(dic["type"]==4):
        print("-----GOT TYPE 4-----")
        cur=mydb.cursor()
        cur.execute("SELECT * FROM rides WHERE rideId = %s",(dic["ride"]))
        res=cur.fetchall()
        mydb.commit()

    if(dic["type"]==5):
        print("-----GOT TYPE 5-----")
        cur=mydb.cursor()
        cur.execute("SELECT username FROM urides WHERE rideId = %s",(dic["ride"]))
        res=cur.fetchall()
        mydb.commit()
    ch.basic_publish(exchange='',routing_key=properties.reply_to,properties=pika.BasicProperties(correlation_id =properties.correlation_id,delivery_mode=2),body=json.dumps(res))
    ch.basic_ack(delivery_tag=method.delivery_tag)

#write
def callback2(ch,method,properties,body):
    print("------------------IN CALLBACK 2----------------------------")
    dic=body.decode('utf-8')
    dic=json.loads(dic)
    mydb=mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
    cur=mydb.cursor()
    if(dic["type"]==1):
        try:
            cur.execute("INSERT INTO users(username,password) VALUES (%s,%s)",(dic["value"][0],dic["value"][1]))
        except:
            obj={'val':400}
        mydb.commit() 
    if(dic["type"]==2):
        sql="DELETE FROM users WHERE username=%s"
        val=[dic["value"],]
        try:
            cur.execute(sql,val)
            mysql.commit()
        except:
            obj={'val',400}
    if(dic["type"]==3):
        try:
            cur.execute("INSERT INTO rides(username,_timestamp,source,destination) VALUES (%s,%s,%s,%s)",(dic["ride"][0],dic["ride"][1],dic["ride"][2],dic["ride"][3]))
            mysql.commit()
        except:
            obj={'val':400}
        
    if(dic["type"]==4):
        try:
            cur.execute("INSERT INTO urides values(%s, %s)",(dic['ride'][0], dic['ride'][1]))
            mysql.commit()
        except:
            obj={'val':400}
        
    if(dic["type"]==5):
        try:
            cur.execute("DELETE FROM rides WHERE rideId = %s",(dic['ride'][0],))
            mysql.commit()
        except:
            obj={'val':400}
    print("------------------ABOUT TO EXIT CALLBACK 2----------------------------")
    #ch.basic_ack(delivery_tag = method.delivery_tag)


def master1():
    connection3 = pika.BlockingConnection(pika.ConnectionParameters(host='rmq'))
    channel3 = connection3.channel()
    channel3.queue_declare(queue='writeQ', durable=True)
    channel3.basic_qos(prefetch_count=1)
    channel3.basic_consume(queue='writeQ', on_message_callback=callback)
    channel3.start_consuming()
def slaver():
    print("i am here2")
    connection2 = pika.BlockingConnection(pika.ConnectionParameters(host='rmq'))
    channel1 = connection2.channel()
    channel1.queue_declare(queue='readQ')
    channel1.basic_qos(prefetch_count=1)
    channel1.basic_consume(queue='readQ', on_message_callback=callback1)
    channel1.start_consuming()
def slavew():
    print("i am here3")
    connection1 = pika.BlockingConnection(pika.ConnectionParameters(host='rmq'))
    channel2 = connection1.channel()
    channel2.exchange_declare(exchange='syncq', exchange_type='fanout',durable=True)
    result = channel2.queue_declare(queue='', exclusive=True,durable=True)
    queue_name = result.method.queue
    #print(queue_name)
    channel2.queue_bind(exchange='syncq', queue=queue_name)
    channel2.basic_consume(queue=queue_name, on_message_callback=callback2, auto_ack=True)
    channel2.start_consuming()


if __name__ == "__main__":
    master=0
    cont_id=socket.gethostname()
    client=docker.from_env()
    cont_pid=int(client.containers.get(cont_id).top()['Processes'][0][0])
    res=requests.post('http://website:80/api/v1/worker/list').json()
    master_cont_pid=min(res)
    if cont_pid==master_cont_pid:
        print('I AM MASTER!!!!!!!!!!!!!!!!!!!!!!')
        master=1
    else:
        print('I AM SLAVE!!!!!!!!!!!!!!!!!!!!!!')
        master=0
    mydb=mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
    if(master):
        x = threading.Thread(target=master1)
        x.start()
    else:
        x1=threading.Thread(target=slaver)
        x1.start()
        x2=threading.Thread(target=slavew)
        x2.start()
