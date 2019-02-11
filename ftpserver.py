import os
import socket
import sys
from threading import Thread

HOST = "127.0.0.1"

usage = "Run the script: ./ftpserver.py PORT"

if len(sys.argv) != 2:
    print(usage)
    sys.exit(0)

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])


def create_socket():
    try:
        global HOST
        global PORT
        global sd
        sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("Socket creation error ", str(e))


def bind_socket():
    try:
        global HOST
        global PORT
        global sd

        sd.bind((HOST, PORT))
        sd.listen(5)
        print("Socket binded to port", PORT, "listeninig")
    except socket.error as e:
        print("Error in binding socket ", str(e), "\nRetrying...")
        bind_socket()


def socket_accept():
    while True:
        conn, address = sd.accept()
        print("Connection established: Ip: ", address[0], ":", address[1])
        try:
            Thread(target=send_data, args=(conn, address)).start()
        except:
            print("error in creating thread")


def handleLs(conn):
    datas = os.listdir()
    datas = [i+str("\n") for i in datas]
    # print(datas)
    size = str(len(datas))
    conn.send(str.encode(size))
    #l = conn.recv(10)
    # print(l.decode("utf-8"))
    for d in datas:
        d = str(d)
        #print("Sending file ", d)
        conn.send(str.encode(d))
        l = conn.recv(10)
        # print(l.decode("utf-8"))


def handleCwd(conn):
    res = os.getcwd()
    conn.send(str.encode(str(res)))


def handleCd(conn, path):
    if not os.path.exists(path):
        data = "No such directory"
        conn.send(str.encode(data))
    else:
        os.chdir(path)
        res = os.getcwd()
        conn.send(str.encode(str(res)))


def handleMkdir(conn, path):
    if not os.path.exists(path):
        os.makedirs(path)
        data = "Directory created successful"
    else:
        data = "Directory alredy exists"
    conn.send(str.encode(data))


def handleGet(conn, filename):
    how_many = conn.recv(20)
    conn.send(str.encode("ok"))
    if how_many.decode("utf-8") == "$all_$":
        path = os.getcwd()
        all_files = [f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))]
        ssize = len(all_files)
        conn.send(str.encode(str(ssize)))
        n = conn.recv(10)
        for a_file in all_files:
            conn.send(str.encode(str(a_file)))
            n = conn.recv(10)
            with open(str(a_file), "rb") as f:
                l = f.read(1024)
                while (l):
                    conn.send(l)
                    n = conn.recv(10)
                    #print('Sent ', repr(n))
                    l = f.read(1024)
                conn.send(str.encode("$end$"))
    else:
        cur_path = os.getcwd()
        if os.path.exists(filename):
            conn.send(str.encode("$present$"))
            istry = conn.recv(20)
            if istry.decode("utf-8") == "ok":
                with open(filename, "rb") as f:
                    f = open(filename, 'rb')
                    l = f.read(1024)
                    while (l):
                        conn.send(l)
                        n = conn.recv(10)
                        print('Sent ', repr(n))
                        l = f.read(1024)
                    # conn.shutdown(socket.SHUT_WR)
                    conn.send(str.encode("$end$"))
                    f.close()
        else:
            conn.send(str.encode("No such file"))


def handlePut(conn, filename):
    how_many = conn.recv(20)
    conn.send(str.encode("ok"))
    if how_many.decode("utf-8") == "$all$":
        ssize = conn.recv(20)
        conn.send(str.encode("ok"))
        for i in range(int(ssize)):
            fff_name = conn.recv(100)
            fff_name = fff_name.decode("utf-8")
            conn.send(str.encode("ok"))
            with open('new_from_cli_'+fff_name, 'wb') as f:
                data = conn.recv(1024)
                while True:
                    f.write(data)
                    conn.send(str.encode("ok"))
                    data = conn.recv(1024)
                    if data.decode("utf-8") == "$end$":
                        print(data.decode("utf-8"))
                        break
    else:
        with open('new_from_cli_'+filename, 'wb') as f:
            data = conn.recv(1024)
            while True:
                f.write(data)
                conn.send(str.encode("ok"))
                data = conn.recv(1024)
                if data.decode("utf-8") == "$end$":
                    print(data.decode("utf-8"))
                    break


def send_data(conn, a):
    send_dir = os.getcwd()
    conn.send(str.encode(str(send_dir)))
    while True:
        data = conn.recv(1024)
        data = data.decode("utf-8")
        r_cmd = data.split(" ")
        cmd = r_cmd[0]
        try:
            filename = r_cmd[1]
        except:
            pass
        if(cmd == "ls"):
            handleLs(conn)
        elif(cmd == "get"):
            handleGet(conn, filename)
        elif(cmd == "put"):
            handlePut(conn, filename)
        elif(cmd == "cwd"):
            handleCwd(conn)
        elif(cmd == "cd"):
            path = filename
            handleCd(conn, path)
        elif(cmd == "mkdir"):
            path = filename
            handleMkdir(conn, path)
        else:
            d = "NO such command, use get, put, cwd, cd, ls or lcd command"


def main():
    create_socket()
    bind_socket()
    socket_accept()


main()
