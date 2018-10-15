import sys, socket, argparse


parser = argparse.ArgumentParser()
parser.add_argument("-ip")
parser.add_argument("-port", type=int)
args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((args.ip, args.port))
data_block = 4096 * 'x'
key_max = 10000
for i in range(key_max+1):
    s.sendall(f'set memtier-{i} 0 0 4096 \r\n{data_block}\r\n'.encode())
    data = s.recv(64)
    assert(data=='STORED\r\n'.encode())
s.close()

print(f'initialized all keys on memcached server {args.ip}:{args.port}')
