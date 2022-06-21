import socket
from os import mkdir, remove
from os.path import exists, getsize

HOST, PORT = 'localhost', 8000 # 호스트 아이피와 포트

downloadpath = 'C:\\socketdownload\\' # 다운로드 파일의 경로

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 소켓을 만든다.

client_socket.connect((HOST, PORT)) # connect 함수로 접속을 한다.

def sendData(data): # 정보를 보내는 함수

    ret = data.encode() # 메시지를 바이너리(byte)형식으로 변환한다.

    length = len(ret) # 메세지 길이를 받는다.

    client_socket.sendall(length.to_bytes(4, byteorder='little')) # 메세지 길이를 리틀 엔디언 형식으로 보낸다.

    client_socket.sendall(ret) # 메세지를 전송한다.

def recieveData(): # 정보를 받는 함수

    data = client_socket.recv(4) # 메세지 길이를 받아온다.

    length = int.from_bytes(data, 'little') # 리틀 엔디언 형식에서 int 형식으로 변환한다.

    data = client_socket.recv(length) # 데이터를 받아온다.

    msg = data.decode() # 수신된 데이터를 str형식으로 decode한다.

    return msg # 받은 데이터를 반환(전달)한다.

def sendFile(dir): # 파일을 보내는 함수

    size = 10485760 if getsize(dir) > 1073741824 else 1024 # 송수신 파일이 1GB를 초과하면 매 번 10MB씩 데이터를 보내고, 아닌 파일은 1KB씩 데이터를 보냄.

    client_socket.sendall(size.to_bytes(4, byteorder='little')) # 크기를 리틀 엔디언 형식으로 보낸다.

    try:

        file = open(dir, 'rb') # 전송할 파일을 엶

        image_data = file.read(size) # 파일을 읽음

        while image_data: # 파일 읽기가 끝날 때까지

            client_socket.send(image_data) # 현재까지 읽은 데이터를 서버에 전송함.

            image_data = file.read(size) # 파일을 다시 읽음
        
        file.close() # 전송이 끝난 파일을 닫음

        client_socket.send(b'break') # 파일 전송을 완료 하였다고 신호를 보냄.

    except: # 어떤 문제가 발생했을 시

        file.close() # 전송중이던 파일을 닫음

        client_socket.send(b'error') # 에러 메세지를 보냄

        assert(KeyboardInterrupt) # 클라이언트를 끊음

def recieveFile(dir): # 파일을 받는 함수

    data = client_socket.recv(4) # 크기를 받아온다.

    size = int.from_bytes(data, 'little') # 리틀 엔디언 형식에서 int 형식으로 변환한다.

    file = open(dir, 'wb') # 서버로 경로를 엶.

    while True: # 무한 반복

        image_chunk = client_socket.recv(size) # 데이터를 받아옴.

        if image_chunk[-5:] == b'break': # 데이터를 다 받았다는 신호를 받으면

            file.write(image_chunk[:-5]) # 남은 데이터를 보내준 뒤

            break # 파일 읽기를 끝냄.
        
        if image_chunk[-5:] == b'error': # 에러가 발생했다는 신호를 받으면

            file.close() # 파일을 닫음

            remove(dir) # 해당 파일을 삭제함.

            return # 파일 읽기를 끝냄.

        file.write(image_chunk) # 데이터를 파일로 보내줌.

    file.close() # 파일을 닫음.

