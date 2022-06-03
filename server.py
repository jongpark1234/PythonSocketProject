import socket
import threading
from os import listdir, remove
from os.path import exists, getsize

serverpath = 'C:\\Users\\DGSW\\Desktop\\Server\\' # 서버 파일의 경로
downloadpath = 'D:\\download\\' # 다운로드 파일의 경로

def getFileSize(directory): # 파일 크기를 불러오는 함수

    if not exists(directory): # 파일 경로가 존재하지 않는다면

        return '-1' # -1을 반환해줌.

    return str(getsize(directory)) # 파일이 존재하면 파일의 크기를 반환해줌.

def sendData(data): # 정보를 보내는 함수

    ret = data.encode() # 메시지를 바이너리(byte)형식으로 변환한다.

    length = len(ret) # 메세지 길이를 받는다.

    client_socket.sendall(length.to_bytes(4, byteorder='little')) # 메세지 길이를 리틀 엔디언 형식으로 서버에 보낸다.

    client_socket.send(ret) # 메세지를 전송한다.

def recieveData(): # 정보를 받는 함수

    data = client_socket.recv(4) # 메세지 길이를 받아온다.

    length = int.from_bytes(data, 'little') # 리틀 엔디언 형식에서 int 형식으로 변환한다.

    data = client_socket.recv(length) # 데이터를 받아온다.
    
    msg = data.decode() # 수신된 데이터를 str형식으로 decode한다.

    return msg # 받은 데이터를 반환(전달)한다.

def recieveFile(dir): # 파일을 받는 함수

    file = open(dir, 'wb') # 서버로 경로를 엶.

    while True: # 무한 반복

        image_chunk = client_socket.recv(1024) # 데이터를 받아옴.

        if image_chunk[-5:] == b'break': # 데이터를 다 받았다는 신호를 받으면

            file.write(image_chunk[:-5]) # 남은 데이터를 보내준 뒤

            print('Done Recieving.')

            break # 파일 읽기를 끝냄.
        
        if image_chunk[-5:] == b'error': # 에러가 발생했다는 신호를 받으면

            file.close() # 파일을 닫음

            remove(dir) # 해당 파일을 삭제함.

            print('Error Occured')

            return # 파일 읽기를 끝냄.

        file.write(image_chunk) # 데이터를 파일로 보내줌.

    file.close() # 파일을 닫음.

def binder(client_socket, address): # binder함수는 서버에서 accept가 되면 생성되는 socket 인스턴스를 통해 client로 부터 데이터를 받으면 echo형태로 재송신하는 메소드이다.

    print(f'{address[0]} 연결됨') # 커넥션이 되면 접속 주소가 나온다.

    try:

        while True: # 접속 상태에서는 클라이언트로 부터 받을 데이터를 무한 대기한다.

            msg = recieveData() # 메세지를 클라이언트로부터 받아온다.

            if msg.strip() == '/로그인': # 로그인 명령을 받았을 때

                ID = recieveData()

                PASS = recieveData()

                if [ID, PASS] == ['admin', '1234']:

                    sendData('break')
                
                else:

                    sendData('retry')

            elif msg.strip() == '/파일목록': # 파일 목록 명령을 받았을 때

                sendData('\n'.join([f'** {i}\t{round(int(getsize(serverpath + i)) / 1024)}Kb **' for i in listdir(serverpath)]))

            elif msg.split()[0] == '/업로드': # 업로드 명령을 받았을 때

                directory = recieveData() # 파일 경로 받기

                filename = recieveData() # 파일 이름 받기

                sendData(getFileSize(directory)) # 파일 크기를 전송함

                recieveFile(serverpath + filename) # 파일을 받음

            elif msg.split()[0] == '/다운로드':

                filename = recieveData() # 클라이언트로부터 파일명 수신

                directory = serverpath + filename # 파일 경로

                sendData(getFileSize(directory)) # 파일 크기를 전송함

                recieveFile(downloadpath + filename) # 파일을 받음

            else:
            
                pass

    except: # 접속이 끊기면 except가 발생한다.
        
        print(f'{str(address[0])} 연결 끊김')

    finally: # 접속이 끊기면 socket 리소스를 닫는다.

        client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 소켓을 만든다.

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 소켓 레벨과 데이터 형태를 설정한다.

server_socket.bind(('localhost', 8000))

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
