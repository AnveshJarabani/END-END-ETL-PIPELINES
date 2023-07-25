import subprocess,glob
scripts=glob.glob("*.py")
BI_PULLS=[i for i in scripts if 'BI_PULL'in i and "ALL" not in i]
BI_TO_DB=[i for i in scripts if 'LOAD' in i]
processes=[]
for i in BI_PULLS:
    p=subprocess.Popen(["python",i],stderr=subprocess.DEVNULL)
    processes.append(p)
for p in processes:
    p.wait()
for i in BI_TO_DB:
    subprocess.Popen(["python",i],stderr=subprocess.DEVNULL)