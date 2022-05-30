import socket, pickle

HOST, PORT = 'localhost', 8000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 소켓을 만든다.

client_socket.connect((HOST, PORT)) # connect 함수로 접속을 한다.

def LoadFileList():

    data = client_socket.recv(1024)

    if not data:

        return data

    ret = pickle.loads(data)

    return ret

try:

    print('** 서버에 접속하였습니다. **') # 서버 연결 시 필수 출력
    
    while [input('ID: '), input('PASS: ')] != ['admin', '1234']: # ID 와 PASS 가 'admin', '1234' 일 때까지 반복

        print('** ID 또는 PASS가 틀렸습니다.! **') # 둘 중 하나 이상이 틀리면 메세지 출력 후 입력 반복

    print('** FTP 서버에 접속하였습니다. **') # 회원 인증 완료 시 출력

    while True: # 무한 반복

        msg = input() # 보낼 메세지 입력

        if msg == '/접속종료': # 접속종료 명령어를 전달받을 경우

            break # 접속을 종료한다.
    
        data = msg.encode() # 메시지를 바이너리(byte)형식으로 변환한다.

        length = len(data) # 메시지 길이를 구한다.
        
        client_socket.sendall(length.to_bytes(4, byteorder = 'little')) # server로 리틀 엔디언 형식으로 데이터 길이를 전송한다.
        
        client_socket.sendall(data) # 데이터를 전송한다.

        if msg == '/파일목록': # 파일목록 명령어를 전달받을 경우

            data = LoadFileList() # 서버에서 파일 목록을 가져온다.

            print('** [File List] **') # 타이틀 출력

            for i in data.keys(): # 파일 목록에 대해 for문을 돌린다.

                print('**', i + f'\t{data[i]}Kb **') # 파일 이름을 출력한다.
            
            print(f'** {len(list(data.keys()))}개 파일 **') # 파일 개수를 출력한다.
        
        if msg.split()[0] == '/업로드': # 업로드 명령어를 전달받을 경우

            directory = msg.split()[1] # 명령어의 인덱스 1은 파일의 경로

            if len(msg.split()) == 3: # 파일 이름까지 입력받은 경우

                filename = msg.split()[2] # 파일 이름은 따로 입력한 파일 이름으로 설정
            
            else: # 아니라면 ( 경로만 입력한 상태라면 )

                filename = msg.split()[1].split('\\')[-1] # 경로의 가장 마지막 부분이 파일 이름

            client_socket.sendall(directory.encode()) # 서버에 파일 경로를 보냄.

            client_socket.sendall(filename.encode()) # 서버에 파일 이름을 보냄.

            reSize = client_socket.recv(1024) # 파일의 크기를 받음

            reSize = reSize.decode() # 파일 크기 디코딩

            if reSize == 'FileNotFoundError': # 만약 해당 경로의 파일을 찾을 수 없다고 반환되었으면

                print('** 파일을 찾을 수 없습니다. **') # 파일을 찾을 수 없다고 출력

                continue # 해당 명령 종료

            status = 'Ready' # 상태 : 준비됨

            client_socket.sendall(status.encode()) # 서버에 해당 상태를 보냄.

            with open('C:\\Users\\DGSW\\Desktop\\Server\\' + filename, 'w', encoding='UTF-8') as f:

                data = client_socket.recv(int(reSize)) # 파일 크기만큼 파일을 받음.

                f.write(data.decode()) # 파일 쓰기
            
            print(f'** {filename} 파일을 업로드하였습니다. **')


        else:


            data = client_socket.recv(4) # server로 부터 전송받을 데이터 길이를 받는다.
            
            length = int.from_bytes(data, 'little') # 데이터 길이는 리틀 엔디언 형식으로 int를 변환한다.
            
            data = client_socket.recv(length) # 데이터 길이를 받는다.
            
            msg = data.decode() # 데이터를 수신한다.
            
except Exception as e:

    print(e)

finally:

    client_socket.close()
