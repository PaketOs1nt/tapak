import os

import builder

os.chdir("src")

MAIN_FILE = "main.py"
RESULT_FILE = "tapak.py"

MODULES = ["importer.py", "repo.py"]

build = builder.Builder.from_file(MAIN_FILE)
print(f"[builder] loaded main file {MAIN_FILE}")

for module in MODULES:
    build.add_module(module)
    print(f"[builder] added module {module}")

result = build.build()
print(f"[builder] compiled main file {MAIN_FILE}")

os.chdir("..")

with open(RESULT_FILE, "wb") as f:
    binary = result.encode()
    f.write(binary)

    print(f"[builder] result saved to {RESULT_FILE} ({len(binary)} bytes)")
