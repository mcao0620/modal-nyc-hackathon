import openai

from tree_sitter import Language
import graphviz as gv
import ast
from tree_sitter import Parser
from llama_index.chat_engine import SimpleChatEngine 

from llama_index.agent import OpenAIAgent
from llama_index.tools.function_tool import FunctionTool

import os

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.environ["OPENAI_API_KEY"]


# Parse AST
filepath = 'indexer.py'
f_contents = None
with open(filepath, 'r') as f:
    f_contents = f.read()
ast_tree = ast.parse(f_contents)  
  

ast_index = {}
# Index by file name
ast_index[filepath] = ast_tree

# Index symbols
for node in ast.walk(ast_tree):
    if isinstance(node, ast.FunctionDef):
        ast_index[node.name] = node
    elif isinstance(node, ast.ClassDef):
        ast_index[node.name] = node

print(ast_index)

class PrintNodeVisitor(ast.NodeVisitor):
    def generic_visit(self, node):
        print(f"Node type: {type(node).__name__}")
        print(f"Node info: {ast.dump(node)}")
        super().generic_visit(node)

# output_string = ""
# for key, node in ast_index.items():
#     output_string += f"{key}: {type(node).__name__}\n"

# print(output_string)

# # Create a custom tool. Type annotations and docstring are used for the
# # tool definition sent to the Function calling API.
# def visit_ast_node(key) -> int:
#     """
#     Adds the two numbers together and returns the result.
#     """
#     node = ast_index.get(key)
#     if node:
#         visitor = PrintNodeVisitor()
#         visitor.visit(node)
#     else:
#         print(f"No node found for key: {key}")

# # Use the get_ast_node_by_name function
# node_name = 'foo'  # Replace with the actual node name
# visit_ast_node(node_name)

# visit_function_tool = FunctionTool.from_defaults(fn=visit_ast_node)

graph = gv.Digraph(format='png')
def visualize_node(node, parent=None):
    """
    Visualize a node in the AST

    Parameters
    ----------
    node : ast.AST
        The node to visualize
    parent : str
        The name of the parent node
    """
    if isinstance(node, ast.FunctionDef):
        graph.node(node.name, shape='box', color='blue', label=f'Function: {node.name}')
        if parent:
            graph.edge(parent, node.name, color='blue')

    elif isinstance(node, ast.ClassDef):
        graph.node(node.name, shape='ellipse', color='green', label=f'Class: {node.name}')
        if parent:
            graph.edge(parent, node.name, color='green')
    
    for child in ast.iter_child_nodes(node):
        parent_name = node.name if hasattr(node, 'name') else None
        visualize_node(child, parent_name)

def visualize_file(ast_index):
    """
    Visualize all nodes in the file

    Parameters
    ----------
    ast_index : dict
        The index of the AST nodes
    """
    for key, node in ast_index.items():
        visualize_node(node)

visualize_file(ast_index)
graph.render('output')

# visualize_node_tool = FunctionTool.from_defaults(fn=visualize_node)

# tools = [visit_function_tool, visualize_node_tool]
# agent = OpenAIAgent.from_tools(tools, verbose=True)

# # use agent
# agent.chat(f"Here are the nodes in the index: {output_string}. Please think about what the user is trying to understand and please select one to visualize.")



"""


Given:

- User's bug, request for changes, or new feature request
- User's code, semantically retrieved from their bug report/request
- User's code's AST

Goal:
- Generate a list of possible changes to the user's code that would fix their bug,
fulfill their request, or implement their feature request
- Generate a visualization of the user's code's AST that highlights the changes
- Annotate the visualization with instructions on how to make the changes to the diagrams.

Do this using a AI chatbot that can be trained to understand the user's request and
generate the changes and visualization.
The agent will annotate the visualization with instructions on how to make the changes.

"""