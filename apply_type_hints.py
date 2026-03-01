import libcst as cst
from typing import Type

class ReturnTypeHintTransformer(cst.CSTTransformer):
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        name = original_node.name.value
        if name == "setUp" or name.startswith("test_"):
            if updated_node.returns is None:
                return updated_node.with_changes(returns=cst.Annotation(cst.Name("None")))
        elif name == "_make_request":
            if updated_node.returns is None:
                updated_node = updated_node.with_changes(returns=cst.Annotation(cst.Name("HttpRequest")))
            
            # Update params to add User type hint if missing
            new_params = []
            for param in updated_node.params.params:
                if param.name.value == "user" and param.annotation is None:
                    new_params.append(param.with_changes(annotation=cst.Annotation(cst.Name("User"))))
                else:
                    new_params.append(param)
            updated_node = updated_node.with_changes(params=updated_node.params.with_changes(params=new_params))
            return updated_node
            
        return updated_node

with open("users/tests.py", "r", encoding="utf-8") as f:
    source = f.read()
module = cst.parse_module(source)

# We need to add imports for User and HttpRequest
import_nodes = [
    cst.ImportFrom(
        module=cst.Name("django").with_changes(value="django.http"),
        names=[cst.ImportAlias(name=cst.Name("HttpRequest"))],
    ),
    cst.ImportFrom(
        module=cst.Name("django").with_changes(value="django.contrib.auth.models"),
        names=[cst.ImportAlias(name=cst.Name("User"))],
    )
]

modified_module = module.visit(ReturnTypeHintTransformer())

# Insert imports after the first few imports safely
body = list(modified_module.body)
body.insert(5, import_nodes[0])
body.insert(6, import_nodes[1])
modified_module = modified_module.with_changes(body=body)

with open("users/tests.py", "w", encoding="utf-8") as f:
    f.write(modified_module.code)
