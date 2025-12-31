from types import ModuleType


class ModuleLoader:
    def __init__(self) -> None:
        self.modules = {}

    def load(self, name: str, code: str, filename: str) -> ModuleType:
        mod = ModuleType(name)
        mod.__file__ = filename

        exec(compile(code, filename, "exec"), mod.__dict__)

        self.modules[name] = mod

        return mod


_8d8b11b3163521e5 = ModuleLoader()
test = _8d8b11b3163521e5.load("test", "asd = 123123123\r\n", "test.py")
print(test.asd)
