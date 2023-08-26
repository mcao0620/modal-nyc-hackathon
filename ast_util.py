import ast
from ast import NodeVisitor
import json
import os


class ASTEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ast.AST):
            return obj.__dict__
        return super().default(obj)

class ASTVisitor(NodeVisitor):
    def __init__(self):
        self.nodes = {}
        
    def visit(self, node):
        self.generic_visit(node)
        
        self.nodes[node.__class__.__name__] = node.__dict__ 

        
def ast_to_dict(ast_tree):
    visitor = ASTVisitor()
    visitor.visit(ast_tree)
    return visitor.nodes

def ast_to_json(ast_dict, output_dir, filename):
    json_content = json.dumps(ast_dict, indent=4, cls=ASTEncoder)
    with open(os.path.join(output_dir, f"ast_{filename}.json"), 'w') as f:
        f.write(json_content)
        
def parse_to_ast(file_path):
    with open(file_path, 'r') as f:
        contents = f.read()

    try:
        return ast.parse(contents)
    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
        return None

def parse_dir(dir_path, output_dir):
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                ast_tree = parse_to_ast(full_path)
                if ast_tree:
                    ast_dict = ast_to_dict(ast_tree)
                    ast_to_json(ast_dict, output_dir, file)

file_path_prefix: str = '/Users/kenneth.o/Documents/Projects/ModalHackathon/expore-tree-sitter/graph-of-thoughts/graph_of_thoughts/'

parse_dir(file_path_prefix, 'nani2')

