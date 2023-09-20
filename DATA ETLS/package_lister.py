import os
from glob import glob

lst = glob("./*.py", root_dir=None)
all_packages=[]
for i in lst:
    with open(i, "r") as f:
        content = f.read()
        cont_lst=content.split("\n")
        cont_lst=[i for i in cont_lst if i.startswith("import") or i.startswith("from")]
    all_packages.extend(cont_lst)
all_packages=set(all_packages)
with open("packages_list.txt", "w") as f2:
        for package in all_packages:
            f2.write(package)
            f2.write("\n")
        