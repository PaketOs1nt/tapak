import importer

REQ = [importer.Module("requests", "2.32.3")]

for r in REQ:
    if not r.check():
        print("installing " + r.name)
        r.install()
        print("installed " + r.name)

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
        self.repo = repo.Repo(REPO_URL)
        self.ic(f"loaded repo {self.repo.repo.name} by {self.repo.repo.name}")

    def looped(self) -> bool:
        inp = self.get("command").split(" ")
        self.ic("=" * 20)
        match inp:
            case ["exit"]:
                return False

            case "run", module:
                for mod in self.repo.repo.modules:
                    if mod.name == module:
                        mod.install_requirements()
                        mod.execute()
                        break

            case ["ls"]:
                for module in self.repo.repo.modules:
                    self.ic(f"module name: {module.name}")
                    self.ic(f"module description: {module.desc}")
                    if module.requirements:
                        self.ic("module requirements:")
                        for req in module.requirements:
                            self.ic(
                                f"{req.name} {req.version} ({'' if req.check() else 'not'} installed)"
                            )
                    self.ic("=" * 20)

            case ["help"]:
                self.ic(
                    "exit - exit the shell\nrun <name> - run module\nhelp - print help\nls - show modules"
                )

        return True

    def main(self):
        self.first()
        while True:
            if not self.looped():
                break


if __name__ == "__main__":
    app = Main()
    app.main()
