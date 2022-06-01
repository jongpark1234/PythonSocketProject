import socket, pickle

HOST, PORT = 'localhost', 8000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 소켓을 만든다.

client_socket.connect((HOST, PORT)) # connect 함수로 접속을 한다.

def LoadFileList(): # 파일 목록을 불러오는 함수 ( pickle 이용 )

    data = client_socket.recv(1024) # 데이터를 가져옴

    if not data: # 데이터가 비었다면

        return data # 피클 작업 해 줄 필요 없이 그냥 보냄

    return pickle.loads(data) # 데이터가 들어있다면 pickle를 통해서 직렬화.

def sendData(data): # 서버에 정보를 보내는 함수

    ret = data.encode() # 메시지를 바이너리(byte)형식으로 변환한다.

    length = len(ret) # 메세지 길이를 받는다.

    client_socket.sendall(length.to_bytes(4, byteorder='little')) # 메세지 길이를 리틀 엔디언 형식으로 서버에 보낸다.

    client_socket.send(ret) # 메세지를 전송한다.

try:

    print('** 서버에 접속하였습니다. **') # 서버 연결 시 필수 출력
    
    while [input('ID: '), input('PASS: ')] != ['admin', '1234']: # ID 와 PASS 가 'admin', '1234' 일 때까지 반복

        print('** ID 또는 PASS가 틀렸습니다.! **') # 둘 중 하나 이상이 틀리면 메세지 출력 후 입력 반복

    print('** FTP 서버에 접속하였습니다. **') # 회원 인증 완료 시 출력

    while True: # 무한 반복

        msg = input() # 보낼 메세지 입력

        if msg == '/접속종료': # 접속종료 명령어를 전달받을 경우

            break # 접속을 종료한다.
    
        sendData(msg)

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

            extension = filename.split('.')[1] # 파일 확장자명 저장 ( svg, jpg, png, txt .... )

            if filename in LoadFileList().keys(): # 만약 중복된 이름이 있다면 #1

                if input('파일이 이미 있습니다. 덮어쓰기 하실건가요??(Yes: 덮어쓰기 / No: 업로드 취소): ').lower() != 'yes': # 덮어씌울지 물어본 뒤

                    print('** 업로드가 취소되었습니다. **') # yes가 아닌 모든 답변은 덮어쓰지 않는(no)다고 생각함.

                    continue # 처음으로 돌아감.
            
            sendData(directory) # 서버로 경로 전송

            sendData(filename) # 서버로 파일명 전송

            sendData(extension) # 서버로 확장자명 전송

            reSize = client_socket.recv(2048) # 파일 크기 수신

            reSize = reSize.decode() # 파일 크기 디코딩
            
            if reSize == '-1': # 만약 해당 경로의 파일을 찾을 수 없다고 반환되었으면

                print('** 파일을 찾을 수 없습니다. **') # 파일을 찾을 수 없다고 출력

                continue # 처음으로 돌아감.

            # 파일 전송 부분 ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ

            file = open(directory, 'rb')

            image_data = file.read(1024)

            while image_data:

                client_socket.send(image_data)

                image_data = file.read(1024)
            
            print('close')

            file.close()

            client_socket.send(b'break')

            print(f'** {filename} 파일을 업로드하였습니다. **')
                

        if msg.split()[0] == '/다운로드': # 다운로드 명령어를 전달받을 경우

            filename = msg.split()[1] # 마지막 인덱스는 다운받을 파일명 

            extension = filename.split('.')[1] # 파일 확장자명 저장 ( svg, jpg, png, txt .... )

            sendData(filename) # 서버로 파일명 전송

            sendData(extension) # 서버로 확장자명 전송

            reSize = client_socket.recv(1024) # 파일 크기 수신 #3

            reSize = reSize.decode() # 파일 크기 디코딩

            if reSize == '-1': # 만약 해당 경로의 파일을 찾을 수 없다고 반환되었으면

                print('** 파일을 찾을 수 없습니다. **') # 파일을 찾을 수 없다고 출력

                continue # 처음으로 돌아감.

            if extension == 'txt':

                with open('D:\\download\\' + filename, 'w', encoding='UTF-8') as f: # 서버 경로로 파일을 연다.

                    data = client_socket.recv(int(reSize)) # 파일 크기만큼 파일을 받음.

                    f.write(data.decode()) # 파일 쓰기
            
            else:

                file = open('C:\\Users\\DGSW\\Desktop\\Server\\' + filename, 'rb')

                image_data = file.read(1024)

                while image_data:

                    client_socket.send(image_data)

                    image_data = file.read(1024)
                
                print('close')

                file.close()

                client_socket.send(b'break')

            print(f'** {filename}을 D:/download/로 다운로드 하였습니다. **')

        else:

            data = client_socket.recv(4) # server로 부터 전송받을 데이터 길이를 받는다.
            
            length = int.from_bytes(data, 'little') # 데이터 길이는 리틀 엔디언 형식으로 int를 변환한다.
            
            data = client_socket.recv(length) # 데이터 길이를 받는다.
            
            msg = data.decode() # 데이터를 수신한다.
            
except Exception as e:

    print(e)

finally:

    client_socket.close()
