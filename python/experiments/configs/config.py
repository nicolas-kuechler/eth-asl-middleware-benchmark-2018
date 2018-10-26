
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


VM_CLIENT = [
{
   "name":"Client1",
   "host":"storefvjdk4dylhf5ksshpublicip1.westeurope.cloudapp.azure.com",
   "private_ip":"10.0.0.10"
},
{
   "name":"Client2",
   "host":"storefvjdk4dylhf5ksshpublicip2.westeurope.cloudapp.azure.com",
   "private_ip":"10.0.0.8"
},
{
   "name":"Client3",
   "host":"storefvjdk4dylhf5ksshpublicip3.westeurope.cloudapp.azure.com",
   "private_ip":"10.0.0.7"
}
]

VM_MIDDLEWARE = [
    {
 "name":"Middleware1",
 "host":"storefvjdk4dylhf5ksshpublicip4.westeurope.cloudapp.azure.com",
 "private_ip":"10.0.0.5"
},
{
 "name":"Middleware2",
 "host":"storefvjdk4dylhf5ksshpublicip5.westeurope.cloudapp.azure.com",
 "private_ip":"10.0.0.9"
}
]

VM_SERVER = [
  {
 "name":"Server1",
 "host":"storefvjdk4dylhf5ksshpublicip6.westeurope.cloudapp.azure.com",
 "private_ip":"10.0.0.11"
},
{
 "name":"Server2",
 "host":"storefvjdk4dylhf5ksshpublicip7.westeurope.cloudapp.azure.com",
 "private_ip":"10.0.0.4"
},
{
 "name":"Server3",
 "host":"storefvjdk4dylhf5ksshpublicip8.westeurope.cloudapp.azure.com",
 "private_ip":"10.0.0.6"
}
]
