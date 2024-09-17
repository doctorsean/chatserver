import socket
import threading
import json

class LoginServer:
    def __init__(self, host='localhost', port=5001):
        self.host = host
        self.port = port
        self.users = {}  # 사용자 목록

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Login server started on {self.host}:{self.port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        data = client_socket.recv(1024).decode()
        user_info = json.loads(data)
        user_id = user_info['id']
        self.users[user_id] = user_info

        # 현재 온라인 사용자 목록 전송
        users_json = json.dumps(self.users)
        print(f"Sending online users: {users_json}")  # 디버깅 출력 추가
        client_socket.send(users_json.encode())
        client_socket.close()

        # 사용자 목록 파일에 저장
        with open('users.json', 'w') as f:
            json.dump(self.users, f, indent=4)

if __name__ == "__main__":
    server = LoginServer()
    server.start_server()
