import socket

HOST = '10.80.162.18'

PORT = 8000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 소켓을 만든다.

client_socket.connect((HOST, PORT)) # connect함수로 접속을 한다.

try:

    print('** 서버에 접속하였습니다. **') # 서버 연결 시 필수 출력
    
    while [input('ID: '), input('PASS: ')] != ['admin', '1234']: # ID 와 PASS 가 'admin', '1234' 일 때까지 반복

        print('** ID 또는 PASS가 틀렸습니다.! **') # 둘 중 하나 이상이 틀리면 메세지 출력 후 입력 반복

    print('** FTP 서버에 접속하였습니다. **') # 회원 인증 완료 시 출력

    while True: # 무한 반복

        msg = input() # 보낼 메세지 입력
        
        data = msg.encode() # 메시지를 바이너리(byte)형식으로 변환한다.

        length = len(data) # 메시지 길이를 구한다.
        
        client_socket.sendall(length.to_bytes(4, byteorder = 'little')) # server로 리틀 엔디언 형식으로 데이터 길이를 전송한다.
        
        client_socket.sendall(data) # 데이터를 전송한다.
        
        data = client_socket.recv(4) # server로 부터 전송받을 데이터 길이를 받는다.
        
        length = int.from_bytes(data, 'little') # 데이터 길이는 리틀 엔디언 형식으로 int를 변환한다.
        
        data = client_socket.recv(length) # 데이터 길이를 받는다.
        
        msg = data.decode() # 데이터를 수신한다.
        
        print('Received from :', msg) # 데이터를 출력한다.

except:

    print('연결 종료')

finally:

    client_socket.close()
