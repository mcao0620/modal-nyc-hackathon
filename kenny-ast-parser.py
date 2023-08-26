import os
import sys
import ast
import json
from tree_sitter import Language, Parser

# Set up tree sitter
Language.build_library(
    # Store the library in the `build` directory
    'build/my-languages.so',
    ['vendor/tree-sitter-python']
)

PY_LANGUAGE = Language('build/my-languages.so', 'python')


file_path_prefix: str = '/Users/kenneth.o/Documents/Projects/ModalHackathon/expore-tree-sitter/graph-of-thoughts/graph_of_thoughts/'


def normalize_asts(asts, tree_sitter_asts):
    normalized = []

    for ast_tree, tree_sitter_ast in zip(asts, tree_sitter_asts):
        dict = {}
        docstrings = {}
        imports = []
        control_flow = []
        variable_types = {}
        # visitor = UnifiedASTVisitor(tree_sitter_ast)
        # visitor.visit(ast_tree)
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

# def print_tree(node, indent=0):
#
#  if node.type == 'function_definition':
#    print(' ' * indent + f"FUNCTION {node.children[0].text}")
#
#  elif node.type == 'lambda_expression':
#    print(' ' * indent + "LAMBDA")
#
#  for child in node.children:
#    print_tree(child, indent + 1)


def print_tree(node, indent=0):
    print('  ' * indent + node.type)
    for child in node.children:
        print_tree(child, indent + 1)


query = PY_LANGUAGE.query("""
(function_definition
  name: (identifier) @function.def)

(call
  function: (identifier) @function.call)
""")

#captures = query.captures(tree.root_node)
#assert len(captures) == 2
#assert captures[0][0] == function_name_node
#assert captures[0][1] == "function.def"


parser = Parser()
parser.set_language(PY_LANGUAGE)


def parse_to_ast(file_path):
    with open(file_path, 'r') as f:
        contents = f.read()
    try:
        # return ast.parse(contents), Parser().parse(contents.encode())
        def read_callable(byte_offset, point):
            src = contents.encode()
            return src[byte_offset:byte_offset+1]
        tree = parser.parse(read_callable)
        #captures = query.captures(tree.root_node)
        #variable_names = []
        #for capture in captures:
        #    name = capture[0] 
        #    variable_names.append(name.text)
        #print(variable_names)

        #print_tree(tree.root_node)
        #print(ast.parse(contents))
        # print(tree.root_node.text)
        return ast.parse(contents), tree
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
                    normalized_ast = normalize_asts(
                        [ast_tree], [tree_sitter_ast])
                    print(normalized_ast)
                    ast_to_json(normalized_ast, output_dir, file)
                    asts.append(ast_tree)
                    tree_sitter_asts.append(tree_sitter_ast)
    return asts, tree_sitter_asts


ast_ast, tree_sit_ast = parse_dir(file_path_prefix, 'nani')

class CodeNode:
    name: str
    docstring: str
    children: list

print(tree_sit_ast)
print("nan")
for tree in tree_sit_ast:
    print_tree(tree.root_node)
