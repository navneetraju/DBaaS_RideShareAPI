import docker
client = docker.APIClient(base_url='unix://var/run/docker.sock')
container=client.create_container(
image='zookeeper_amqp_consumer',
command="sh -c 'sleep 1500'",
volumes=['/code','/var/run/docker.sock'],
host_config=client.create_host_config(binds={
'/code':{
'bind':'.',
'mode':'rw',
},
'/var/run/docker.sock':{
'bind':'/var/run/docker.sock',
'mode':'rw',
}
})
)
client.start(container=container.get('Id'))