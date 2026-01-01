import json
import os

import builder

AUTHOR = "@PaketPKSoftware"
REPO_NAME = "Paket Base Repo"

PATH = "repo"

modules = os.listdir(PATH)

structure = {"name": REPO_NAME, "author": AUTHOR, "modules": []}

start_dir = os.path.dirname(__file__)

for module in modules:
    module_structure = {"name": module, "requirements": [], "desc": ""}
    path = os.path.join(PATH, module)

    main = module + ".py"

    connected = os.listdir(path)

    connected.remove(main)

    os.chdir(path)

    build = builder.Builder.from_file(main)

    for conn in connected:
        if conn.endswith(".py"):
            build.add_module(conn)

    code = build.build()
    module_structure["code"] = code

    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            for line in f.readlines():
                name, ver = line.split("==")
                module_structure["requirements"].append(
                    {"name": name.strip(), "version": ver.strip()}
                )

    if os.path.exists(f"{module}.txt"):
        with open(f"{module}.txt", "r") as f:
            module_structure["desc"] = f.read().strip()

    structure["modules"].append(module_structure)
    os.chdir(start_dir)

with open("repo.json", "w") as f:
    json.dump(structure, f, indent=4)
