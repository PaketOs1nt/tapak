from types import ModuleType
class ModuleLoader:
 cache:dict[tuple[str, str], ModuleType]={}
 def __init__(self)->None:
  self.modules={}
 def load(self,name:str,code:str,filename:str)->ModuleType:
  if (name, filename) not in ModuleLoader.cache:
   mod=ModuleType(name)
   mod.__file__=filename
   mod.__dict__['ModuleLoader']=ModuleLoader
   exec(compile(code,filename,'exec'),mod.__dict__)
   self.modules[name]=mod
   ModuleLoader.cache[name, filename]=mod
   return mod
  return ModuleLoader.cache[name, filename]
_8a4c6beb2ba9255a = ModuleLoader()
importer=_8a4c6beb2ba9255a.load('importer',"import importlib\nimport importlib.metadata\nimport sys\nimport typing\nfrom dataclasses import dataclass\nimport pip\n@dataclass\nclass Module:\n name:str\n version:str\n def check(self)->bool:\n  if importlib.util.find_spec(self.name) is None:\n   return 0x0\n  if importlib.metadata.version(self.name) != self.version:\n   return 0x0\n  return 0o1\n def install(self):\n  try:\n   sys.stderr=typing.TextIO()\n   pip.main(['install',f'{self.name}=={self.version}'])\n  except BaseException as e:\n   print(e)\n  finally:\n   sys.stderr=sys.__stderr__",'importer.py')
REQ=[importer.Module('requests','2.32.3')]
for r in REQ:
 if not r.check():
  print('installing '+r.name)
  r.install()
  print('installed '+r.name)
repo=_8a4c6beb2ba9255a.load('repo',"from dataclasses import dataclass\nfrom typing import List\nimport requests\nimporter=ModuleLoader.cache['importer', 'importer.py']\nclass ReqirementJson(importer.Module):\n @staticmethod\n def from_json(data:dict)->'ReqirementJson':\n  return ReqirementJson(data.get('name','').strip(),data.get('version','').strip())\n@dataclass\nclass ModuleJson:\n name:str\n desc:str\n code:str\n requirements:List[ReqirementJson]\n @staticmethod\n def from_json(data:dict)->'ModuleJson':\n  return ModuleJson(data.get('name',''),data.get('desc',''),data.get('code',''),[ReqirementJson.from_json(req) for req in data.get('requirements',[])])\n def check_requirements(self)->bool:\n  for req in self.requirements:\n   if not req.check():\n    return 0b0\n  return 0b1\n def install_requirements(self):\n  for req in self.requirements:\n   if not req.check():\n    req.install()\n def execute(self):\n  exec(compile(self.code,'name.py','exec'),{'ModuleLoader':globals()['ModuleLoader'],'__name__':'__main__'})\n@dataclass\nclass RepoJson:\n name:str\n author:str\n modules:List[ModuleJson]\n @staticmethod\n def from_json(data:dict)->'RepoJson':\n  return RepoJson(data.get('name',''),data.get('author',''),[ModuleJson.from_json(module) for module in data.get('modules',[])])\nclass Repo:\n def __init__(self,url:str)->None:\n  self.url=url\n  self.load()\n def load(self):\n  raw=requests.get(self.url).json()\n  self.repo=RepoJson.from_json(raw)",'repo.py')
REPO_URL='https://raw.githubusercontent.com/PaketOs1nt/tapak/refs/heads/main/repo.json'
class Main:
 def ic(self,data:str):
  for ln in data.split('\n'):
   print(f'[tapak] {ln}')
 def get(self,data:str):
  return input(f'[tapak] {data} > ')
 def first(self):
  self.repo=repo.Repo(REPO_URL)
  self.ic(f'loaded repo "{self.repo.repo.name}" by {self.repo.repo.author}')
 def looped(self)->bool:
  inp=self.get('command').split(' ')
  self.ic('='*0o24)
  match inp:
   case ['exit']:
    return 0b0
   case ['run',module]:
    for mod in self.repo.repo.modules:
     if mod.name == module:
      mod.install_requirements()
      mod.execute()
      break
   case ['save',module]:
    for mod in self.repo.repo.modules:
     if mod.name == module:
      path=f'{mod.name}.py'
      with open(path,'wb') as f:
       f.write(mod.code.encode())
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
     self.ic('='*0x14)
   case ['load',new_repo_url]:
    self.repo=repo.Repo(new_repo_url)
    self.ic(f'loaded repo "{self.repo.repo.name}" by {self.repo.repo.author}')
   case ['help']:
    self.ic('exit - exit the shell\nrun <name> - run module\nhelp - print help\nls - show modules\nsave <name> - save module as python file')
  return 0o1
 def main(self):
  self.first()
  while 0o1:
   try:
    if not self.looped():
     break
   except Exception as e:
    self.ic(str(e))
if __name__ == '__main__':
 app=Main()
 app.main()