class DirectoryNode:
    def __init__(self, name: str, parent):
        self.name = name
        if parent is None:
            self.parent = self
        self.parent = parent
        self.files = {}
        self.subdirs = {}


class FilesTree:
    def __init__(self, root: DirectoryNode):
        self.root = root
        self.curr_dir = self.root

    def add_dir(self, path: str):
        in_dir = self.curr_dir
        if path[0] == '/':
            in_dir = self.root
        dirs = path.strip('/').split('/')

        for i, dir in enumerate(dirs):
            if dir in in_dir.subdirs and i == len(dirs)-1:
                return "Directory exists\n", self.full_path(in_dir)
            if dir == '.':
                continue
            elif dir == '..':
                in_dir = in_dir.parent
            elif dir in in_dir.subdirs:
                in_dir = in_dir.subdirs[dir]
            elif i == len(dirs)-1:
                in_dir.subdirs[dir] = DirectoryNode(dir, in_dir)
                return "", self.full_path(in_dir.subdirs[dir])
            else:
                break
        return "No such a file or directory\n", self.full_path(in_dir)

    def get_dir(self, path: str) -> tuple[DirectoryNode, bool]:
        in_dir = self.curr_dir
        if path[0] == '/':
            in_dir = self.root
        dirs = path.strip('/').split('/')

        for dir in dirs:
            if dir == '.':
                continue
            elif dir == '..':
                in_dir = in_dir.parent
            elif dir in in_dir.subdirs:
                in_dir = in_dir.subdirs[dir]
            else:
                return in_dir, False
        return in_dir, True

    def can_add_file(self, path: str):
        file_name = path.strip('/').split('/')[-1]
        path = "./" + '/'.join(path.strip('/').split('/')[:-1])

        in_dir, success = self.get_dir(path)

        file_full_path = self.full_path(in_dir).rstrip('/') + f'/{file_name}'
        if not success:
            return "No such a file or directory\n", in_dir, file_full_path

        if file_name in in_dir.files:
            return "File exists", in_dir, file_full_path
        return "", in_dir, file_full_path

    def add_file(self, path: str, chunks: dict, chunksReplicas: dict):
        file_name = path.strip('/').split('/')[-1]
        message, in_dir, file_full_path = self.can_add_file(path)

        if message != "":
            return message, file_full_path

        in_dir.files[file_name] = {
            'chunks': chunks,
            'chunksReplicas': chunksReplicas
        }
        return "", file_full_path

    def change_dir(self, path: str):
        in_dir, success = self.get_dir(path)
        new_dir_full_path = self.full_path(self.curr_dir)

        if path.strip('/') == "":
            self.curr_dir = self.root
            new_dir_full_path = self.full_path(self.curr_dir)
            return "", new_dir_full_path

        if not success:
            return "No such a file or directory\n", new_dir_full_path

        self.curr_dir = in_dir
        return "", new_dir_full_path

    def ls(self, path):
        if path == '':
            path = '.'
        in_dir, success = self.get_dir(path)

        if not success:
            return "No such a file or directory\n", list()

        file_list = [f'f: {x}' for x in list(in_dir.files.keys())]
        directory_list = [f'd: {x}' for x in list(in_dir.subdirs.keys())]

        return "", file_list + directory_list

    def full_path(self, dir: DirectoryNode):
        path = []
        while dir.name != '/':
            path.append(dir.name)
            dir = dir.parent
        path.reverse()

        return '/' + '/'.join(path)


def tree_to_map(root: DirectoryNode):
    tree_map = {}
    for file_name, file_info in root.files.items():
        # Add file data (chunks, node, replicaNode)
        tree_map[file_name] = file_info

    for subdir_name, subdir in root.subdirs.items():
        # Recursively convert subdirectories
        tree_map[subdir_name] = tree_to_map(subdir)

    return tree_map


def map_to_tree(map, name, parent):
    root = DirectoryNode(name, parent)  # Create the root DirectoryNode
    if parent is None:
        root.parent = root

    for name, value in map.items():
        if 'chunks' not in value.keys():
            # It's a subdirectory
            # Recursively create the subdirectory tree
            subdir = map_to_tree(value, name, root)
            root.subdirs[name] = subdir
        else:
            # It's a file
            root.files[name] = value  # Add file with metadata

    return root
