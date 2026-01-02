import hashlib

import requests

import importer

REQUIREMENTS = [importer.Module("requests", "2.32.3")]
LAST_VER = "https://raw.githubusercontent.com/PaketOs1nt/tapak/refs/heads/main/tapak.py"

for requirement in REQUIREMENTS:
    if not requirement.check():
        print("[loader] installing " + requirement.name)
        requirement.install()
        print("[loader] installed " + requirement.name)

LAST_CONTENT = requests.get(LAST_VER).content

with open(__file__, "rb") as f:
    current_hash = hashlib.sha256(f.read()).hexdigest()
last_hash = hashlib.sha256(LAST_CONTENT).hexdigest()

if last_hash != current_hash:
    print("[loader] updating...")
    with open(__file__, "wb") as f:
        f.write(LAST_CONTENT)

    print("[loader] updated! need restart")
    exit()
else:
    print("[loader] you using last version!")


import repo

REPO_URL = (
    "https://raw.githubusercontent.com/PaketOs1nt/tapak/refs/heads/main/repo.json"
)


class Main:
    def ic(self, data: str):
        for ln in data.split("\n"):
            print(f"[tapak] {ln}")

    def get(self, data: str):
        return input(f"[tapak] {data} > ")

    def first(self):
        self.repo = repo.Repo(REPO_URL)  # type: ignore
        self.ic(f'loaded repo "{self.repo.repo.name}" by {self.repo.repo.author}')

    def looped(self) -> bool:
        inp = self.get("command").split(" ")
        self.ic("=" * 25)
        match inp:
            case ["exit"]:
                return False

            case "run", module:
                for mod in self.repo.repo.modules:
                    if mod.name == module:
                        mod.install_requirements()
                        mod.execute()
                        break

            case "save", module:
                for mod in self.repo.repo.modules:
                    if mod.name == module:
                        path = f"{mod.name}.py"
                        with open(path, "wb") as f:
                            f.write(mod.code.encode())
                        self.ic(f"saved to {path}")
                        break

            case ["ls"]:
                for module in self.repo.repo.modules:
                    self.ic(f"module name: {module.name}")
                    self.ic(f"module description: {module.desc}")
                    if module.requirements:
                        self.ic("module requirements:")
                        for req in module.requirements:
                            self.ic(
                                f"{req.name} {req.version} ({'' if req.check() else 'not '}installed)"
                            )
                    self.ic("=" * 25)

            case "load", new_repo_url:
                self.repo = repo.Repo(new_repo_url)  # type: ignore
                self.ic(
                    f'loaded repo "{self.repo.repo.name}" by {self.repo.repo.author}'
                )

            case ["help"]:
                self.ic(
                    "help - print help\n"
                    "run <name> - run module\n"
                    "save <name> - save module as python file\n"
                    "ls - show modules\n"
                    "load <repo-url> - use custom repo"
                )

        return True

    def main(self):
        self.first()
        while True:
            try:
                if not self.looped():
                    break
            except BaseException as e:
                self.ic(str(e))


if __name__ == "__main__":
    app = Main()
    app.main()
