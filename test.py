import os

def changename(name):
    nameList = name.split("_")
    for i in range(len(nameList) - 1):
        nameList[i] = nameList[i].lower()
    return "_".join(nameList)

directory = 'data/processed_descriptions'

for filename in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, filename)):
        new_name = changename(filename)
        if new_name != filename:  # Avoid unnecessary renaming
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))
