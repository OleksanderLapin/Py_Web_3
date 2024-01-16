from pathlib import Path
import sys
import shutil
import os
from time import time
from multiprocessing import Process, current_process

# Folders and there extensions
dir_suff_dict = {
"Images": ['JPEG', 'PNG', 'JPG', 'SVG'],
"Documents": ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
"Archives": ['ZIP', 'GZ', 'TAR'],
"Audio": ['MP3', 'OGG', 'WAV', 'AMR'],
"Video": ['AVI', 'MP4', 'MOV', 'MKV'],
"Unknown": ['Unknown ext']
}
# All extensions from dir_suff_dist
all_ext = ['JPEG', 'PNG', 'JPG', 'SVG', 'DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX', 'ZIP', 'GZ', 'TAR', 'MP3', 'OGG', 'WAV', 'AMR', 'AVI', 'MP4', 'MOV', 'MKV']

# Path to sorted folder
a = Path(sys.argv[1])

# Creating directories if not exists
for k in dir_suff_dict:
    if not os.path.exists(f'{a}/{k}'):
        os.mkdir(f'{a}/{k}')

unknown_ext = []
known_ext = []
all_files = {
    "Archives" : [],
    "Audio" : [],
    "Documents" : [],
    "Images" : [],
    "Video" : [],
    "Unknown" : []
}

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯЄІЇҐ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g", 'A', 'B', 'V', 'G', 'D', 'E', 'E', 'J', 'Z', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'F', 'H', 'TS', 'CH', 
'SH', 'SCH', '', 'Y', '', 'E', 'YU', 'YA', 'JE', 'I', 'JI', 'G')

TRANS = {ord(i): TRANSLATION[b] for b, i in enumerate(CYRILLIC_SYMBOLS)}
# Translate all cyrillic symbols to latin and all unknown symbol to '_' 
def normalize(file_name):
    b = file_name.translate(TRANS)
    return ''.join(
        (
            _
            if (ord(_) >= 97 and ord(_) <= 122) # a-z
            or (ord(_) >= 65 and ord(_) <= 90)  # A-Z
            or (ord(_) >= 48 and ord(_) <= 57)  # 0-9
            else '_'
        )
        for _ in b
    )

# Remove empty folders
def removeEmptyFolders(path): 
    files = os.listdir(path)                                                             
    if len(files):                                                                      # Check if list is not empty
        for f in files:                                                                 # Iterate over all the files
            full_path = os.path.join(path, f)                                           # Get full path of the file
            if os.path.isdir(full_path): 
                removeEmptyFolders(full_path)                                           # Recurse function
    files = os.listdir(path)  
    if len(files) == 0 and os.path.split(path)[1] not in dir_suff_dict.keys():          # If list is empty then delete that folder 
        # print("Removing empty folder:", path)                                         # If needed to knew deleted folders
        os.rmdir(path)    


# Main funk sorting folder
def sort_folder(path):
    for i in path.iterdir():
        if i.is_file() and os.path.split(i)[1] not in dir_suff_dict.keys():             # If file and not in skipped folders
            (file_name, ext) = os.path.splitext(i)                                      # Split to know the ext of file
            for key, val in dir_suff_dict.items():                                      # Sorting according to ext
                if ext.upper().removeprefix('.') in val:
                    norm_file_name = normalize(os.path.split(file_name)[1])                     # Normalize just the name of file, not all path to it
                    c = Path(os.path.join(os.path.split(file_name)[0], norm_file_name + ext))   # Create a new path to renamed file
                    os.rename(i, c)
                    if ext.lower() not in known_ext:                                    # Adding to list of ext the scrypt know
                        known_ext.append(ext.lower())
                    if key == "Archives":                                               # To unpack archive 
                        for g, val in all_files.items():                                # 
                            if g == key:
                                val.append(norm_file_name)                              # To add file to current list
                        shutil.unpack_archive(c, os.path.join(a, key, norm_file_name))  # Unpack, rename archive
                        os.remove(c)                                                    # Remove archive
                    else:                                                               # For all other files 
                        try:                                                            # Check if file_name exists in needed folder
                            for g, val in all_files.items():
                                if g == key:
                                    val.append(norm_file_name + ext)
                            shutil.move(c, os.path.join(a, key))                        # Move file to needed folder, according to ext
                        except shutil.Error:                                            # To overcome this issue
                            j = 1
                            newName = os.path.join(a, key, norm_file_name + str(j) + ext)
                            while os.path.exists(newName):
                                j += 1
                                newName = os.path.join(a, key, norm_file_name + str(j) + ext)   # Add number to file name
                            shutil.move(c, newName)
                if ext.upper().removeprefix('.') not in all_ext:                        # To add unknown ext to list
                    if ext not in unknown_ext:                                          # If it is already there skip
                        unknown_ext.append(ext) 
                    unknown_file_name = os.path.split(file_name)[1]                                       
                    if key == 'Unknown':
                        try:
                            for g, val in all_files.items():
                                if g == 'Unknown':
                                    val.append(unknown_file_name + ext)
                            shutil.move(i, os.path.join(a, 'Unknown'))
                        except shutil.Error:
                            j = 1
                            newName = os.path.join(a, 'Unknown', unknown_file_name + str(j) + ext)
                            while os.path.exists(newName):
                                j += 1
                                newName = os.path.join(a, 'Unknown', unknown_file_name + str(j) + ext)
                            shutil.move(i, newName)

        elif os.path.split(i)[1] not in dir_suff_dict.keys():                           # Recurse if folder  
            # (path_to, folder_name) = os.path.split(i)                                   # rename it
            # norm_folder_name = normalize(folder_name)                                   # Normalize the folder name
            # d = Path(os.path.join(path_to, norm_folder_name))                           # Rename the folder
            # os.rename(i, d)
            sort_folder(i)                                                              # Recurse function 
    return f'All unknown ext: {unknown_ext}. \nAll sorted ext {known_ext}.\n'


if __name__ == "__main__":
    start = time()
    pr_rf = Process(target=sort_folder, args=(a, ))
    pr_rf.start()
    pr_rf.join()
    # sort_folder(a)
    removeEmptyFolders(a)
    # for key in all_files.keys():
    #     if key in all_files:
    #         print(f"Files in {key}: {all_files[key]}.\n")
    print(time() - start)
