from FileSystem import FileSystem
import pickle
import os
import sys


def main():

    # check if there is already some data available
    if os.path.isfile('./fileSystem.dat'):
        with open('./fileSystem.dat', 'rb') as fs:
            fileSystem = pickle.load(fs)
    else:
        fileSystem = FileSystem()
    currFileString = ', currFile: ' + \
        fileSystem.currentFile[0].name + \
        ' mode: ' + \
        fileSystem.currentFile[1] if fileSystem.currentFile[0] is not None else ''
    try:
        userInput = input(
            f'{fileSystem.getPathToCurrentDir()} {currFileString}  $ ')
    except (EOFError, KeyboardInterrupt):
        quit()

    while(userInput != 'shutdown'):
        splittedText = userInput.split()
        command = splittedText[0]
        match command:
            case 'ls':
                fileSystem.listCurrentChildren()
            case 'cd':
                if len(splittedText) == 2:
                    fileSystem.changeDirectory(splittedText[1])
                else:
                    print('Usage: cd dest_name')
            case 'mkdir':
                print(fileSystem.createDir(splittedText[1]))
            case 'create':
                print(fileSystem.createFile(splittedText[1]))
            case 'delete':
                print(fileSystem.deleteNode(splittedText[1]))
            case 'open':
                print(fileSystem.openFile(
                    splittedText[1], splittedText[2] if 2 < len(splittedText) else 'r'))
            case 'close':
                print(fileSystem.close(splittedText[1]))
            case 'write_to_file':
                if splittedText[1].isdigit():
                    print(fileSystem.write_to_file(
                        int(splittedText[1]), splittedText[2:]))
                else:
                    print(fileSystem.write_to_file(
                        None, ' '.join(splittedText[1:])))
            case 'read_from_file':
                if len(splittedText) > 1:
                    print(fileSystem.read_from_file(
                        splittedText[1], splittedText[2]))
                else:
                    print(fileSystem.read_from_file())
            case 'move_within_file':
                if len(splittedText) < 4:
                    print('missing parameters re-enter the command')
                else:
                    print(fileSystem.move_within_file(
                        int(splittedText[1]), int(splittedText[2]), int(splittedText[3])))
            case 'truncate_file':
                print(fileSystem.trucate_file())
            case 'show_map':
                fileSystem.showMemoryMap()
            case 'move':
                if len(splittedText) == 3:
                    print(fileSystem.move(splittedText[1], splittedText[2]))
                else:
                    print('usage: move src dest')
            case other:
                print('command not recognized')
        currFileString = ', currFile: ' + \
            fileSystem.currentFile[0].name + \
            ' mode: ' + \
            fileSystem.currentFile[1] if fileSystem.currentFile[0] is not None else ''
        try:
            userInput = input(
                f'{fileSystem.getPathToCurrentDir()} {currFileString} $ ')
        except (EOFError, KeyboardInterrupt):
            print('\nClosing without saving...')
            exit()
    # Closing open files if any
    fileSystem.currentFile = (None, None)
    with open('./fileSystem.dat', 'wb') as fs:
        pickle.dump(fileSystem, fs)


if __name__ == '__main__':
    main()
