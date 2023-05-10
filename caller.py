from filemanager import create_Folder
import pathlib
import os


p = pathlib.Path(__file__).parent
os.chdir(p)
path = os.getcwd()

if __name__ == "__main__":
    name = input("digite el nombre del cliente ")
    create_Folder(name, path)
