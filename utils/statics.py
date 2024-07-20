import os
import re

def extract_number(filename):
    match = re.search(r"(\d+)_img", filename)
    if match:
        return int(match.group(1))
    return 0

regex = r"_\d+\.txt"

source_pathS = "output\\sick"
target_pathS = "dataset\\sick"

source_pathH = "output\\healthy"
target_pathH = "dataset\\healthy"

for filenameH in os.listdir(source_pathH):
    if "Dinamic" in filenameH or re.search(regex, filenameH):
        continue
    else:
        full_source_path = os.path.join(source_pathH, filenameH)

        if not os.path.exists(target_pathH):
            os.makedirs(target_pathH)
        
        full_target_path = os.path.join(target_pathH, filenameH)

        with open(full_source_path, "rb") as source, open(full_target_path, "wb") as target:
           content = source.read()
           target.write(content)


for filenameS in os.listdir(source_pathS):
    if "Dinamic" in filenameS or re.search(regex, filenameS):
        continue
    else:
        full_source_path = os.path.join(source_pathS, filenameS)

        if not os.path.exists(target_pathS):
            os.makedirs(target_pathS)
        
        full_target_path = os.path.join(target_pathS, filenameS)

        with open(full_source_path, "rb") as source, open(full_target_path, "wb") as target:
           content = source.read()
           target.write(content)

print("Tamanho Source_healthy",len(os.listdir(source_pathH)))
print("Tamanho target_healthy",len(os.listdir(target_pathH)))
print("----------------------------------------------------------")
print("Tamanho Source_Sick",len(os.listdir(source_pathS)))
print("Tamanho Target_Sick",len(os.listdir(target_pathS)))
    

    




