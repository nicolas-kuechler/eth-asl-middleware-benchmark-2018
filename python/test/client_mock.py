import sys, socket, argparse

use_server_mock = False

parser = argparse.ArgumentParser()
parser.add_argument("-ip")
parser.add_argument("-port", type=int)
args = parser.parse_args()


data_block = 4096 * 'x'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((args.ip, args.port))
s.sendall(f'set memtier-1 0 0 4096\r\n{data_block}\r\n'.encode())
data = s.recv(128)
if not use_server_mock:
    assert(data=='STORED\r\n'.encode())
else:
    assert(data=='ERROR\r\n'.encode())
s.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((args.ip, args.port))
s.sendall(f'set memtier-1 0 4096\r\n{data_block}\r\n'.encode())
data = s.recv(64)
assert(data=='ERROR\r\n'.encode())
s.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((args.ip, args.port))
s.sendall(f'put memtier-2 0 0 4096\r\n{data_block}\r\n'.encode())
data = s.recv(64)
assert(data=='ERROR\r\n'.encode())
s.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((args.ip, args.port))
s.sendall(f'get memtier-3 0 0 4096\r\n{data_block}\r\n'.encode())
data = s.recv(64)
assert(data=='ERROR\r\n'.encode())
s.close()

print(f"passed all tests")
