from FileSystem import FileSystem
import pickle
import os
import sys
import threading


def thread_function(name):
    print("This is thread " + str(name))


def main():
    numThreads = sys.argv[1]
    print(numThreads)
    x = threading.Thread(target=thread_function, args=(1,))
    x.start()


if __name__ == '__main__':
    main()
