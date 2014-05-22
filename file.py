import os


class File:
    def __init__(self, path, file):
        self.path = os.path.join(path, file).encode('utf-8', errors='surrogateescape')
        self.name, self.extension = os.path.splitext(file)

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return self.path == other.path

    def __str__(self):
        return self.path.decode('utf-8')

    def __repr__(self):
        return self.path.decode('utf-8') +'('+str(self.inode)+')'


class FileInode(File):
    def __init__(self, path, file):
        super().__init__(path, file)
        self.inode = os.stat(self.path).st_ino

    def __hash__(self):
        return self.inode

    def __eq__(self, other):
        return self.inode == other.inode


def files_in_directory(dir, stat = None):
    all = []
    for path, folders, files in os.walk(dir):
        all.extend([File(path, file) for file in files])
    return set(all)


def make_hardlink(source, destination):
    os.link(source, destination)

