import os
import json
from tinydb import TinyDB
from tinydb.table import Document


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
                return "File exists\n", False
            if dir == '.':
                continue
            elif dir == '..':
                in_dir = in_dir.parent
            elif dir in in_dir.subdirs:
                in_dir = in_dir.subdirs[dir]
            elif i == len(dirs)-1:
                in_dir.subdirs[dir] = DirectoryNode(dir, in_dir)
                return "", True
            else:
                break
        return "No such a file or directory\n", False

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

    def add_file(self, path: str, chunks: dict, chunksReplicas: dict):
        file_name = path.strip('/').split('/')[-1]
        path = "./" + '/'.join(path.strip('/').split('/')[:-1])

        in_dir, success = self.get_dir(path)

        if not success:
            return "No such a file or directory\n", False

        in_dir.files[file_name] = {
            'chunks': chunks,
            'chunksReplicas': chunksReplicas
        }
        return "", True

    def change_dir(self, path: str):
        in_dir, success = self.get_dir(path)

        if path.strip('/') == "":
            self.curr_dir = self.root
            return "", True

        if not success:
            return "No such a file or directory\n", False

        self.curr_dir = in_dir
        return "", True

    def ls(self, path):
        if path == '':
            path = '.'
        in_dir, success = self.get_dir(path)

        if not success:
            return "No such a file or directory\n", list()

        file_list = [f'f: {x}' for x in list(in_dir.files.keys())]
        directory_list = [f'd: {x}' for x in list(in_dir.subdirs.keys())]

        return "", file_list + directory_list


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


"""
main() for testing, it will be deleted later
This functions will be executed from a cli client
"""


def main():
    db = TinyDB('db.json')
    root_db = db.table('tree')

    map = root_db.get(doc_id=1)
    if not map:
        root = DirectoryNode('/', None)
        root.parent = root
        root_db.insert(Document(tree_to_map(root), doc_id=1))
    else:
        root = map_to_tree(map, '/', None)

    file_tree = FilesTree(root)  # Create the initial file tree

    while True:
        # Display current path
        print(
            f"\u001b[35mCurrent Directory: \u001b[33m{file_tree.curr_dir.name}")
        command = input("\u001b[32m> \u001b[37m")

        args = command.split()
        if not args:
            continue  # Ignore empty commands

        if args[0] == 'mkdir':
            if len(args) != 2:
                print("Usage: add_dir <directory_path>")
            else:
                message, success = file_tree.add_dir(args[1])
                print(message, end="")

        elif args[0] == 'touch':
            if len(args) != 2:
                print("Usage: add_file <file_path> <chunks> <node> <replicaNode>")
            else:
                message, success = file_tree.add_file(
                    args[1],
                    {
                        "1": "127.0.0.5",
                        "2": "127.0.0.2",
                        "3": "127.0.0.7",
                        "4": "127.0.0.1",
                    }, {
                        "1": "127.0.0.5",
                        "2": "127.0.0.5",
                        "3": "127.0.0.7",
                        "4": "127.0.0.3",
                    }
                )
                print(message, end="")

        elif args[0] == 'cd':
            if len(args) != 2:
                print("Usage: cd <directory_path>")
            else:
                message, success = file_tree.change_dir(args[1])
                print(message, end="")

        elif args[0] == 'ls':
            if len(args) == 1:
                message, items = file_tree.ls("")
            elif len(args) >= 1:
                message, items = file_tree.ls(args[1])
            else:
                print("Usage: ls <directory_path>(optional)")
                continue
            if items:
                print("\n".join(items))
            elif message != "":
                print(message, end="")
            else:
                print("Directory is empty")

        elif args[0] == 'help':
            print("Available commands:")
            print("  add_dir <path>     - Create a directory")
            print("  add_file <path> <chunks> <node> <replicaNode> - Create a file")
            print("  cd <path>          - Change directory")
            print("  ls                 - List directory contents")
            print("  help               - Show this help")
            print("  exit               - Quit the program")

        elif args[0] == 'exit':
            break

        elif args[0] == 'clear':
            os.system('clear')
        else:
            print("Invalid command. Enter 'help' for a list of commands.")

        root_db.upsert(Document(tree_to_map(root), doc_id=1))


if __name__ == "__main__":
    main()
