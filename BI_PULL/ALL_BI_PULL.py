import subprocess,glob
scripts=glob.glob("*.py")
BI_PULLS=[i for i in scripts if 'ALL' not in i and "DB" not in i]
BI_TO_DB=[i for i in scripts if 'DB' in i]
for i in BI_PULLS:
    subprocess.run(["python",i],stderr=subprocess.DEVNULL)
for i in BI_TO_DB:
    subprocess.run(["python",i],stderr=subprocess.DEVNULL)
    

