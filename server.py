import socket, threading, pickle

files = []

def binder(client_socket, address): # binder함수는 서버에서 accept가 되면 생성되는 socket 인스턴스를 통해 client로 부터 데이터를 받으면 echo형태로 재송신하는 메소드이다.

    print('Connected by', address) # 커넥션이 되면 접속 주소가 나온다.

    try:

        while True: # 접속 상태에서는 클라이언트로 부터 받을 데이터를 무한 대기한다.

            data = client_socket.recv(4) # socket의 recv함수는 연결된 소켓으로부터 데이터를 받을 대기하는 함수입니다. 최초 4바이트를 대기합니다.

            length = int.from_bytes(data, 'little') # 최초 4바이트는 전송할 데이터의 크기이다. 그 크기는 little 엔디언으로 byte에서 int형식으로 변환한다.

            data = client_socket.recv(length) # 다시 데이터를 수신한다.

            msg = data.decode() # 수신된 데이터를 str형식으로 decode한다.

            print(msg)

            if msg.strip() == '/파일목록':

                ret = pickle.dumps(files)

                client_socket.sendall(ret)

            else:
            
                data = msg.encode() # 바이너리(byte)형식으로 변환한다.
                
                length = len(data) # 바이너리의 데이터 사이즈를 구한다.
                
                client_socket.sendall(length.to_bytes(4, byteorder = 'little')) # 데이터 사이즈를 little 엔디언 형식으로 byte로 변환한 다음 전송한다.
                
                client_socket.sendall(data) # 데이터를 클라이언트로 전송한다.

    except: # 접속이 끊기면 except가 발생한다.

        print('except : ' + address)

    finally: # 접속이 끊기면 socket 리소스를 닫는다.

        client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 소켓을 만든다.

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 소켓 레벨과 데이터 형태를 설정한다.

server_socket.bind(('192.168.224.222', 8000))

server_socket.listen() # server 설정이 완료되면 listen를 시작한다.

try:

    while True: # 서버는 여러 클라이언트를 상대하기 때문에 무한 루프를 사용한다.

        client_socket, addr = server_socket.accept() # client로 접속이 발생하면 accept가 발생한다. 그럼 client 소켓과 addr(주소)를 튜플로 받는다.

        Thread = threading.Thread(target = binder, args = (client_socket, addr)) # Thread를 이용해서 client 접속 대기를 만들고 다시 accept로 넘어가서 다른 client를 대기한다.

        Thread.start()

except:

    print('server close')

finally: # 에러가 발생하면 서버 소켓을 닫는다.

    server_socket.close()
