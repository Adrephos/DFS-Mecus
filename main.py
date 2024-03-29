import os

def split_file(path: str, chunck_size:int):
    fileR = open(path, "rb")
    chunck = 0
    byte = fileR.read(chunck_size)

    try:
        os.mkdir("./chuncks")
    except:
        print("./chuncks/ already exists")

    while byte:
        fileN = path.split("/")[-1] + ".chunk" + str(chunck)
        fileT = open("./chuncks/" + fileN, "wb")
        fileT.write(byte)
        fileT.close

        byte = fileR.read(chunck_size)

        chunck += 1

img = input("File path (from root): ")
split_file(img, 1400*1024)