try:

    print('** 서버에 접속하였습니다. **') # 서버 연결 시 필수 출력
    
    while True: # ID 와 PASS 가 맞을 때까지 반복

        sendData('/로그인')

        sendData(input('ID: ') + ' ' + input('PASS: ')) # ID와 PASS를 입력받고 서버 공백을 기준으로 구분하여 서버에 보냄.

        if recieveData() == 'True': # 수신받은 메세지가 올바르다는 뜻의 True 라면
            
            break # 로그인 과정을 끝냄

        print('** ID 또는 PASS가 틀렸습니다.! **') # 둘 중 하나 이상이 틀리면 메세지 출력 후 입력 반복

    print('** FTP 서버에 접속하였습니다. **') # 회원 인증 완료 시 출력

    while True: # 무한 반복

        msg = input() # 보낼 메세지 입력

        if msg == '/접속종료': # 접속종료 명령어를 전달받을 경우

            break # 접속을 종료한다.
    
        sendData(msg) # 입력받은 메세지를 서버에 보냄

        if msg == '/파일목록': # 파일목록 명령어를 전달받을 경우

            print('** [File List] **') # 타이틀 출력
            
            filelist = recieveData() # 파일 목록을 받아옴

            length = 0 if filelist.split('\n') == [''] else len(filelist.split('\n')) # 파일 개수는 얻은 데이터의 개행 개수. 개행이 없다면 정보가 있는지 확인하고 있으면 1, 없으면 0.

            print(filelist) # 파일 목록 출력

            print(f'** {length}개 파일 **') # 파일 개수를 출력한다.
        
        elif msg.split()[0] == '/업로드': # 업로드 명령어를 전달받을 경우

            directory = msg.split()[1] # 명령어의 인덱스 1은 파일의 경로

            if len(msg.split()) == 3: # 파일 이름까지 입력받은 경우

                filename = msg.split()[2] # 파일 이름은 따로 입력한 파일 이름으로 설정
            
            else: # 아니라면 ( 경로만 입력한 상태라면 )

                filename = msg.split()[1].split('\\')[-1] # 경로의 가장 마지막 부분이 파일 이름
            
            if not exists(directory): # 만약 해당 경로의 파일을 찾을 수 없다고 반환되었으면

                print('** 파일을 찾을 수 없습니다. **') # 파일을 찾을 수 없다고 출력

                continue # 처음으로 돌아감.
            
            sendData(filename) # 서버에 파일명을 보냄

            if recieveData() == 'True': # 만약 중복된 이름이 있다면

                weather = input('파일이 이미 있습니다. 덮어쓰기 하실건가요??(Yes: 덮어쓰기 / No: 업로드 취소): ').lower() # 덮어씌울지 물어봄.

                if weather != 'yes': # 덮어씌우지 않는다고 했다면 ( yes가 아닌 모든 답변은 덮어쓰지 않는(no)다고 생각함. )

                    print('** 업로드가 취소되었습니다. **') # 취소했다고 메세지 출력

                    sendData('False') # 서버에 덮어씌우지 않는다고 선언

                    continue # 처음으로 돌아감.

                else: # 덮어씌운다고 했다면

                    sendData('True') # 서버에 덮어씌운다고 선언
            
            sendFile(directory) # 파일을 서버에 전송함

            print(f'** {filename} 파일을 업로드하였습니다. **') # 파일 업로드 성공 메세지 출력

        elif msg.split()[0] == '/다운로드': # 다운로드 명령어를 전달받을 경우

            if not exists(downloadpath): # 아직 다운로드를 받은 적이 없다면
                
                mkdir(downloadpath) # 다운로드 파일을 받을 경로 생성

            filename = msg.split()[1] # 마지막 인덱스는 다운받을 파일명 

            sendData(filename) # 서버로 파일명 전송

            if recieveData() == 'False': # 만약 해당 경로의 파일을 찾을 수 없다고 반환되었으면

                print('** 파일을 찾을 수 없습니다. **') # 파일을 찾을 수 없다고 출력

                continue # 처음으로 돌아감.

            recieveFile(downloadpath + filename) # 파일을 서버에 전송함

            print(f'** {filename}을 {downloadpath}로 다운로드 하였습니다. **') # 파일 다운로드 성공 메세지 출력

        else:

            pass
            
except Exception as e: # 접속이 끊어진다면

    print('연결이 끊어졌습니다.') # 끊어졌다고 알려줌

finally: # 프로그램이 끝날 때

    client_socket.close() # 소켓을 종료함
