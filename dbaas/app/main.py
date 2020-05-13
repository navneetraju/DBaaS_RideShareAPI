from flask import Flask, render_template,\
jsonify,request,abort,redirect
import requests
from datetime import datetime
import docker
import pika
import json
import re
import uuid
import time 
import math
from flask_mysqldb import MySQL
from flask_apscheduler import APScheduler
import os
from kazoo.client import KazooClient
from kazoo.client import KazooState


print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++==========================++++++++++++++++++++++++++=')
zk = KazooClient(hosts='zoo:2181')
zk.start()
zk.ensure_path("/slaves")
prev=list()

def spawn_containers(diff,temp):
        for i in range(diff):
            new_cont_name='zookeeper_amqp_consumer_'+str(temp+1)
            temp+=1
            print('------------------------------NEW CONTAINER')
            client=docker.from_env()  
            master_pid=min(requests.post('http://127.0.0.1:80/api/v1/worker/list').json())                                                                                           	
            all_c_list=client.containers.list()
            for i in all_c_list:
                c_name=i.name
                x=re.search("consumer+",c_name)
                if(x):
                    if int(i.top()['Processes'][0][1])==master_pid:
                        master_cont_obj=i
            print('MASTER container------------------------- ',master_cont_obj.name)
            master_cont_obj.exec_run("sh -c 'mysqldump -u root user_rides > data.sql'",stdout=False)
            client=docker.from_env()
            container=client.containers.run(
                    image='zookeeper_amqp_consumer',
                    detach=True,
                    command=" sh -c '/code/worker.sh && sleep 15 && exec python app.py'",
                    volumes={'/home/ubuntu/dbaas':{'bind':'/code','mode':'rw'},
                    '/var/run/docker.sock':{'bind':'/var/run/docker.sock','mode':'rw'}
                    },
                    name=new_cont_name,
                    network='zookeeper_amqp_default'
            )
            container.logs()



@zk.ChildrenWatch('/slaves',send_event=True)
def demo_func(children, event):
    if(event!=None):
        global prev
        print('Children: ',children)
        print('Prev: ',prev)
        if(len(prev)>len(children)):
            num_count=requests.post('http://127.0.0.1:80/get_count').json()
            num_count=int(num_count)
            if num_count==0:
                num_workers=1
            else:
                num_workers=math.ceil(num_count/20)
            work=requests.get('http://127.0.0.1:80/api/v1/worker/list')
            workers=work.json()
            num_actual_workers=len(workers)-1    
            diff=num_actual_workers-num_workers
            if diff == 0:
                print('NO RESTORATION REQUIRED,SLAVE WAS SHUTDOWN')
            elif diff<0:
                diff=abs(diff)
                print("SLAVE KILLED,RESTORING SLAVE...")
                temp=num_actual_workers
                temp+=1
                spawn_containers(1,temp)
        prev=children

app= Flask(__name__)

scheduler=APScheduler()
scheduler.init_app(app)


app.config['MYSQL_HOST']	 = 'count_db' 
app.config['MYSQL_USER']	 = 'user'
app.config['MYSQL_PASSWORD']     = '123'
app.config['MYSQL_DB'] 		 = 'db_count'
app.config['MYSQL_PORT']=3306

mysql=MySQL(app)



def increment_db_count():
        cur=mysql.connection.cursor()
        cur.execute("UPDATE `read_db_count` SET count=count + 1 WHERE `name`='read_db_api_count'")
        mysql.connection.commit()
        cur.close()

def increment_visited_count():
        cur=mysql.connection.cursor()
        cur.execute("UPDATE `read_db_count` SET count=count + 1 WHERE `name`='visited'")
        mysql.connection.commit()
        cur.close()




@app.route('/get_count',methods=["POST"])
def get_count():
    cur=mysql.connection.cursor()
    cur.execute("SELECT `count` FROM `read_db_count` WHERE `name`='read_db_api_count'")
    l = cur.fetchall()
    mysql.connection.commit()
    cur.close()	
    l=l[0][0]
    return jsonify(json.dumps(l)),200

@app.route('/get_visited',methods=["POST"])
def get_visited():
    cur=mysql.connection.cursor()
    cur.execute("SELECT `count` FROM `read_db_count` WHERE `name`='visited'")
    l = cur.fetchall()
    mysql.connection.commit()
    cur.close()	
    l=l[0][0]
    return jsonify(json.dumps(l)),200

@app.route('/scaling')
def scaling():
    num_count=requests.post('http://127.0.0.1:80/get_count').json()
    num_count=int(num_count)
    if num_count==0:
        num_workers=1
    else:
        num_workers=math.ceil(num_count/20)
    work=requests.get('http://127.0.0.1:80/api/v1/worker/list')
    workers=work.json()
    num_actual_workers=len(workers)-1
    #print('Number of Workers Present: ',num_actual_workers)
    #print('Number of Workers There Should Be: ',num_workers)
    diff=num_actual_workers-num_workers
    if diff == 0:
        print('NO SCALING REQUIRED')
    elif diff<0:
        diff=abs(diff)
        print("SCALING OUT....")
        temp=num_actual_workers
        temp+=1
        spawn_containers(diff,temp)
    elif diff>0:
        print("SCALING IN....")
        for i in range(diff):
            t=requests.post('http://127.0.0.1:80/api/v1/crash/slave')



