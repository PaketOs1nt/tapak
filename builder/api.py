from types import ModuleType


class ModuleLoader:
    def __init__(self) -> None:
        self.modules = {}

    def load(self, name: str, code: str, filename: str) -> ModuleType:
        mod = ModuleType(name)
        mod.__file__ = filename
        mod.__dict__["ModuleLoader"] = ModuleLoader
        exec(compile(code, filename, "exec"), mod.__dict__)

        self.modules[name] = mod

        return mod
