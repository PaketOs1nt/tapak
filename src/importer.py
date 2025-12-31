import importlib
import importlib.metadata
import sys
import typing
from dataclasses import dataclass

import pip


@dataclass
class Module:
    name: str
    version: str

    def check(self) -> bool:
        if importlib.util.find_spec(self.name) is None:  # type: ignore
            return False

        if importlib.metadata.version(self.name) != self.version:
            return False

        return True

    def install(self):
        try:
            sys.stderr = typing.TextIO()
            pip.main(["install", f"{self.name}=={self.version}"])

        except BaseException as e:
            print(e)

        finally:
            sys.stderr = sys.__stderr__
