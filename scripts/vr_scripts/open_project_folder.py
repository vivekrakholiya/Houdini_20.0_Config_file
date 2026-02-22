import os , hou
import subprocess

def open_caja(path):
    # Expand the user's home directory if ~ is used
    path = os.path.expanduser(path)

    # Ensure the path exists
    if os.path.exists(path):
        try:
            subprocess.run(['caja', path], check=True)
            print(f"Caja opened at: {path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to open Caja: {e}")
    else:
        print(f"Path does not exist: {path}")



directory_path = hou.hscriptExpression('$HIP')



open_caja(directory_path)
