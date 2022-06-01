import socket
import os
import threading
import pickle
import math
from os.path import exists, getsize

files = {}

def getFileSize(directory):

    fileSize = getsize(directory)

    return str(fileSize)

def getFileData(directory):

    with open(directory, 'r', encoding="UTF-8") as f:

        data = ''

        for i in f:

            data += i

    return data

def recieveData(): # 클라이언트로부터 데이터를 받는 함수

    data = client_socket.recv(4) # 메세지 길이를 받아온다.

    length = int.from_bytes(data, 'little') # 리틀 엔디언 형식에서 int 형식으로 변환한다.

    data = client_socket.recv(length) # 데이터를 받아온다.
    
    msg = data.decode() # 수신된 데이터를 str형식으로 decode한다.

    return msg # 받은 데이터를 반환(전달)한다.

def binder(client_socket, address): # binder함수는 서버에서 accept가 되면 생성되는 socket 인스턴스를 통해 client로 부터 데이터를 받으면 echo형태로 재송신하는 메소드이다.

    print('Connected by', address) # 커넥션이 되면 접속 주소가 나온다.

    try:

        while True: # 접속 상태에서는 클라이언트로 부터 받을 데이터를 무한 대기한다.

            msg = recieveData() # 메세지를 클라이언트로부터 받아온다.

            if msg.strip() == '/파일목록': # 파일 목록 명령을 받았을 때

                client_socket.sendall(pickle.dumps(files)) # 파일 리스트 보냄

            if msg.split()[0] == '/업로드':

                client_socket.sendall(pickle.dumps(files)) # 파일 리스트 보냄 ( 중복 확인을 위해 ) #1

                directory = recieveData() # 파일 경로 받기

                filename = recieveData() # 파일 이름 받기

                extension = recieveData() # 파일 확장자명 받기

                if not exists(directory): # 파일 경로가 존재하지 않는다면

                    client_socket.sendall(b'-1') # 반환값은 -1

                    continue # 처음으로 돌아감.

                reSize = getFileSize(directory) # 파일 크기 얻음

                files[filename] = round(int(reSize) / 1024) # 파일 목록 ( dict ) 에 { 파일명 : 파일 크기 } 형태로 저장

                client_socket.sendall(reSize.encode()) # 파일 크기를 클라이언트로 전송

                # 파일 전송 부분 ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ

                file = open('C:\\Users\\DGSW\\Desktop\\Server\\' + filename, 'wb')

                while True:

                    image_chunk = client_socket.recv(1024)

                    if image_chunk[-5:] == b'break':

                        file.write(image_chunk[:-5])

                        print('Done Recieving.')

                        break
                    
                    file.write(image_chunk)

                file.close()



            if msg.split()[0] == '/다운로드':

                filename = recieveData() # 클라이언트로부터 파일명 수신

                extension = recieveData() # 클라이언트로부터 확장자명 수신

                directory = 'C:\\Users\\DGSW\\Desktop\\Server\\' + filename # 파일 경로

                if not exists(directory): # 해당 파일이 서버에 존재하지 않을 경우

                    client_socket.sendall(b'-1') # -1 송신

                    continue # 처음으로 돌아감.

                reSize = getFileSize(directory) # 파일 크기를 얻어옴

                client_socket.sendall(reSize.encode()) # 파일 크기를 클라이언트로 전송

                if extension == 'txt':

                    client_socket.sendall(getFileData(directory).encode())
                
                else:                    

                    file = open('D:\\download\\' + filename, 'wb')

                    while True:

                        image_chunk = client_socket.recv(1024)

                        if image_chunk[-5:] == b'break':

                            file.write(image_chunk[:-5])

                            print('Done Recieving.')

                            break
                        
                        file.write(image_chunk)

                    file.close()


            else:
            
                data = msg.encode() # 바이너리(byte)형식으로 변환한다.
                
                length = len(data) # 바이너리의 데이터 사이즈를 구한다.
                
                client_socket.sendall(length.to_bytes(4, byteorder = 'little')) # 데이터 사이즈를 little 엔디언 형식으로 byte로 변환한 다음 전송한다.
                
                client_socket.sendall(data) # 데이터를 클라이언트로 전송한다.

    except Exception as e: # 접속이 끊기면 except가 발생한다.
        
        print(e)
        print('except : ' + str(address[0]))

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
