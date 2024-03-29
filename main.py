import os

def split_file(path: str, chunk_size:int):
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

img = input("File path (from root): ")
split_file(img, 1400*1024)
