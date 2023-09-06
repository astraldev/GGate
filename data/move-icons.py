import os

path = "./images"
target = "./images/apps"

for file in os.listdir(path):
    fn = os.path.join(path, file)
    if os.path.isfile(fn):
        size = file.split(".")[0].split("-")[-1]
        target_dir = os.path.join(target, f"{size}x{size}")
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)
        os.system(f"mv {fn} {target_dir}/ggate.png")