class dbReadClient(object):
        def __init__(self):
            self.connection=pika.BlockingConnection(
                pika.ConnectionParameters(host='rmq')
            )
            self.channel=self.connection.channel()
            result=self.channel.queue_declare(queue='responseQ',exclusive=True)
            self.callback_queue=result.method.queue

            self.channel.basic_consume(
                queue=self.callback_queue,
                on_message_callback=self.on_response,
                auto_ack=True
            )

        def on_response(self,ch,method,props,body):
            if self.corr_id==props.correlation_id:
                self.response=body
        
        def call(self,dic):
            self.response=None
            self.corr_id = str(uuid.uuid4())
            self.channel.basic_publish(
                exchange='',
                routing_key='readQ',
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                ),
                body=str(dic)
            )
            while self.response is None:
                self.connection.process_data_events()
            return self.response

    

def reset_count_main():
    send=requests.post('http://localhost:80/utils/reset')



@app.route("/api/v1/db/write",methods=["POST","DELETE","PUT"])
def write():
    dic=request.get_json()
    print(dic)
    dic=json.dumps(dic)
    connection=pika.BlockingConnection(pika.ConnectionParameters(host='rmq'))
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
    return jsonify(),200

@app.route("/api/v1/db/clear",methods=["POST","DELETE","PUT"])
def clear():
    dic={"type":6}
    dic=json.dumps(dic)
    connection=pika.BlockingConnection(pika.ConnectionParameters(host='rmq'))
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
    return jsonify(),200

@app.route("/api/v1/db/read",methods=["POST","GET"])
def read():
    visited=requests.post('http://127.0.0.1:80/get_visited').json()
    if int(visited) == 0:
        print('--------------------------------------------------------------------------TIMER STARTED---------------------------------------------------------------------------')
        increment_visited_count()
        scheduler.start()
        app.apscheduler.add_job(func=scaling,trigger='interval',minutes=2,id='scaling_id')
        app.apscheduler.add_job(func=reset_count_main,trigger='interval',minutes=2,id='db_read_count_id')    
    prev=requests.post('http://127.0.0.1:80/get_count').json()
    print('Initial Count: ',prev)
    increment_db_count()
    prev=requests.post('http://127.0.0.1:80/get_count').json()
    print('Count incremented to: ',prev)
    read_db_rpc=dbReadClient()
    dic=request.get_json()
    print(dic)
    dic=json.dumps(dic)
    response=read_db_rpc.call(dic)
    response=response.decode("utf-8") 
    #final_dictionary = json.loads(response) 
    read_db_rpc.connection.close()
    return response,200

@app.route("/utils/reset",methods=["POST"])
def reset_count():
        cur=mysql.connection.cursor()
        cur.execute("UPDATE `read_db_count` SET count=0 WHERE `name`='read_db_api_count'")
        mysql.connection.commit()
        cur.close()
        prev=requests.post('http://127.0.0.1:80/get_count').json()
        print('COUNT RESET TO: ',prev)
        return jsonify(),200


@app.route("/api/v1/crash/master",methods=["POST","GET"])
def kill():
    client=docker.from_env()                                                                                                 	
    ar=list_workers().get_json()
    print('LIST: ',ar)
    if len(ar)==0:
        return jsonify(),400
    least_pid=min(ar)
    all_c_list=client.containers.list()
    for i in all_c_list:
        c_name=i.name
        x=re.search("consumer+",c_name)
        if(x):
            if int(i.top()['Processes'][0][1])==least_pid:
                i.kill()
                client.containers.prune()
                t=list()
                t.append(str(least_pid))
                return jsonify(t),200
    return jsonify(),403

@app.route("/api/v1/crash/slave",methods=["POST","GET"])
def kill2():
    client=docker.from_env()
    ar=list_workers().get_json()
    print('LIST: ',ar)
    if len(ar)==0:
        return jsonify(),400
    max_pid=max(ar)
    all_c_list=client.containers.list()
    for i in all_c_list:
        c_name=i.name
        x=re.search("consumer+",c_name)
        if(x):
            if int(i.top()['Processes'][0][1])==max_pid:
                i.kill()
                client.containers.prune()
                t=list()
                t.append(str(max_pid))
                return jsonify(t),200
    return jsonify(),403

@app.route("/api/v1/worker/list",methods=["POST","GET"])
def list_workers():
    client=docker.from_env()
    client.containers.prune()
    workers=list()
    all_c_list=client.containers.list()
    for i in all_c_list:
        c_name=i.name
        x=re.search("consumer+",c_name)
        if(x):
            id=int(i.top()['Processes'][0][1])
            workers.append(id)
    workers.sort()        
    return jsonify(workers)



if __name__ =="__main__":

    
    app.run(debug=False, use_reloader=False)

