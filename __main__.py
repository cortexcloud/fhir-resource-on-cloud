import platform
import glob

from datetime import datetime
from fhir_transformer.csop.processor import process

def run():
    slash = "\\" if platform.system() == "Windows" else "/"
    print(f"Converting CSOP Files in {slash}uploads{slash}csop{slash}")
    files = glob.glob(f".{slash}uploads{slash}csop{slash}*")
    if len(files) == 0:
        print(f"No file found in .{slash}uploads{slash}csop{slash}")
    else:
        print(f"{len(files)} file found in .{slash}uploads{slash}csop{slash}")
        print(f"Try matching the files")

        bill_trans_files = list()
        bill_disp_files = list()

        for file in files:
            if "BILLTRAN" in file.upper():
                bill_trans_files.append(file)
            if "BILLDISP" in file.upper():
                bill_disp_files.append(file)
        if len(bill_trans_files) == len(bill_disp_files):
            for i in range(0,len(bill_trans_files)):
                path_trans = bill_trans_files[i] 
                path_disps = bill_disp_files[i] 
                process(path_trans,path_disps,datetime.now().date(),i)
        else:
            print('no. bill trans files doesnt match with no. bill disp files')
run()