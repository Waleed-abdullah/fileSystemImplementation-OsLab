class FileNode:
    def __init__(self, name):
        self.name = name
        self.dataPointers = []  # holds indices to the data blocks assigned to the file
