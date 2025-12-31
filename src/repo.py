from dataclasses import dataclass
from typing import List

import requests

import importer


class ReqirementJson(importer.Module):
    @staticmethod
    def from_json(data: dict) -> "ReqirementJson":
        return ReqirementJson(data.get("name", ""), data.get("version", ""))


@dataclass
class ModuleJson:
    name: str
    desc: str
    code: str
    requirements: List[ReqirementJson]

    @staticmethod
    def from_json(data: dict) -> "ModuleJson":
        return ModuleJson(
            data.get("name", ""),
            data.get("desc", ""),
            data.get("code", ""),
            [ReqirementJson.from_json(req) for req in data.get("requirements", [])],
        )

    def check_requirements(self) -> bool:
        for req in self.requirements:
            if not req.check():
                return False

        return True

    def install_requirements(self):
        for req in self.requirements:
            if not req.check():
                req.install()

    def execute(self):
        exec(compile(self.code, "name.py", "exec"), {})


@dataclass
class RepoJson:
    name: str
    author: str
    modules: List[ModuleJson]

    @staticmethod
    def from_json(data: dict) -> "RepoJson":
        return RepoJson(
            data.get("name", ""),
            data.get("author", ""),
            [ModuleJson.from_json(module) for module in data.get("modules", [])],
        )


class Repo:
    def __init__(self, url: str) -> None:
        self.url = url
        self.load()

    def load(self):
        raw = requests.get(self.url).json()
        self.repo = RepoJson.from_json(raw)
