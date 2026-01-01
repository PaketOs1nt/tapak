import os
from dataclasses import dataclass
from typing import Any

from . import obfunparse as ast


@dataclass
class PreModule:
    name: str
    code: str
    file: str

    def build(self, loadername: str) -> ast.AST:
        return ast.Assign(
            targets=[ast.Name(id=self.name, ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=loadername, ctx=ast.Load()),
                    attr="load",
                    ctx=ast.Load(),
                ),
                args=[
                    ast.Constant(value=self.name),
                    ast.Constant(value=self.code),
                    ast.Constant(value=self.file),
                ],
                keywords=[],
            ),
        )


class AstOnefileImports(ast.NodeTransformer):
    def __init__(
        self, modules: dict[str, PreModule], _ModuleLoader: bool = True
    ) -> None:
        super().__init__()
        self.final: ast.AST | None = None
        self.loader_name = "_" + os.urandom(8).hex()
        self.modules = modules
        self._ModuleLoader = _ModuleLoader

    def visit(self, node: ast.AST) -> ast.AST | None:
        result = super().visit(node)
        self.final = result
        return result

    def visit_Import(self, node: ast.Import) -> Any:
        if len(node.names) == 1:
            name = node.names[0].name
            if name in self.modules:
                return ast.fix_missing_locations(
                    self.modules[name].build(self.loader_name)  # type: ignore
                )

        return self.generic_visit(node)

    def compile(self) -> str:
        if self._ModuleLoader:
            api_path = os.path.join(os.path.dirname(__file__), "api.py")
            with open(api_path, "rb") as f:
                api_code = ast.unparse(ast.parse(f.read().decode()))
        else:
            api_code = ""

        if len(self.modules) > 0:
            result = f"{api_code}\n{self.loader_name} = ModuleLoader()\n"
        else:
            result = ""

        if self.final:
            result += ast.unparse(self.final)

        return result


class Builder:
    @staticmethod
    def from_file(path: str) -> "Builder":
        with open(path, "rb") as f:
            code = f.read().decode()

        name = os.path.splitext(path)[0]
        return Builder(code, name)

    def __init__(self, code: str, name: str) -> None:
        self.code = code
        self.name = name
        self.modules: dict[str, PreModule] = {}

    def add_module(self, file: str):
        with open(file, "rb") as f:
            code = f.read().decode()

        name = os.path.splitext(file)[0]
        self.modules[name] = PreModule(name, code, file)

    def build(self, _ModuleLoader: bool = True):
        for mod in self.modules.values():
            without = self.modules.copy()
            del without[mod.name]
            mod_builder = Builder(mod.code, mod.file)
            mod_builder.modules = without
            mod.code = mod_builder.build(_ModuleLoader=False)

        ast_code = ast.parse(self.code)
        fix_imports = AstOnefileImports(self.modules, _ModuleLoader=_ModuleLoader)
        fix_imports.visit(ast_code)

        result = fix_imports.compile()
        return result
