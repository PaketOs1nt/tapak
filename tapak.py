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

_22e9f457d54debef = ModuleLoader()
importer = _22e9f457d54debef.load('importer', "\n_889d169abc44a419 = ModuleLoader()\n_91cbad002c3d87d5 = ModuleLoader()\nimport importlib\nimport importlib.metadata\nimport sys\nimport typing\nfrom dataclasses import dataclass\nimport pip\n\n@dataclass\nclass Module:\n    name: str\n    version: str\n\n    def check(self) -> bool:\n        if importlib.util.find_spec(self.name) is None:\n            return False\n        if importlib.metadata.version(self.name) != self.version:\n            return False\n        return True\n\n    def install(self):\n        try:\n            sys.stderr = typing.TextIO()\n            pip.main(['install', f'{self.name}=={self.version}'])\n        except BaseException as e:\n            print(e)\n        finally:\n            sys.stderr = sys.__stderr__", 'importer.py')
REQ = [importer.Module('requests', '2.32.3')]
for r in REQ:
    if not r.check():
        print('installing ' + r.name)
        r.install()
        print('installed ' + r.name)
repo = _22e9f457d54debef.load('repo', '\n_27758438cd01a482 = ModuleLoader()\n_5bc0e0929cc89b2e = ModuleLoader()\nfrom dataclasses import dataclass\nfrom typing import List\nimport requests\nimporter = _27758438cd01a482.load(\'importer\', "\\n_889d169abc44a419 = ModuleLoader()\\n_91cbad002c3d87d5 = ModuleLoader()\\nimport importlib\\nimport importlib.metadata\\nimport sys\\nimport typing\\nfrom dataclasses import dataclass\\nimport pip\\n\\n@dataclass\\nclass Module:\\n    name: str\\n    version: str\\n\\n    def check(self) -> bool:\\n        if importlib.util.find_spec(self.name) is None:\\n            return False\\n        if importlib.metadata.version(self.name) != self.version:\\n            return False\\n        return True\\n\\n    def install(self):\\n        try:\\n            sys.stderr = typing.TextIO()\\n            pip.main([\'install\', f\'{self.name}=={self.version}\'])\\n        except BaseException as e:\\n            print(e)\\n        finally:\\n            sys.stderr = sys.__stderr__", \'importer.py\')\n\nclass ReqirementJson(importer.Module):\n\n    @staticmethod\n    def from_json(data: dict) -> \'ReqirementJson\':\n        return ReqirementJson(data.get(\'name\', \'\').strip(), data.get(\'version\', \'\').strip())\n\n@dataclass\nclass ModuleJson:\n    name: str\n    desc: str\n    code: str\n    requirements: List[ReqirementJson]\n\n    @staticmethod\n    def from_json(data: dict) -> \'ModuleJson\':\n        return ModuleJson(data.get(\'name\', \'\'), data.get(\'desc\', \'\'), data.get(\'code\', \'\'), [ReqirementJson.from_json(req) for req in data.get(\'requirements\', [])])\n\n    def check_requirements(self) -> bool:\n        for req in self.requirements:\n            if not req.check():\n                return False\n        return True\n\n    def install_requirements(self):\n        for req in self.requirements:\n            if not req.check():\n                req.install()\n\n    def execute(self):\n        exec(compile(self.code, \'name.py\', \'exec\'), {\'ModuleLoader\': globals()[\'ModuleLoader\'], \'__name__\': \'__main__\'})\n\n@dataclass\nclass RepoJson:\n    name: str\n    author: str\n    modules: List[ModuleJson]\n\n    @staticmethod\n    def from_json(data: dict) -> \'RepoJson\':\n        return RepoJson(data.get(\'name\', \'\'), data.get(\'author\', \'\'), [ModuleJson.from_json(module) for module in data.get(\'modules\', [])])\n\nclass Repo:\n\n    def __init__(self, url: str) -> None:\n        self.url = url\n        self.load()\n\n    def load(self):\n        raw = requests.get(self.url).json()\n        self.repo = RepoJson.from_json(raw)', 'repo.py')
REPO_URL = 'https://raw.githubusercontent.com/PaketOs1nt/tapak/refs/heads/main/repo.json'

class Main:

    def ic(self, data: str):
        for ln in data.split('\n'):
            print(f'[tapak] {ln}')

    def get(self, data: str):
        return input(f'[tapak] {data} > ')

    def first(self):
        self.repo = repo.Repo(REPO_URL)
        self.ic(f'loaded repo "{self.repo.repo.name}" by {self.repo.repo.author}')

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
            case ['save', module]:
                for mod in self.repo.repo.modules:
                    if mod.name == module:
                        path = f'{mod.name}.py'
                        with open(path, 'w') as f:
                            f.write(mod.code)
                        self.ic(f'saved to {path}')
                        break
            case ['ls']:
                for module in self.repo.repo.modules:
                    self.ic(f'module name: {module.name}')
                    self.ic(f'module description: {module.desc}')
                    if module.requirements:
                        self.ic('module requirements:')
                        for req in module.requirements:
                            self.ic(f"{req.name} {req.version} ({('' if req.check() else 'not ')}installed)")
                    self.ic('=' * 20)
            case ['help']:
                self.ic('exit - exit the shell\nrun <name> - run module\nhelp - print help\nls - show modules\nsave <name> - save module as python file')
        return True

    def main(self):
        self.first()
        while True:
            try:
                if not self.looped():
                    break
            except Exception as e:
                self.ic(str(e))
if __name__ == '__main__':
    app = Main()
    app.main()