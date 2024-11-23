import socket
import threading
import os
import sys

def request_parser(request):
        #first line of the request breaks into 3 parts type(GET/POST/PUT ETC), path and http version
        request_splitlines = request.splitlines()
        req_type, req_path, req_httpver = request_splitlines[0].split(" ")[0], request_splitlines[0].split(" ")[1], request_splitlines[0].split(" ")[2]
        print(req_type, req_path, req_httpver)
        try:
            req_user_agent = request_splitlines[2].split(" ")[1]
        except:
             req_user_agent = None
             print("no user-agent provided")
        body = request_splitlines[-1]




        return req_type, req_path, req_httpver, req_user_agent, body



def construct_response(req_type, req_httpver, req_path, req_user_agent="unknown",body=None):
    suc_response = f"{req_httpver} 200 OK"
    fail_response = f"{req_httpver} 404 Not Found"

    match req_type:
         case "GET":

            match req_path.split("/")[1]:
                 
                 #ECHO
                case "echo":
                    content_type = "Content-Type: text/plain"
                    #content_length = f"Content-Length: {len(req_path.split("/")[2])}"
                    content = req_path.split("/")[2]
                    return f"{suc_response}\r\n{content_type}\r\nContent-Length: {len(content)}\r\n\r\n{content}"
                
                #USER AGENT
                case "user-agent":
                        content_type = "Content-Type: text/plain"
                        content = req_user_agent
                        return f"{suc_response}\r\n{content_type}\r\nContent-Length: {len(content)}\r\n\r\n{content}"
                 
                #FILES
                case "files":
                        if "--directory" in sys.argv:
                            try:
                                working_dir = sys.argv[sys.argv.index("--directory") + 1]
                            except:
                                print("--directory used with no input")

                        content_type = "Content-Type: application/octet-stream"
                        file_path = f"{working_dir}{"/".join(req_path.split("/")[2:])}"
                        print(file_path)
                        try:
                            
                            with open(file_path) as file:
                                content = file.read()
                        except:
                            print("file not found")
                            return f"{fail_response}\r\n\r\n"
                        
                        return f"{suc_response}\r\n{content_type}\r\nContent-Length: {os.path.getsize(file_path)}\r\n\r\n{content}"
         case "POST":
            suc_response = f"{req_httpver} 201 Created"
            
            match req_path.split("/")[1]:
                 
                 case "files":
                      try:
                           working_dir = sys.argv[sys.argv.index("--directory") + 1]
                      except:
                           print("--directory used with no input")
                        
                      file_path = f"{working_dir}{"/".join(req_path.split("/")[2:])}"
                      with open(file_path, 'w') as file:
                           file.write(body)
                      return f"{suc_response}\r\n\r\n"

                



    response_code, comment = ("404","Not Found") if req_path != "/" else ("200","OK")
    print(f"{req_httpver} {response_code}")
    return f"{req_httpver} {response_code} {comment}\r\n\r\n"


def new_connection(client, addr):

     while True:
          
          request = client.recv(1024).decode()
          req_type, req_path, req_httpver, req_user_agent,body = request_parser(request)
          print(f"encoded response: {construct_response(req_type,req_httpver,req_path,req_user_agent,body).encode()}")
          client.send(construct_response(req_type,req_httpver,req_path,req_user_agent,body).encode())
     client.close()
     

def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 4221))
    server_socket.settimeout(5)
    server_socket.listen(5)

    while True:
        client, addr = server_socket.accept() # wait for client
        print(f"Connection from client: {client}, Source address: {addr}")
        threading.Thread(target=new_connection, args=(client,addr)).start()

        

if __name__ == "__main__":
    main()
