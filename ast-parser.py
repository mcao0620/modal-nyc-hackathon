import os
import ast
import json
from astroid import TypeInferenceVisitor, InferenceError
from tree_sitter import Language, Parser


class UnifiedASTVisitor(ast.NodeVisitor):
    def __init__(self, tree_sitter_ast):
        self.dependencies = []
        self.function_calls = []
        self.decorators = []
        self.anti_patterns = []
        self.control_flow = []
        self.variable_types = {}
        self.tree_sitter_ast = tree_sitter_ast

    def visit_Import(self, node):
        for alias in node.names:
            self.dependencies.append(alias.name)

    def visit_ImportFrom(self, node):
        self.dependencies.append(node.module)

    def visit_Call(self, node):
        self.function_calls.append(node.func.id if isinstance(node.func, ast.Name) else '')

    def visit_FunctionDef(self, node):
        self.decorators.extend(d.id for d in node.decorator_list if isinstance(d, ast.Name))
        self.control_flow.append(node)

    def visit_ClassDef(self, node):
        self.decorators.extend(d.id for d in node.decorator_list if isinstance(d, ast.Name))
        self.control_flow.append(node)

    def visit_While(self, node):
        self.control_flow.append(node)

    def visit_For(self, node):
        self.control_flow.append(node)

    def visit_If(self, node):
        self.control_flow.append(node)

    def visit_TryExcept(self, node):
        self.control_flow.append(node)

    def visit_ListComp(self, node):
        self.control_flow.append(node)

    def visit_SetComp(self, node):
        self.control_flow.append(node)

    def visit_With(self, node):
        self.control_flow.append(node)

    def visit_Assign(self, node):
        inferer = TypeInferenceVisitor()
        try:
            inferer.visit(node)
            self.variable_types[node.targets[0].id] = inferer.result or 'Mixed'
        except InferenceError:
            self.variable_types[node.targets[0].id] = 'Mixed'

    def generic_visit(self, node):
        # Map Python ast nodes to equivalent Tree-sitter nodes
        tree_sitter_node = self.tree_sitter_ast.get_node(node)
        if tree_sitter_node:
            # Extract additional nodes only in Tree-sitter AST
            self.control_flow.append(tree_sitter_node)
        super().generic_visit(node)

def normalize_asts(asts, tree_sitter_asts):
    normalized = []
  
    for ast_tree, tree_sitter_ast in zip(asts, tree_sitter_asts):
        dict = {}
        docstrings = {}
        imports = []
        control_flow = []
        variable_types = {}
        visitor = UnifiedASTVisitor(tree_sitter_ast)
        visitor.visit(ast_tree)
        for node in ast.walk(ast_tree):
            dict[node.__class__.__name__] = {
                'lineno': getattr(node, 'lineno', None),
                'col_offset': getattr(node, 'col_offset', None),
                'name': getattr(node, 'name', None),
                'parent_class': getattr(node, 'parent', None),
                'constants': [n.s for n in ast.walk(node) if isinstance(n, ast.Constant)],
                'decorators': [d.id for d in getattr(node, 'decorator_list', []) if isinstance(d, ast.Name)],
                'control_flow': control_flow,
                'variable_types': variable_types
            }
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                docstrings[node.name] = ast.get_docstring(node)
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
        dict['docstrings'] = docstrings
        dict['imports'] = imports
        normalized.append(dict)

    return normalized

def parse_to_ast(file_path):
    with open(file_path, 'r') as f:
        contents = f.read()
    try:
        return ast.parse(contents), Parser().parse(contents.encode())
    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
        return None, None

def ast_to_json(ast_dict, output_dir, filename):
    json_content = json.dumps(ast_dict, indent=4)
    with open(os.path.join(output_dir, f"ast_{filename}.json"), 'w') as f:
        f.write(json_content)

def parse_dir(dir_path, output_dir):
    asts = []
    tree_sitter_asts = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                ast_tree, tree_sitter_ast = parse_to_ast(full_path)
                if ast_tree and tree_sitter_ast:
                    normalized_ast = normalize_asts([ast_tree], [tree_sitter_ast])
                    ast_to_json(normalized_ast, output_dir, file)
                    asts.append(ast_tree)
                    tree_sitter_asts.append(tree_sitter_ast)
    return asts, tree_sitter_asts
