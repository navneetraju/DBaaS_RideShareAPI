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
from kazoo.client import KazooClient
from kazoo.client import KazooState




def callback(ch, method, properties, body):
    print('inside master callback')
    body1=body
    dic = json.loads(body)
    if(dic["type"]==1):
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        try:
            cur.execute("INSERT INTO users(username,password) VALUES (%s,%s)",(dic["value"][0],dic["value"][1]))
        except:
            print('SOME ERROR') 
        print("done")
        sql.commit() 
        sql.close()
    if(dic["type"]==2):
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        try:
            query="delete from users where username="+dic["value"]
            cur.execute(query)
        except:
            print('NOT DELETING!!!!')
        sql.commit()
        sql.close()
    if(dic["type"]==3):
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        try:
            cur.execute("INSERT INTO rides(username,_timestamp,source,destination) VALUES (%s,%s,%s,%s)",(dic["ride"][0],dic["ride"][1],dic["ride"][2],dic["ride"][3]))
        except:
            print('SOME ERROR')
        sql.commit()
        sql.close()
    if(dic["type"]==4):
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        try:
            cur.execute("INSERT INTO urides values(%s, %s)",(dic['ride'][0], dic['ride'][1]))
        except:
            print('SOME ERROR')
        sql.commit()
        sql.close()
    if(dic["type"]==5):
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        try:
            query="DELETE FROM rides WHERE rideId="+str(dic['ride'][0])
            cur.execute(query)
        except:
            print('SOME ERROR')
        sql.commit()
        sql.close()
    if(dic["type"]==6):
        print('---------------------TYPE 6------------')
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        try:
            cur.execute("DELETE FROM urides")
            sql.commit()
            cur.execute("DELETE FROM rides")
            sql.commit()
            cur.execute("DELETE FROM users")
            sql.commit()
            cur.execute("ALTER TABLE rides AUTO_INCREMENT=1")
            sql.commit()
            print('done deleting')
            #print('done commiting')
        except mysql.connector.Error as err:
            print('SOME ERROR IN DELETING')
            print("Something went wrong: {}".format(err))
        try:
            sql.commit()
            print('committed')
        except:
            print('SOME ERROR IN committing')
        sql.close()
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(dic)
    connectionsy = pika.BlockingConnection(pika.ConnectionParameters(host='rmq'))
    channelsy = connectionsy.channel()
    channelsy.exchange_declare(exchange='syncq', exchange_type='fanout')
    channelsy.basic_publish(exchange='syncq', routing_key='', body=body1,properties=pika.BasicProperties(correlation_id =properties.correlation_id,delivery_mode=2))
    connectionsy.close()
    print("------------------------Master Done Writting----------------------------")


