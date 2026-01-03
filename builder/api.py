from types import ModuleType


class ModuleLoader:
    cache: dict[tuple[str, str], ModuleType] = {}

    def __init__(self) -> None:
        self.modules = {}

    def _load(self, name: str, code: str, filename: str) -> ModuleType:
        if (name, filename) not in ModuleLoader.cache:
            mod = ModuleType(name)
            mod.__file__ = filename
            mod.__dict__["ModuleLoader"] = ModuleLoader
            exec(compile(code, filename, "exec"), mod.__dict__)

            self.modules[name] = mod
            ModuleLoader.cache[(name, filename)] = mod

            return mod

        return ModuleLoader.cache[(name, filename)]

    def load(self, name: str, code: str, filename: str):
        globals()[name] = self._load(name, code, filename)

    def from_cache(self, name, filename):
        self.load(name, "", filename)
