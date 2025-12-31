import os

import builder

os.chdir("src")

build = builder.Builder.from_file("main.py")
build.add_module("test.py")

print(build.build())