#read
def callback1(ch,method,properties,body):	
    dic=body.decode('utf-8')
    dic=json.loads(dic)
    print('inside read callback')
    print('dic ',dic)
    print(type(dic))
    print(dic["type"])
    if(dic["type"]==1):
        print("-----GOT TYPE 1-----")
        cur=mydb.cursor()
        print(dic["user"])
        qury="SELECT * FROM users WHERE username="+dic["user"]
        #cur.execute("SELECT * FROM users WHERE username=%s",(dic["user"]))
        cur.execute(qury)
        res=cur.fetchall()
        mydb.commit()

    if(dic["type"]==2):
        print("-----GOT TYPE 2-----")
        cur=mydb.cursor()
        cur.execute("SELECT * FROM rides WHERE source=%s AND destination=%s",(dic["ride"][0],dic["ride"][1]))
        res=cur.fetchall()
        mydb.commit()

    if(dic["type"]==3):
        print("-----GOT TYPE 3-----")
        cur=mydb.cursor()
        query="SELECT * FROM rides WHERE rideId="+str(dic["ride"])
        cur.execute(query)
        res=cur.fetchall()
        mydb.commit()

    if(dic["type"]==4):
        users=[]
        print("-----GOT TYPE 4-----")
        cur=mydb.cursor()
        try:
            query="SELECT * FROM rides WHERE rideId="+str(dic["ride"])
            cur.execute(query)
        except:
            print('Error Here-cur')
        res1=cur.fetchall()
        print('res1: ',res1)
        val=(dic["ride"])
        cur1=mydb.cursor()
        try:
            query="SELECT username FROM urides WHERE rideId="+str(dic["ride"])
            cur1.execute(query)
        except:
            print('Error Here-cur1')
        res2=cur1.fetchall()
        for i in res2:
            users.append(i[0])
        if(len(res1)==0):
            res=res1
        ret={}
        ret["rideId"]=res1[0][0]
        ret["created_by"]=res1[0][1]
        ret["users"]=users
        ret["timestamp"]=res1[0][2]
        ret["source"]=res1[0][3]
        ret["destination"]=res1[0][4]
        if(len(res1)!=0):
            res=ret
    if(dic["type"]==5):
        print("-----GOT TYPE 5-----")
        cur=mydb.cursor()
        cur.execute("SELECT username FROM users")
        l=cur.fetchall()
        mydb.commit()
        m=[]
        for i in l:
            m.append(i[0])
        res=m
    if(dic["type"]==6):
        print('-------GOT TYPE 6------')
        cur=mydb.cursor()
        cur.execute("SELECT COUNT(*) FROM rides")
        l=cur.fetchall()
        mydb.commit()
        print('done!',str(l[0][0]))
        res=str(l[0][0])
    l={"val":res}
    ch.basic_publish(exchange='',routing_key=properties.reply_to,properties=pika.BasicProperties(correlation_id =properties.correlation_id,delivery_mode=2),body=json.dumps(l))
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
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        try:
            query="delete from users where username="+dic["value"]
            cur.execute(query)
        except:
            print('NOT DELETING!!!!')
        sql.commit()
        sql.close()
    if(dic["type"]==3):
        try:
            cur.execute("INSERT INTO rides(username,_timestamp,source,destination) VALUES (%s,%s,%s,%s)",(dic["ride"][0],dic["ride"][1],dic["ride"][2],dic["ride"][3]))
            mydb.commit()
        except:
            obj={'val':400}
        
    if(dic["type"]==4):
        try:
            cur.execute("INSERT INTO urides values(%s, %s)",(dic['ride'][0], dic['ride'][1]))
            mydb.commit()
        except:
            obj={'val':400}
        
    if(dic["type"]==5):
        try:
            cur.execute("DELETE FROM rides WHERE rideId = %s",(dic['ride'][0],))
            mydb.commit()
        except:
            obj={'val':400}
    if(dic["type"]==6):
        print('---------------------TYPE 6------------')
        sql= mysql.connector.connect(host="localhost",user="root",passwd="",database="user_rides")
        cur=sql.cursor()
        try:
            cur.execute("DELETE FROM urides")
            sql.commit()
            cur.execute("DELETE FROM rides")
            sql.commit()
            cur.execute("DELETE FROM users")
            sql.commit()
            cur.execute("ALTER TABLE rides AUTO_INCREMENT=1")
            sql.commit()
            print('done deleting')
            #print('done commiting')
        except mysql.connector.Error as err:
            print('SOME ERROR IN DELETING')
            print("Something went wrong: {}".format(err))
        try:
            sql.commit()
            print('committed')
        except:
            print('SOME ERROR IN committing')
        sql.close()
    print("------------------ABOUT TO EXIT CALLBACK 2----------------------------")

    #ch.basic_ack(delivery_tag = method.delivery_tag)

