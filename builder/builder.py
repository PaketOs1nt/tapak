import ast
import os
from dataclasses import dataclass
from typing import Any


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
    def __init__(self, modules: dict[str, PreModule]) -> None:
        super().__init__()
        self.final: ast.AST | None = None
        self.loader_name = "_" + os.urandom(8).hex()
        self.modules = modules

    def visit(self, node: ast.AST) -> ast.AST:
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
        api_path = os.path.join(os.path.dirname(__file__), "api.py")
        with open(api_path, "rb") as f:
            api_code = f.read().decode()

        result = f"{api_code}\n{self.loader_name} = ModuleLoader()\n"
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
        self.modules = {}

    def add_module(self, file: str):
        with open(file, "rb") as f:
            code = f.read().decode()

        name = os.path.splitext(file)[0]
        self.modules[name] = PreModule(name, code, file)

    def build(self):
        ast_code = ast.parse(self.code)
        fix_imports = AstOnefileImports(self.modules)
        fix_imports.visit(ast_code)

        result = fix_imports.compile()
        return result
