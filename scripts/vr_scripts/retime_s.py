import os , hou

import shutil


selected_dir = hou.ui.selectFile(
    title="Select Directory",
    collapse_sequences=False,
    file_type=hou.fileType.Directory
)


if os.name == 'nt':
    a = str(selected_dir).replace('/','\\')

elif os.name == 'posix':
    a = selected_dir
    pass
    
    

if a:
     

    source_folder_path = str(a)

    new_file_name = (hou.ui.readInput("Enter new sequnce name", buttons=("OK", "Cancel"), initial_contents="new_sequnce")[1])

    # new extension
    #print("example : ---  enter = 1(exr) , 2 (png) , 3(jpg)  -----:   ")
    extansion = hou.ui.displayMessage("new file extansion", buttons=("exr", "png" , "jpg"))
    if extansion == 0:
        new_extension = ".exr"
    elif extansion== 1:
        new_extension = ".png"
    elif extansion== 2:
        new_extension = ".jpg"


    # new start frame


    new_start_frame = int((hou.ui.readInput("Enter sequnce start frame", buttons=("OK", "Cancel"), initial_contents='1001')[1]))

    # asking acreat folder or not

    create_folder = hou.ui.displayMessage("Do you want copy re-frame sequce in to separate folde", buttons=("No", "Yes"))


    if create_folder == 1:
        copyFile = 1
    else:
        copyFile = 0


    # find items in folder path
    sequnce_list = os.listdir(source_folder_path)




    # create folder re_frame folder if not extis
    if copyFile == 1:
        re_frame = source_folder_path + '\\' + 're_frame'
        if os.path.exists(re_frame):
            print('reframe folder alredy extist')
            totle_item = len(sequnce_list) -1
        else:
            os.mkdir(re_frame)
            print('re_frame folder created...')
            totle_item = len(sequnce_list)
    else:
        totle_item = len(sequnce_list)
        pass


    # copy items and rename it
    if copyFile == 1:
        for index, file in enumerate(sequnce_list):

            # print(file)


            sorce_file_path = str(source_folder_path + '\\' + file)

            destination_file_path = str(re_frame)
            



            if os.path.exists(str(destination_file_path + '\\' + file)):
                print('File Alredy Extis in re_frame Folder')
                print('frist move or delet files')

                break

            else:

                if index == (totle_item):
                    break
                else:
                    

                    shutil.copy(sorce_file_path,destination_file_path) 

                    # rename File

                    os.rename(str(destination_file_path + '\\' + file),str(destination_file_path + '\\' + new_file_name + "." + str(new_start_frame+index) +new_extension))




                    prograss = index / (totle_item) * 100
                    print(str(prograss) + '%...')
                    #print(str(destination_file_path + '\\' + "." + new_file_name + str(new_start_frame+index) +new_extension) +'copy and rename succfully')

    else:
        for index, file in enumerate(sequnce_list):

            # print(file)


            sorce_file_path = str(source_folder_path + '\\' + file)

            destination_file_path = str(source_folder_path)
            

            if index == (totle_item):
                break
            else:
                    

                # shutil.copy(sorce_file_path,destination_file_path) 

                # rename File

                os.rename(str(sorce_file_path),str(destination_file_path + '\\' + new_file_name + "." + str(new_start_frame+index) +new_extension))


                prograss = index / (totle_item) * 100
                print(str(prograss) + '%...')
                print(str(destination_file_path + '\\' + new_file_name + "." + str(new_start_frame+index) + new_extension) +'rename succfully')

else:
    pass