class slave():
    def __init__(self):
        self.connection2 = pika.BlockingConnection(pika.ConnectionParameters(host='rmq'))
        self.channel1 = self.connection2.channel()
        self.channel1.queue_declare(queue='readQ')
        self.channel1.basic_qos(prefetch_count=1)
        self.channel1.basic_consume(queue='readQ', on_message_callback=callback1)
        self.connection1 = pika.BlockingConnection(pika.ConnectionParameters(host='rmq'))
        self.channel2 = self.connection1.channel()
        self.channel2.exchange_declare(exchange='syncq', exchange_type='fanout')
        self.result = self.channel2.queue_declare(queue='', exclusive=True)
        self.queue_name = self.result.method.queue
        self.channel2.queue_bind(exchange='syncq', queue=self.queue_name)
        self.channel2.basic_consume(queue=self.queue_name, on_message_callback=callback2)
        self.slaver_thread = threading.Thread(target=self.runslaver)
        self.slaver_thread.start()
        print('SLAVE R CONSUMING!')
        self.slavew_thread = threading.Thread(target=self.runslavew)
        self.slavew_thread.start()
        print('SLAVE W CONSUMING!')
        
    def runslaver(self):
        try:
            self.channel1.start_consuming()
        except:
            return
        
    def runslavew(self):
        try:
            self.channel2.start_consuming()
        except:
            return

    def stop_slave(self):
        try:
            self.channel1.stop_consuming()
        except:
            print('error channel1')
        try:
            self.channel2.stop_consuming()
        except:
            print('error channel2')
        self.slaver_thread.join()
        self.slavew_thread.join()
        

class masterworker():
    def __init__(self):
        #threading.Thread.__init__(self)
        #self.name=name
        self.connection3 = pika.BlockingConnection(pika.ConnectionParameters(host='rmq'))
        self.channel3 = self.connection3.channel()
        self.channel3.queue_declare(queue='writeQ', durable=True)
        self.channel3.basic_qos(prefetch_count=1)
        self.channel3.basic_consume(queue='writeQ', on_message_callback=callback)
        self.master_thread = threading.Thread(target=self.run)
        self.master_thread.start()
    def run(self):
        try:
            print('master consuming')
            self.channel3.start_consuming()
        except:
            print('SOME PROBLEM RUNNING MASTER')
        finally:
            print('ended master')
    def __del__(self):
        try:
            print('DESTRUCTING!!!!!!!!!!!!!!!!!!!!')
            self.channel3.stop_consuming()
            #self.connection1.close()
        except:
            print('some problem in destuction')

def watch_master(event):
    if(event!=None):
        global master
        if(master):
            return 
        else:
            print('INSIDE WATCH_MASTER!!!!!!!!!!!!!!!!!!')
            cont_id=socket.gethostname()
            client=docker.from_env()
            cont_pid=int(client.containers.get(cont_id).top()['Processes'][0][1])
            res=requests.post('http://website:80/api/v1/worker/list').json()
            master_cont_pid=min(res)
            if cont_pid==master_cont_pid:
                print('SLAVE BECOMING MASTER!!')
                master=1
                global slave_obj
                slave_obj.stop_slave()
                zk.create("/master", b"master node",ephemeral=True)
                print('SLAVE IS NOW MASTER!!!!!')
                cont_id=socket.gethostname()
                current_node_name="/slaves/node"+cont_id
                zk.delete(current_node_name)
                startmaster()
                
            else:
                print('I AM STILL SLAVE')
                master=0
                started_watch=0
                while(started_watch==0):
                    try:
                        zk.get("/master", watch=watch_master)
                    except:
                        continue
                    started_watch=1

def startmaster():
    global newmaster
    newmaster=masterworker()
	newmaster.master_thread.join()
if __name__ == "__main__":
    master=0
    global zk
    global newmaster
    zk = KazooClient(hosts='zoo:2181')
    zk.start()
    cont_id=socket.gethostname()
    client=docker.from_env()
    cont_pid=int(client.containers.get(cont_id).top()['Processes'][0][1])
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
        zk.create("/master", b"master node",ephemeral=True)
        print('HERE=--=-=-=')
        x = masterworker()
        #x.start()
        #x.join()
    else:
        zk.ensure_path("/slaves")
        node_name="/slaves/node"+cont_id
        zk.create(node_name, b"slave node",ephemeral=True)
        started_watch=0
        while(started_watch==0):
            try:
                zk.get("/master", watch=watch_master)
            except:
                continue
            started_watch=1
        print('master watch set')
        #x1=slaver()
        #x1.run()
        #x2=slavew()
        #x2.run()
        slave_obj=slave()
        
