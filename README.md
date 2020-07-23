# RideShareAPI
DBaaS Service for RideShare API
### DBaaS service
The DbaaS,users,rides folder have to be pushed to an AWS EC2 instance with at least 8GB RAM in order to allow the service to run smoothly and allow for scaling.   
The DbaaS service has to run in conjunction with the the users and rides VMs.  
To run the users/rides on their respective virtual machines,ensure docker and docker-compose is installed and run:
```
sudo docker-compose up --build  
```
In the DBaaS VM, ensure read-write permissions are given to the root directory by running:
```
chmod 0777 *  
```
Ensure docker and docker-compose are installed and run:
```
sudo docker-compose up --build --scale consumer=2  
```
--scale consumer=2 is given to create 2 workers which based on their PID become master and slave.
