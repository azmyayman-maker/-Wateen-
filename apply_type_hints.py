import libcst as cst

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

def _dotted_module(path: str) -> cst.BaseExpression:
    parts = path.split('.')
    expr = cst.Name(parts[0])
    for part in parts[1:]:
        expr = cst.Attribute(value=expr, attr=cst.Name(part))
    return expr

# We need to add imports for User and HttpRequest
import_nodes = [
    cst.ImportFrom(
        module=_dotted_module("django.http"),
        names=[cst.ImportAlias(name=cst.Name("HttpRequest"))],
    ),
    cst.ImportFrom(
        module=_dotted_module("django.contrib.auth.models"),
        names=[cst.ImportAlias(name=cst.Name("User"))],
    )
]

modified_module = module.visit(ReturnTypeHintTransformer())

body = list(modified_module.body)
insert_pos = 0

# Scan for initial docstring or import blocks to find the insertion point
for idx, node in enumerate(body):
    if isinstance(node, (cst.Import, cst.ImportFrom)):
        insert_pos = idx + 1
    elif isinstance(node, cst.SimpleStatementLine) and isinstance(node.body[0], cst.Expr) and isinstance(node.body[0].value, cst.SimpleString) and insert_pos == 0:
        insert_pos = idx + 1

# Safely insert if they don't already exist
existing_imports = [
    node for node in body if isinstance(node, cst.ImportFrom)
]

def has_import(tree_imports, module_path, name_val):
    for imp in tree_imports:
        if isinstance(imp.module, cst.Attribute) or isinstance(imp.module, cst.Name):
            # Check if this import handles our symbol
            for alias in getattr(imp, 'names', []):
                if getattr(alias.name, 'value', '') == name_val:
                    return True
    return False

if not has_import(existing_imports, "django.http", "HttpRequest"):
    body.insert(insert_pos, import_nodes[0])
    insert_pos += 1
if not has_import(existing_imports, "django.contrib.auth.models", "User"):
    body.insert(insert_pos, import_nodes[1])

modified_module = modified_module.with_changes(body=body)

with open("users/tests.py", "w", encoding="utf-8") as f:
    f.write(modified_module.code)
