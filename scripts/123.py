import os , random , sys
import hou


# this code is for change rando splash screen 

maxImageNum = 11

line_number = 27


def randomNum(maximageNum):
    return random.randint(1, maximageNum)


def getImagePath():
    current_folder = hou.homeHoudiniDirectory()
    
    imageFolderPath = current_folder + '/' 'startup_images' + '/' + 'images' + '/' 
    image_file_formate = '.png'
    cmd = 'HOUDINI_SPLASH_FILE = '
    imageFilePath = cmd + imageFolderPath + str(randomNum(maxImageNum)) + image_file_formate 

    return imageFilePath




def envPath():
    current_folder = hou.homeHoudiniDirectory()
    imageFolderPath = current_folder +'/'+ "houdini.env"

    return imageFolderPath

def replace_line_in_file(file_path, line_number, new_line):
    
    lines = []
    with open(file_path, 'r') as f:
        for i, line in enumerate(f, 1):
            if i == line_number:
                lines.append(new_line + '\n')
            else:
                lines.append(line)

    with open(file_path, 'w') as f:
        f.writelines(lines)




replace_line_in_file(envPath(), line_number, getImagePath())





#################################################  the end of the code  ###############################################################

# Path to your custom XML file
