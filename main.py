import os

def split_file(path: str, chunk_size: int):
    fileR = open(path, "rb")
    chunk = 0
    byte = fileR.read(chunk_size)

    try:
        os.mkdir("./chunks")
    except:
        print("./chunks/ already exists")

    while byte:
        fileN = path.split("/")[-1] + ".chunk" + str(chunk)
        fileT = open("./chunks/" + fileN, "wb")
        fileT.write(byte)
        fileT.close

        byte = fileR.read(chunk_size)

        chunk += 1


def rebuild_file(name: str):
    try:
        os.mkdir("./reconstruct")
    except:
        print("./reconstruct/ already exists")

    fileM = open("./reconstruct/" + name, "wb")
    chunk = 0

    fileName = "./chunks/" + name + ".chunk" + str(chunk)
    try:
        fileTemp = open(fileName, "rb")
    except:
        print("not a valid file to reconstruct")
        exit()
    while fileTemp:
        print(f'- chunk #{chunk} done')
        byte = fileTemp.read()
        fileM.write(byte)

        chunk += 1

        fileName = "./chunks/" + name + ".chunk" + str(chunk)
        try:
            fileTemp = open(fileName, "rb")
        except:
            break


print("Split file")
file = input("File path (from root): ")
split_file(file, 1400*1024)

print("\nRebuild file")
rebuild_file(file.split("/")[-1])
