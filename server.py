from FileSystem import FileSystem
import pickle
import os
import sys
from _thread import start_new_thread
import socket
from RWLock import RWLock

rwlock = RWLock()


def multi_client(connection, fileSystem, threadNum):
    connection.sendall(str.encode('Welcome client, enter your username:'))
    username = connection.recv(2048).decode()
    connection.sendall(str.encode('Welcome ' + username))
    while True:
        # send prompt
        currFileString = ', currFile: ' + \
            fileSystem.currentFile[threadNum][0].name + \
            ' mode: ' + \
            fileSystem.currentFile[threadNum][1] if fileSystem.currentFile[threadNum][0] is not None else ''
        prompt = f'{fileSystem.getPathToCurrentDir(threadNum)} {currFileString} $ '
        connection.sendall(str.encode(prompt))

        userCommand = connection.recv(2048).decode()
        if not userCommand or userCommand == 'exit':
            break

        splittedText = userCommand.split()
        command = splittedText[0]
        match command:
            case 'ls':
                connection.sendall(str.encode(
                    fileSystem.listCurrentChildren(threadNum)))
            case 'cd':
                if len(splittedText) == 2:
                    connection.sendall(str.encode(
                        fileSystem.changeDirectory(splittedText[1], threadNum)))
                else:
                    connection.sendall(str.encode('Usage: cd dest_name'))
            case 'mkdir':
                connection.sendall(str.encode(
                    fileSystem.createDir(splittedText[1], threadNum)))
            case 'create':
                connection.sendall(str.encode(
                    fileSystem.createFile(splittedText[1], threadNum)))
            case 'delete':
                connection.sendall(str.encode(
                    fileSystem.deleteNode(splittedText[1], threadNum)))
            case 'open':
                connection.sendall(str.encode(fileSystem.openFile(
                    splittedText[1], splittedText[2] if 2 < len(splittedText) else 'r', threadNum)))
            case 'close':
                connection.sendall(str.encode(
                    fileSystem.closeFile(splittedText[1], threadNum)))
            case 'write_to_file':
                rwlock.acquire_writelock()
                if splittedText[1].isdigit():
                    connection.sendall(str.encode(
                        fileSystem.write_to_file(
                            int(splittedText[1]), ' '.join(splittedText[2:]), threadNum
                        )
                    ))
                else:
                    connection.sendall(str.encode(
                        fileSystem.write_to_file(
                            None, ' '.join(splittedText[1:]), threadNum
                        )
                    ))
                rwlock.release_writelock()
            case 'read_from_file':
                rwlock.acquire_readlock()
                if len(splittedText) > 1:
                    connection.sendall(str.encode(
                        fileSystem.read_from_file(
                            splittedText[1], 
                            splittedText[2] if len(splittedText) == 3 else float('inf'),
                            threadNum
                        )
                    ))
                else:
                    connection.sendall(str.encode(
                        fileSystem.read_from_file(thread=threadNum)
                    ))
                rwlock.release_readlock()
            case 'move_within_file':
                if len(splittedText) < 4:
                    connection.sendall(str.encode(
                        'missing parameters re-enter the command'))
                else:
                    connection.sendall(str.encode(fileSystem.move_within_file(
                        int(splittedText[1]), int(splittedText[2]), int(splittedText[3]), threadNum)))
            case 'truncate_file':
                connection.sendall(str.encode(
                    fileSystem.trucate_file(threadNum)))
            case 'show_map':
                connection.sendall(str.encode(fileSystem.showMemoryMap()))
            case 'move':
                if len(splittedText) == 3:
                    connection.sendall(str.encode(fileSystem.move(
                        splittedText[1], splittedText[2], threadNum)))
                else:
                    connection.sendall(str.encode('usage: move src dest'))
            case other:
                connection.sendall(str.encode('command not recognized'))
    connection.close()
    dumpFileSystem(fileSystem, threadNum)
    global threadCount
    threadCount -= 1
    threadOccupancy[threadNum] = False


def openFileSystem():
    # open file system
    # check if there is already some data available
    if os.path.isfile('./fileSystem.dat'):
        with open('./fileSystem.dat', 'rb') as fs:
            fileSystem = pickle.load(fs)
    else:
        fileSystem = FileSystem()
    return fileSystem


def dumpFileSystem(fileSystem, threadNum):
    # dump the file system
    fileSystem.currentDir[threadNum] = fileSystem.root
    fileSystem.currentFile[threadNum] = (None, None)
    with open('./fileSystem.dat', 'wb') as fs:
        pickle.dump(fileSystem, fs)


def server():
    # get the fileSystem
    fileSystem = openFileSystem()
    # CLI argument to handle number of clients
    numThreads = int(sys.argv[1]) if len(sys.argv) > 1 else 4

    # create a different directory and file pointer for each thread
    fileSystem.currentDir = [fileSystem.root] * numThreads
    fileSystem.currentFile = [(None, None) for _ in range(numThreads)]

    serverSideSocket = socket.socket()
    host = '127.0.0.1'
    port = 95
    global threadCount
    global threadOccupancy
    # threadIdx is to check the occupancy of the ports False if free, True if occupied
    threadOccupancy = [False for _ in range(numThreads)]
    threadCount = 0
    try:
        serverSideSocket.bind((host, port))
    except socket.error as e:
        print(str(e))

    print('Server is Listening...')
    serverSideSocket.listen(numThreads)
    while True:
        try:
            client, address = serverSideSocket.accept()
        except KeyboardInterrupt:
            exit()
        if threadCount == numThreads:
            client.sendall(str.encode(
                'Connection ports are full try again after some time'))
            client.close()
            continue
        print('Connected to:' + address[0] + ':' + str(address[1]))
        clientIdx = threadOccupancy.index(False)
        threadOccupancy[clientIdx] = True
        start_new_thread(multi_client, (client, fileSystem,
                         clientIdx))
        threadCount += 1
        print('Thread Number:' + str(threadCount))
    serverSideSocket.close()


if __name__ == '__main__':
    server()
