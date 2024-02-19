import socket
import threading

# 클라이언트에 전송하는 메세지 코드
START = "START"
play_number = 1
SEND_CREATE = "2000"
# 명령어 코드
JOIN = "JOIN"
BEFORE_GAME = "BEFORE_GAME"
GAME_ING = "GAME_ING"
MOVE_START = "MOVE_START"
MOVE_COMPLETE = "MOVE_COMPLETE"
REMOVE = "REMOVE"
WAIT = "WAIT"
WIN = "WIN"
WINNER = "WINNER"
LOSER = "LOSER"
CLOSE = "CLOSE"
CLOSE_FIN = "CLOSE_FIN"
INIT = "INIT"

# 서버 설정
# SERVER_HOST = '192.168.10.68'
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5557
BUFFER_SIZE = 1024

PLAYER_NUMBER = 2
# 클라이언트 관리를 위한 리스트
client_list = []
# 클라이언트 핸들링 함수


def receive_client(current_client, ):
    global PLAYER_NUMBER
    print(f'New connection from {address}')

    client_list.append(current_client)

    # send_client(client_socket, (play_number).encode("utf-8"))
    # send_queue.put((play_number).encode("utf-8"))
    print(PLAYER_NUMBER)

    while True:
        try:
            receive_data = current_client.recv(BUFFER_SIZE).decode("utf-8")

            if not receive_data:
                break

            data = receive_data.split("\n")
            for msg in data:
                command = msg.split("|")

                if command[0] == JOIN:
                    if PLAYER_NUMBER == 1:
                        PLAYER_NUMBER = 2
                    else:
                        PLAYER_NUMBER = 1

                    current_client.sendall((BEFORE_GAME + "|" + str(PLAYER_NUMBER) + '\n').encode("utf-8"))

                    if len(client_list) == 2:
                        for client in client_list:
                            client.sendall((BEFORE_GAME + "|" + START + '\n').encode("utf-8"))
                            # send_queue.put(START.encode("utf-8"))
                        print("START!")

                elif command[0] == SEND_CREATE:
                    for other_client in client_list:
                        if other_client != current_client:
                            other_client.sendall((GAME_ING + "|" + command[1] + "|" + command[2] + '\n').encode("utf-8"))
                elif command[0] == MOVE_START:
                    for other_client in client_list:
                        if other_client != current_client:
                            other_client.sendall((MOVE_START + "|" + command[1] + "|" + command[2] + '\n').encode("utf-8"))
                elif command[0] == MOVE_COMPLETE:
                    for other_client in client_list:
                        if other_client != current_client:
                            other_client.sendall((MOVE_COMPLETE + "|" + command[1] + "|" + command[2] + '\n').encode("utf-8"))
                elif command[0] == REMOVE:
                    for other_client in client_list:
                        if other_client != current_client:
                            other_client.sendall((REMOVE + "|" + command[1] + "|" + command[2] + '\n').encode("utf-8"))
                elif command[0] == WAIT:
                    for other_client in client_list:
                        if other_client != current_client:
                            other_client.sendall((WAIT + '\n').encode("utf-8"))
                elif command[0] == WIN:
                    current_client.sendall((WINNER + "|" + '\n').encode("utf-8"))
                    for other_client in client_list:
                        if other_client != current_client:
                            other_client.sendall((LOSER + '\n').encode("utf-8"))
                elif command[0] == CLOSE:
                    current_client.sendall((CLOSE_FIN + "|" + '\n').encode("utf-8"))
                    for other_client in client_list:
                        if other_client != current_client:
                            other_client.sendall((INIT + '\n').encode("utf-8"))
                    print("연결 해제")

                    break

        except Exception as e:
            print(f'Error: {e}')
            break

    client_list.remove(current_client)
    current_client.close()

    print(f'Connection from {address} closed')

    # def send_client(client_socket):
    #     while True:
    #         recv = send_queue.get()
    #         client_socket.sendall(recv)


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)

print("NineMenMorris Server Open ")
print(f'Server listening on {SERVER_HOST}:{SERVER_PORT}')

try:
    while True:
        client_socket, address = server_socket.accept()
        client_handler = threading.Thread(target=receive_client, args=(client_socket, ))
        client_handler.start()

except KeyboardInterrupt:
    print("Server is shutting down...")
    server_socket.close()

    # client_send = threading.Thread(target=send_client, args=(client_socket, address))
    # client_send.start()