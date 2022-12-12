from DirectoryNode import DirectoryNode
import math
TOTAL_MEM = 2**10
BLOCK_SIZE = 20
TOTAL_BLOCKS = TOTAL_MEM // BLOCK_SIZE


class FileSystem:

    def __init__(self):
        self.root = DirectoryNode('root')
        self.currentDir = self.root
        self.blocks = [{'usedSize': 0, 'data': ''}
                       for _ in range(TOTAL_BLOCKS)]
        # 1 means the block is occupied and 0 means that it is free
        self.freeBlocks = [0] * TOTAL_BLOCKS
        self.numFreeBlocks = TOTAL_BLOCKS
        # idx 0 indicates fileNode, idx 1 indicates the mode
        self.currentFile = (None, None)

    def createDir(self, newDirName):
        return self.currentDir.createDirectory(newDirName)

    def openFile(self, fileName, mode):
        self.currentFile = (self.currentDir.getFile(fileName), mode)
        if self.currentFile[0] == None:
            self.currentFile = (None, None)
            return "File does not exist"
        else:
            return "File opened"

    def close(self, fileName):
        if self.currentFile[0].name == fileName:
            self.currentFile = (None, None)
            return "Closed File"
        else:
            return 'This file is not open'

    def write_to_file(self, writeAt, text):
        if len(text) == 0:
            return "Empty text"
        fileNode, mode = self.currentFile[0], self.currentFile[1]
        if fileNode is None:
            return "No file"
        if mode == 'r':
            return "File is in read mode"
        '''So now we need to figure out how to allocate blocks
        ceil(len(text) / BLOCK_SIZE) will give us required blocks 
        if it is in w mode then it is easy just start writing in each block
        Each block can have a node (dictionary)
        {usedSize: xx, data: ---}
        if it is in append mode then
        we get the last used block from the fileNode and see if it has some more room then we can get that amount of bytes into the block
        '''

        blocksRequired = math.ceil(len(text)) // BLOCK_SIZE
        if blocksRequired > self.numFreeBlocks:
            return "Not enough blocks available for data"

        if writeAt is None:
            if mode == 'w' or mode == "rw":
                # We need to overwrite the blocks if already allocated
                # new blocks will be assigned previous will be deallocated
                self.deallocateBlocksFromFile(fileNode)
                self.allocate_and_fill_Blocks(fileNode, text)
            elif mode == 'a':
                self.appendToFile(fileNode, text)

        else:  # writeAt is provided
            '''we have to write at a specific block
            we must fill that block first and then
            if there are more blocks in the file then continue writing in those blocks
            For example if writeAt is 20 then we must find in which block byte 20 lies, we can do that by simply performing division and to find the location in that block we can use the modulo operator
            '''
            blockNumber = writeAt // BLOCK_SIZE
            loc_in_block = writeAt % BLOCK_SIZE
            if blockNumber >= len(fileNode.dataPointers):
                self.appendToFile(fileNode, text)
            else:
                data = self.read_from_file()
                newData = data[:writeAt] + text + data[writeAt:]
                for blockIdx in len(fileNode.dataPointers):
                    block = self.blocks[blockIdx]
                    block['usedSize'] = min(len(newData), BLOCK_SIZE)
                    block['data'] = newData[:BLOCK_SIZE]
                    newData = newData[BLOCK_SIZE:]
                if len(newData):
                    self.allocate_and_fill_Blocks(fileNode, newData)
        return 'successfuly written'

    def allocate_and_fill_Blocks(self, fileNode, text):

        for blockIdx, blockStatus in enumerate(self.freeBlocks):
            if len(text) == 0:
                break
            if blockStatus == 1:
                continue
            block = self.blocks[blockIdx]
            block['usedSize'] = min(len(text), BLOCK_SIZE)
            block['data'] = text[:BLOCK_SIZE]
            text = text[BLOCK_SIZE:]
            self.freeBlocks[blockIdx] = 1
            self.numFreeBlocks -= 1
            fileNode.dataPointers.append(blockIdx)
            if len(text) == 0:
                break

    def appendToFile(self, fileNode, text):
        if len(fileNode.dataPointers) > 0:
            lastUsedBlock = self.blocks[fileNode.dataPointers[-1]]
            freeSpace = BLOCK_SIZE - lastUsedBlock['usedSize']
            lastUsedBlock['usedSize'] = min(
                len(text) + lastUsedBlock['usedSize'], BLOCK_SIZE)
            lastUsedBlock['data'] += text[:freeSpace]
            text = text[freeSpace:]

        self.allocate_and_fill_Blocks(fileNode, text)

    def read_from_file(self, start=0, size=float('inf')):
        fileNode, mode = self.currentFile[0], self.currentFile[1]
        if fileNode is None:
            return "No file"
        if mode == 'w' or mode == 'a':
            return "File is not in read mode"

        totalBytesInFile = len(fileNode.dataPointers) * BLOCK_SIZE
        startBlock = start // BLOCK_SIZE
        if startBlock >= len(fileNode.dataPointers):
            return '**starting location outside file**'
        readData = ''
        if size - start >= totalBytesInFile:
            for i in range(startBlock, len(fileNode.dataPointers)):
                blockIdx = fileNode.dataPointers[i]
                block = self.blocks[blockIdx]
                readData += block['data']

        if size - start < totalBytesInFile:
            remainingSize = size
            for i in range(startBlock, len(fileNode.dataPointers)):
                if remainingSize <= 0:
                    break
                blockIdx = fileNode.dataPointers[i]
                block = self.blocks[blockIdx]
                readData += block['data'][: min(remainingSize,
                                                block['usedSize'])]
                remainingSize -= block['usedSize']
        return readData

    def createFile(self, name):
        return self.currentDir.createFile(name)

    def showMemoryMap(self):
        self.showMemoryMapHelper(self.root)

    def showMemoryMapHelper(self, currentNode, level=0):
        childNodes = []
        if type(currentNode) != type({}):
            print(" " * level, currentNode.name)
            childNodes = currentNode.children
        else:
            blockMapping = str(
                currentNode['node'].dataPointers) if currentNode['nodeType'] == 'file' else ''
            print(" " * level,
                  currentNode['nodeType'] + '->' + currentNode['nodeName'] + blockMapping)

            if currentNode['nodeType'] == 'dir':
                childNodes = currentNode['node'].children

        for childNode in childNodes:
            self.showMemoryMapHelper(childNode, level + 1)

    def deleteNode(self, name):
        childNode, idxInChildNodes = self.currentDir.getNodeToBeDeleted(name)
        if childNode == -1:
            return 'Node not found in current dir'

        currentNode = childNode['node']
        # if the current node is a file node we must deallocate its blocks
        if childNode['nodeType'] == 'file':
            self.deallocateBlocksFromFile(currentNode)

        self.currentDir.children.pop(idxInChildNodes)
        return 'Deleted node'

    def deallocateBlocksFromFile(self, fileNode):
        previousBlockPointers = fileNode.dataPointers
        fileNode.dataPointers = []  # new blocks will be assigned previous will be deallocated
        for blockIdx in previousBlockPointers:
            block = self.blocks[blockIdx]
            block['usedSize'] = 0
            block['data'] = ''
            self.freeBlocks[blockIdx] = 0
            self.numFreeBlocks += 1
        return 'DeAllocated blocks'

    def changeDirectory(self, name):
        newDir = self.currentDir.getDir(name)
        self.currentDir = newDir if newDir is not None else self.currentDir
        return 'Dir doesnt exist' if newDir is None else self.currentDir.name

    def move(self, source_name, dest_name):
        if source_name == 'root':
            return 'Cannot Move root node'
        currentDirChildren = self.currentDir.children

        sourceNode = None
        sourceNodeIdx = None
        for nodeIdx, holderNode in enumerate(currentDirChildren):
            if holderNode['nodeName'] == source_name:
                sourceNode = holderNode
                sourceNodeIdx = nodeIdx
        if sourceNode is None:
            return 'file doesnt exist in current directory'

        if self.currentDir != self.root and dest_name == self.currentDir.parent.name:
            self.currentDir.parent.children.append(sourceNode)
            self.currentDir.children.pop(sourceNodeIdx)
            return 'Moved'

        directories = self.getDirNodes()
        if dest_name not in directories:
            return 'Destination does not exist'

        destinationNode = directories[dest_name]
        if not destinationNode.checkIfNameExists(source_name):
            destinationNode.children.append(sourceNode)
            if sourceNode['nodeType'] == 'dir':
                sourceNode['node'].parent = destinationNode
            currentDirChildren.pop(sourceNodeIdx)
        else:
            return 'A file with the same name already exists in destination'
        return 'Moved'

    def getDirNodes(self):
        currentNode = self.root
        nodes = {}
        queue = [currentNode]
        while len(queue):
            currentNode = queue.pop(0)
            childNodes = currentNode.children
            for holderNode in childNodes:
                if holderNode['nodeType'] == 'dir':
                    queue.append(holderNode['node'])
            nodes[currentNode.name] = currentNode
        return nodes

    def move_within_file(self, start, size, target):
        data = self.read_from_file()
        dataToMove = data[start:size]
        newData = data[:start] + data[start + size: target] + \
            dataToMove + data[target:]
        fileNode, prevMode = self.currentFile
        self.currentFile = (fileNode, 'w')
        self.write_to_file(newData)
        self.currentFile = (fileNode, prevMode)
        return 'Moved Data'

    def trucate_file(self):
        fileNode, mode = self.currentFile
        if fileNode is None:
            return 'No opened file'
        if mode == 'r':
            return 'cannot truncate in read mode'
        # de allocate all blocks and their data
        self.deallocateBlocksFromFile(fileNode)
        return 'truncated File'

    def getPathToCurrentDir(self):
        path = []
        tempDir = self.currentDir
        while tempDir is not None:
            path.append(tempDir.name)
            tempDir = tempDir.parent
        path.reverse()
        return '/'.join(path)

    def listCurrentChildren(self):
        for children in self.currentDir.children:
            nodeType, nodeName = children['nodeType'], children['nodeName']
            print(f'Type: {nodeType}, name: {nodeName}')

    # for absolute path implementation
    def getNodeFromPath(self):
        pass
