
BASE_DIR = "C:/Development/asl-fall18-project"

EXP_TEST_TIME = 80

EXP_REMOVE_FILES_VM = False
EXP_REMOVE_FILES_LOCAL = False

VM_MW_PORT = 6379
VM_MEMCACHED_PORT = 11211

AZURE_CREDENTIALS_FILE = "C:/Users/nicok/.ssh/asl/asl-experiment-master.json"

MONGODB_IP = "localhost"
MONGODB_PORT = 27017

SSH_USERNAME = "kunicola"
SSH_PRIVATE_KEY_FILE = "C:/Users/nicok/.ssh/asl/asl-private-openssh.ppk"

NOTIFY_URL = "https://notify.run/c/YbbTbFoj0Yn9vUuN"


VM_CLIENT = [
{
   "name":"Client1",
   "host":"storev5akpxc5salm4sshpublicip1.westeurope.cloudapp.azure.com",
   "private_ip":"10.0.0.11"
},
{
   "name":"Client2",
   "host":"storev5akpxc5salm4sshpublicip2.westeurope.cloudapp.azure.com",
   "private_ip":"10.0.0.9"
},
{
   "name":"Client3",
   "host":"storev5akpxc5salm4sshpublicip3.westeurope.cloudapp.azure.com",
   "private_ip":"10.0.0.7 "
}
]

VM_MIDDLEWARE = [
    {
 "name":"Middleware1",
 "host":"storev5akpxc5salm4sshpublicip4.westeurope.cloudapp.azure.com",
 "private_ip":"10.0.0.10"
},
{
 "name":"Middleware2",
 "host":"storev5akpxc5salm4sshpublicip5.westeurope.cloudapp.azure.com",
 "private_ip":"10.0.0.5"
}
]

VM_SERVER = [
  {
 "name":"Server1",
 "host":"storev5akpxc5salm4sshpublicip6.westeurope.cloudapp.azure.com",
 "private_ip":"10.0.0.4"
},
{
 "name":"Server2",
 "host":"storev5akpxc5salm4sshpublicip7.westeurope.cloudapp.azure.com",
 "private_ip":"10.0.0.8"
},
{
 "name":"Server3",
 "host":"storev5akpxc5salm4sshpublicip8.westeurope.cloudapp.azure.com",
 "private_ip":"10.0.0.6"
}
]
