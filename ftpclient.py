import socket
import os
import sys
HOST = "127.0.0.1"

usage = "Run the script: ./ftpserver.py PORT"

if len(sys.argv) != 2:
    print(usage)
    sys.exit(0)

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])


s = socket.socket()
s.connect((HOST, PORT))

cur_dir = s.recv(1024)
cur_dir = cur_dir.decode("utf-8")
while True:
    cmd = input(str("ftp@ ") + str(cur_dir) + " > ")
    s.send(str.encode(cmd))
    s_cmd = cmd.split(" ")
    cm = s_cmd[0]

    try:
        fname = s_cmd[1]
    except:
        fname = ""

    if cm == "ls":
        size = s.recv(2)
        # s.send(str.encode("ok"))
        print("number of files: ", size.decode("utf-8"))

        for i in range(int(size)):
            # print(i)
            data = s.recv(1024)
            s.send(str.encode("ok"))
            if not data:
                break
            data = data.decode("utf-8")
            print(data)

    if cm == "cwd":
        r = s.recv(1024)
        print(r.decode("utf-8"))

    if cm == "cd":
        r = s.recv(1024)
        r = r.decode("utf-8")
        cur_dir = r
        print(r)

    if cm == "mkdir":
        r = s.recv(1024)
        print(r.decode("utf-8"))

    if cm == "lcd":
        try:
            os.chdir(fname)
            print(os.getcwd())
        except:
            print(os.getcwd())

    if cm == "get":
        if fname == ".":
            s.send(str.encode("$all_$"))
            n = s.recv(10)
            ssize = s.recv(20)
            s.send(str.encode("ok"))
            for i in range(int(ssize)):
                fff_name = s.recv(100)
                fff_name = fff_name.decode("utf-8")
                s.send(str.encode("ok"))
                with open('new_from_serv_'+fff_name, 'wb') as f:
                    data = s.recv(1024)
                    while True:
                        f.write(data)
                        s.send(str.encode("ok"))
                        data = s.recv(1024)
                        if data.decode("utf-8") == "$end$":
                            print(data.decode("utf-8"))
                            break
        else:
            s.send(str.encode("$one_$"))
            n = s.recv(10)
            should_try = s.recv(20)
            if should_try.decode("utf-8") == "$present$":
                s.send(str.encode("ok"))
                with open('new_'+fname, 'wb') as f:
                    data = s.recv(1024)
                    while True:
                        f.write(data)
                        s.send(str.encode("ok"))
                        data = s.recv(1024)
                        if data.decode("utf-8") == "$end$":
                            print(data.decode("utf-8"))
                            break
            else:
                print(should_try.decode("utf-8"))

    if cm == "put":
        if fname == ".":
            s.send(str.encode("$all$"))
            n = s.recv(10)
            path = os.getcwd()
            all_files = [f for f in os.listdir(path)
                         if os.path.isfile(os.path.join(path, f))]

            ssize = len(all_files)
            s.send(str.encode(str(ssize)))
            n = s.recv(10)
            for a_file in all_files:
                s.send(str.encode(str(a_file)))
                n = s.recv(10)
                with open(str(a_file), "rb") as f:
                    l = f.read(1024)
                    while (l):
                        s.send(l)
                        n = s.recv(10)
                        print('Sent ', repr(n))
                        l = f.read(1024)
                    s.send(str.encode("$end$"))
        else:
            if fname == "":
                print("provide a filename")
            else:
                s.send(str.encode("$one$"))
                cur_path = os.getcwd()
                if os.path.exists(fname):
                    with open(fname, "rb") as f:
                        l = f.read(1024)
                        while (l):
                            s.send(l)
                            n = s.recv(10)
                            print('Sent ', repr(n))
                            l = f.read(1024)
                        s.send(str.encode("$end$"))
                else:
                    print("No Such file ", fname)

    if cm == "bye":
        break
