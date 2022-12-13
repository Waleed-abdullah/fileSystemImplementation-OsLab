from FileSystem import FileSystem
import pickle
import os
import sys
import threading
import concurrent.futures


def thread_function(threadNum, fileSystem, commands, outputAtThread):
    for userCommand in commands:
        currFileString = ', currFile: ' + \
            fileSystem.currentFile[0].name + \
            ' mode: ' + \
            fileSystem.currentFile[1] if fileSystem.currentFile[0] is not None else ''
        prompt = f'{fileSystem.getPathToCurrentDir()} {currFileString} $ ' + \
            userCommand
        outputAtThread.append(prompt)
        splittedText = userCommand.split()
        command = splittedText[0]
        match command:
            case 'ls':
                outputAtThread.append(fileSystem.listCurrentChildren())
            case 'cd':
                if len(splittedText) == 2:
                    outputAtThread.append(
                        fileSystem.changeDirectory(splittedText[1], threadNum))
                else:
                    outputAtThread.append('Usage: cd dest_name')
            case 'mkdir':
                outputAtThread.append(
                    fileSystem.createDir(splittedText[1], threadNum))
            case 'create':
                outputAtThread.append(
                    fileSystem.createFile(splittedText[1], threadNum))
            case 'delete':
                outputAtThread.append(
                    fileSystem.deleteNode(splittedText[1], threadNum))
            case 'open':
                outputAtThread.append(fileSystem.openFile(
                    splittedText[1], splittedText[2] if 2 < len(splittedText) else 'r', threadNum))
            case 'close':
                outputAtThread.append(
                    fileSystem.closeFile(splittedText[1], threadNum))
            case 'write_to_file':
                if splittedText[1].isdigit():
                    outputAtThread.append(fileSystem.write_to_file(
                        int(splittedText[1]), ' '.join(splittedText[2:]), threadNum))
                else:
                    outputAtThread.append(fileSystem.write_to_file(
                        None, ' '.join(splittedText[1:]), threadNum))
            case 'read_from_file':
                if len(splittedText) > 1:
                    outputAtThread.append(fileSystem.read_from_file(
                        splittedText[1], splittedText[2] if len(splittedText) == 3 else float('inf'), threadNum))
                else:
                    outputAtThread.append(
                        fileSystem.read_from_file(thread=threadNum))
            case 'move_within_file':
                if len(splittedText) < 4:
                    outputAtThread.append(
                        'missing parameters re-enter the command')
                else:
                    outputAtThread.append(fileSystem.move_within_file(
                        int(splittedText[1]), int(splittedText[2]), int(splittedText[3]), threadNum))
            case 'truncate_file':
                outputAtThread.append(fileSystem.trucate_file(threadNum))
            case 'show_map':
                outputAtThread.append(fileSystem.showMemoryMap())
            case 'move':
                if len(splittedText) == 3:
                    outputAtThread.append(fileSystem.move(
                        splittedText[1], splittedText[2], threadNum))
                else:
                    outputAtThread.append('usage: move src dest')
            case other:
                outputAtThread.append('command not recognized')


def main():
    # open file system
    # check if there is already some data available
    if os.path.isfile('./fileSystem.dat'):
        with open('./fileSystem.dat', 'rb') as fs:
            fileSystem = pickle.load(fs)
    else:
        fileSystem = FileSystem()

    # handle threads
    numThreads = int(sys.argv[1])

    # create a different directory and file pointer for each thread
    fileSystem.currentDir = [fileSystem.root] * numThreads
    fileSystem.currentFile = [(None, None) for _ in range(numThreads)]

    # create lists to store the input commands and the output of executing each thread
    inputCommandsAtThread = [] * numThreads
    outputAtThread = [[] for _ in range(numThreads)]

    for threadNum in range(numThreads):
        threadFileName = f'input_thread{threadNum}.txt'
        with open(threadFileName, 'r') as threadFile:
            inputCommandsAtThread[threadNum] = threadFile.readlines()

    with concurrent.futures.ThreadPoolExecutor(max_workers=numThreads) as executor:
        for threadNum in range(numThreads):
            executor.submit(thread_function, threadNum, fileSystem,
                            inputCommandsAtThread[threadNum], outputAtThread[threadNum])

    for threadNum in range(numThreads):
        outputThreadFileName = f'output_thread{threadNum}.txt'
        with open(outputThreadFileName, 'w') as threadFile:
            for line in outputAtThread[threadNum]:
                threadFile.write(line + '\n')

    # dump the file system
    fileSystem.currentDir = [fileSystem.root]
    fileSystem.currentFile = [(None, None)]
    with open('./fileSystem.dat', 'wb') as fs:
        pickle.dump(fileSystem, fs)


if __name__ == '__main__':
    main()
