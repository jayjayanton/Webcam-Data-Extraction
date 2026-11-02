import glob
import os
import numpy as np
import urllib.request

parent_dir = "G:/TDOT Webscrapping/"

last_dir = max(glob.glob(os.path.join(parent_dir, '*/')), key=os.path.getmtime)

current_dir = os.chdir(last_dir)

Text_Files = sorted(glob.glob("*.txt"))
Missing_Webcams = f"Missing_Webcams.txt"
for Text in Text_Files:
    with open(Text, "r") as t:
        for row in t.readlines():
            # try:
            row = row.split("_")
            url = row[-1].split()
            name = row[1:2]
            name = "''".join(name)
            if bool(name):
                # print(name)
                with open(Missing_Webcams, 'a') as fp:
                    pass

                    for i in url:
                        try:# urllib.request.urlretrieve(i, f"{name}.jpg")
                            if not i.startswith("https:"):
                                urllib.request.urlretrieve(i, f"{name}.jpg")
                            else:
                                fp.write(f"{name}\n")
                        except Exception as e:
                            # print(f"{e}")
                            fp.write(f"{name}\n")
                            continue
