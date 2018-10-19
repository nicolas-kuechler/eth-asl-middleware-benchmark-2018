
## Commands

SET:
 <command name> <key> <flags> <exptime> <bytes> [noreply]\r\n
 <datablock>\r\n


 GET:
 get <key>\r\n


 MULTI-GET:
 get <key> <key> <key> <key>\r\n


 ## Client
 memtier_benchmark --server=10.0.0.9 --port=11211 --protocol=memcache_text --clients=1 --threads=1 --key-maximum=1000


memtier_benchmark --threads=2 --clients=32 --ratio=1:1 --server=localhost --port=6379 --protocol=memcache_text --key-maximum=10000 --data-size=4096 --expiry-range=9999-10000 --json-out-file=client_00.log


### Experiment 21
memtier_benchmark


 ## Middleware



 ## Server
 memcached -l 10.0.0.9 -p 11211 -vv
