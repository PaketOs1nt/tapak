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

_5f60d4af8981d0a3 = ModuleLoader()
importer = _5f60d4af8981d0a3.load('importer', "\n_4bfc2ffe6703a974 = ModuleLoader()\n_0291f2f9ccdba437 = ModuleLoader()\nimport importlib\nimport importlib.metadata\nimport sys\nimport typing\nfrom dataclasses import dataclass\nimport pip\n\n@dataclass\nclass Module:\n    name: str\n    version: str\n\n    def check(self) -> bool:\n        if importlib.util.find_spec(self.name) is None:\n            return False\n        if importlib.metadata.version(self.name) != self.version:\n            return False\n        return True\n\n    def install(self):\n        try:\n            sys.stderr = typing.TextIO()\n            pip.main(['install', f'{self.name}=={self.version}'])\n        except BaseException as e:\n            print(e)\n        finally:\n            sys.stderr = sys.__stderr__", 'importer.py')
REQ = [importer.Module('requests', '2.32.3')]
for r in REQ:
    if not r.check():
        print('installing ' + r.name)
        r.install()
        print('installed ' + r.name)
repo = _5f60d4af8981d0a3.load('repo', '\n_7e4af656dbf31161 = ModuleLoader()\n_6b0fafd48bb3bf81 = ModuleLoader()\nfrom dataclasses import dataclass\nfrom typing import List\nimport requests\nimporter = _7e4af656dbf31161.load(\'importer\', "\\n_4bfc2ffe6703a974 = ModuleLoader()\\n_0291f2f9ccdba437 = ModuleLoader()\\nimport importlib\\nimport importlib.metadata\\nimport sys\\nimport typing\\nfrom dataclasses import dataclass\\nimport pip\\n\\n@dataclass\\nclass Module:\\n    name: str\\n    version: str\\n\\n    def check(self) -> bool:\\n        if importlib.util.find_spec(self.name) is None:\\n            return False\\n        if importlib.metadata.version(self.name) != self.version:\\n            return False\\n        return True\\n\\n    def install(self):\\n        try:\\n            sys.stderr = typing.TextIO()\\n            pip.main([\'install\', f\'{self.name}=={self.version}\'])\\n        except BaseException as e:\\n            print(e)\\n        finally:\\n            sys.stderr = sys.__stderr__", \'importer.py\')\n\nclass ReqirementJson(importer.Module):\n\n    @staticmethod\n    def from_json(data: dict) -> \'ReqirementJson\':\n        return ReqirementJson(data.get(\'name\', \'\'), data.get(\'version\', \'\'))\n\n@dataclass\nclass ModuleJson:\n    name: str\n    desc: str\n    code: str\n    requirements: List[ReqirementJson]\n\n    @staticmethod\n    def from_json(data: dict) -> \'ModuleJson\':\n        return ModuleJson(data.get(\'name\', \'\'), data.get(\'desc\', \'\'), data.get(\'code\', \'\'), [ReqirementJson.from_json(req) for req in data.get(\'requirements\', [])])\n\n    def check_requirements(self) -> bool:\n        for req in self.requirements:\n            if not req.check():\n                return False\n        return True\n\n    def install_requirements(self):\n        for req in self.requirements:\n            if not req.check():\n                req.install()\n\n    def execute(self):\n        exec(compile(self.code, \'name.py\', \'exec\'), {\'ModuleLoader\': globals()[\'ModuleLoader\']})\n\n@dataclass\nclass RepoJson:\n    name: str\n    author: str\n    modules: List[ModuleJson]\n\n    @staticmethod\n    def from_json(data: dict) -> \'RepoJson\':\n        return RepoJson(data.get(\'name\', \'\'), data.get(\'author\', \'\'), [ModuleJson.from_json(module) for module in data.get(\'modules\', [])])\n\nclass Repo:\n\n    def __init__(self, url: str) -> None:\n        self.url = url\n        self.load()\n\n    def load(self):\n        raw = requests.get(self.url).json()\n        self.repo = RepoJson.from_json(raw)', 'repo.py')
REPO_URL = 'https://raw.githubusercontent.com/PaketOs1nt/tapak/refs/heads/main/repo.json'

class Main:

    def ic(self, data: str):
        for ln in data.split('\n'):
            print(f'[tapak] {ln}')

    def get(self, data: str):
        return input(f'[tapak] {data} > ')

    def first(self):
        self.repo = repo.Repo(REPO_URL)
        self.ic(f'loaded repo {self.repo.repo.name} by {self.repo.repo.author}')

    def looped(self) -> bool:
        inp = self.get('command').split(' ')
        self.ic('=' * 20)
        match inp:
            case ['exit']:
                return False
            case ['run', module]:
                for mod in self.repo.repo.modules:
                    if mod.name == module:
                        mod.install_requirements()
                        mod.execute()
                        break
            case ['ls']:
                for module in self.repo.repo.modules:
                    self.ic(f'module name: {module.name}')
                    self.ic(f'module description: {module.desc}')
                    if module.requirements:
                        self.ic('module requirements:')
                        for req in module.requirements:
                            self.ic(f"{req.name} {req.version} ({('' if req.check() else 'not')} installed)")
                    self.ic('=' * 20)
            case ['help']:
                self.ic('exit - exit the shell\nrun <name> - run module\nhelp - print help\nls - show modules')
        return True

    def main(self):
        self.first()
        while True:
            if not self.looped():
                break
if __name__ == '__main__':
    app = Main()
    app.main()