import socket


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("localhost", 11213))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(8096)
            if not data:
                print("break")
                break
            conn.sendall('ERROR\r\n'.encode())
