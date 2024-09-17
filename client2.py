import socket
import threading
import json
import time

class Client:
    def __init__(self, user_id, host='localhost', server_port=5001):
        self.user_id = user_id
        self.host = host
        self.server_port = server_port
        self.online_users = {}
        self.session_users = {}  # 세션에 초대된 사용자 목록
        self.port = self.get_available_port()
        self.ip = socket.gethostbyname(socket.gethostname())
        self.run()

    def get_available_port(self):
        # 임시 소켓을 열어 사용할 수 있는 포트를 자동으로 할당받음
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_socket:
            temp_socket.bind(('', 0))
            return temp_socket.getsockname()[1]

    def run(self):
        self.login_to_server()
        threading.Thread(target=self.receive_messages).start()
        threading.Thread(target=self.periodic_update_online_users).start()
        self.show_menu()

    def login_to_server(self):
        # 로그인 서버에 접속하여 사용자 정보 전송
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.server_port))
        user_info = {'id': self.user_id, 'ip': self.ip, 'port': self.port}
        client_socket.send(json.dumps(user_info).encode())

        # 로그인 서버로부터 온라인 사용자 목록 수신
        data = client_socket.recv(1024).decode()
        self.online_users = json.loads(data)3

        # 온라인 사용자 목록 화면에 출력
        self.print_online_users()

        client_socket.close()

    def update_online_users(self):
        # 로그인 서버에 접속하여 최신 온라인 사용자 목록 수신
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.server_port))
        user_info = {'id': self.user_id, 'ip': self.ip, 'port': self.port}
        client_socket.send(json.dumps(user_info).encode())

        data = client_socket.recv(1024).decode()
        self.online_users = json.loads(data)

        client_socket.close()

    def periodic_update_online_users(self):
        while True:
            time.sleep(5)  # 5초마다 업데이트
            self.update_online_users()

    def print_online_users(self):
        print("Online users:")
        for user_id, info in self.online_users.items():
            print(f"ID: {user_id}, IP: {info['ip']}, Port: {info['port']}")

    def receive_messages(self):
        # 클라이언트의 메시지 수신용 서버 소켓 설정
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(5)

        while True:
            client_socket, client_address = server_socket.accept()
            data = client_socket.recv(1024).decode()
            print(f"Message from {client_address}: {data}")
            client_socket.close()

    def send_message(self, recipient_id, message):
        # 메시지 전송
        if recipient_id in self.online_users:
            recipient_info = self.online_users[recipient_id]
            recipient_host = recipient_info['ip']
            recipient_port = recipient_info['port']

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((recipient_host, recipient_port))
            client_socket.send(message.encode())
            client_socket.close()
        else:
            print(f"User {recipient_id} is not online")

    def invite_user_to_session(self, recipient_id):
        # 사용자를 세션에 초대
        if recipient_id in self.online_users:
            self.session_users[recipient_id] = self.online_users[recipient_id]
            print(f"User {recipient_id} invited to the session")
        else:
            print(f"User {recipient_id} is not online")

    def end_session(self):
        # 세션 종료
        self.session_users.clear()
        print("Session ended")

    def send_message_to_session(self, message):
        # 세션의 모든 사용자에게 메시지 전송
        for recipient_id, recipient_info in self.session_users.items():
            recipient_host = recipient_info['ip']
            recipient_port = recipient_info['port']
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((recipient_host, recipient_port))
            client_socket.send(message.encode())
            client_socket.close()
        print("Message sent to all session users")

    def show_menu(self):
        # 사용자 메뉴 출력 및 처리
        while True:
            print("\nMenu:")
            print("1. Send a message to a user")
            print("2. Invite a user to the session")
            print("3. End the session")
            print("4. Send a message to all session users")
            print("5. Exit")
            choice = input("Enter choice: ")

            if choice == '1':
                recipient_id = input("Enter recipient ID: ")
                message = input("Enter message: ")
                self.send_message(recipient_id, message)
            elif choice == '2':
                recipient_id = input("Enter recipient ID to invite: ")
                self.invite_user_to_session(recipient_id)
            elif choice == '3':
                self.end_session()
            elif choice == '4':
                message = input("Enter message for the session: ")
                self.send_message_to_session(message)
            elif choice == '5':
                break

if __name__ == "__main__":
    user_id = input("Enter your user ID: ")
    client = Client(user_id)
