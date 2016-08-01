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
        return self.path.decode('utf-8')


class FileInode(File):
    def __init__(self, base):
        self.path = base.path
        self.name = base.name
        self.extension = base.extension
        self.inode = os.stat(self.path).st_ino

    def __hash__(self):
        return self.inode

    def __eq__(self, other):
        return self.inode == other.inode

    def __str__(self):
        return super().__str__() +' ('+str(self.inode)+')'

    def __repr__(self):
        return super().__str__() +' ('+str(self.inode)+')'


def files_in_directory(dir, stat = None):
    all = []
    for path, folders, files in os.walk(dir):
        all.extend([File(path, file) for file in files])
    return set(all)


def difference_on_inode(base_set, different_set):
    return set([FileInode(f) for f in base_set]) - set([FileInode(f) for f in different_set])


def make_hardlink(source, destination):
    dir = os.path.dirname(destination)
    if not os.access(dir, os.F_OK):
        os.makedirs(dir)
    os.link(source, destination)

