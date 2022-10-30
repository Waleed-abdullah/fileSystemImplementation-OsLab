from FileNode import FileNode

FILE = 'file'
DIR = 'dir'


class DirectoryNode:

    def __init__(self, name):
        self.name = name
        self.children = []
        self.parent = None

    def createFile(self, fileName):
        if self.checkIfNameExists(fileName):
            return "FileName already exists"
        self.children.append(
            {'nodeName': fileName, 'node': FileNode(fileName), 'nodeType': FILE})
        return "Added File"

    def createDirectory(self, dirName):
        if self.checkIfNameExists(dirName):
            return "Directory already exists"
        self.children.append(
            {'nodeName': dirName, 'node': DirectoryNode(dirName), 'nodeType': DIR})
        self.children[-1]['node'].parent = self
        return 'Added directory'

    def getNodeToBeDeleted(self, nodeName):
        for idx, child in enumerate(self.children):
            name = child['nodeName']
            if nodeName == name:
                return (child, idx)
        return -1

    def getFile(self, fileName):
        for node in self.children:
            if node['nodeName'] == fileName and node['nodeType'] == FILE:
                return node['node']
        return None

    def getDir(self, dirName):
        if dirName == '..':
            return self.parent
        for node in self.children:
            if node['nodeName'] == dirName and node['nodeType'] == DIR:
                return node['node']
        return None

    def checkIfNameExists(self, name):
        for node in self.children:
            if node['nodeName'] == name:
                return True
        return False
