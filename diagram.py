import openai
import os
openai.api_key = os.environ["OPENAI_API_KEY"]

from tree_sitter import Language
import graphviz as gv
import ast
from tree_sitter import Parser
from llama_index.chat_engine import SimpleChatEngine 

from llama_index.agent import OpenAIAgent
from llama_index.tools.function_tool import FunctionTool


with open('.env') as f:
    for line in f:
        if line.strip():
            key, value = line.strip().split('=')
            os.environ[key] = value
openai.api_key = os.getenv("OPENAI_API_KEY")


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

# visualize_file(ast_index)
# graph.render('output')

# visualize_node_tool = FunctionTool.from_defaults(fn=visualize_node)

# tools = [visit_function_tool, visualize_node_tool]
# agent = OpenAIAgent.from_tools(tools, verbose=True)

# # use agent
# agent.chat(f"Here are the nodes in the index: {output_string}. Please think about what the user is trying to understand and please select one to visualize.")

def render_project_ticket():
    return """
<Project Ticket>
This clone repo doesn't include the depth of the repo. It only clones the first level of the repo. It should clone the entire repo.
</Project Ticket>"""
#     return """
# <Project Ticket>
# The token splitting has a bug. It splits the text into too many chunks. It should split the text into fewer chunks.
# </Project Ticket>
# """

def render_code_snippets():
    return """
<Code snippet>
def clone_repo(self):
    print("Cloning repo...")
    os.system(f"git clone {{self.repo_url}} {{self.local_repo_path}}")
</Code snippet>
"""

#     return """
# <Code snippet>
# # filepath: indexer.py 
# def split_by_token(text, tokenizer):
#     # heuristic
#     text_token_len = len(tokenizer.encode(text))
#     n_chunks = text_token_len // 8000 + 1
#     if n_chunks > 1:
#         words = text.split(" ")
#         chunk_len = len(words) // n_chunks
#         chunks = [words[i : i + chunk_len] for i in range(0, len(words), chunk_len)]
#         return [" ".join(chunk) for chunk in chunks]
#     else:
#         return [text]
# </Code snippet>
# """

def render_feedback():
    return "You did not return valid Graphviz DOT code. You included text before or after the Graphviz DOT code. Please try again."

def render_ast_nodes():
    node_name = 'split_by_token'
    node = ast_index.get(node_name)
    node_info = ""
    if node:
        visitor = PrintNodeVisitor()
        node_info = f"Node type: {type(node).__name__}\nNode info: {ast.dump(node)}"
        visitor.visit(node)
    else:
        print(f"No node found for key: {node_name}")

    return f"""
<AST nodes>
{node_info}
</AST nodes>
"""

prompt = f"""
You're an AI chatbot that creates visualizations using Graphviz DOT code.

You're job, is to visualize the changes needed for a user's bug report, request for changes, or new feature request, Basically a Project Ticket. 

Here is the :
{render_project_ticket()}

Here are are the most relevant files and code snippets:
{render_code_snippets()}

Here are the AST nodes in the index that occur in the code snippets:
{render_ast_nodes()}


You're job is to generate Graphviz DOT code that visualizes the changes needed to the user's code to fix their bug, fulfill their request, or implement their feature request.
Generate Graphviz DOT code by looking at provided ticket, code and AST and adding nodes, edges, comments and other information to represent the changes needed. For example:
digraph G {{
    UserClass [shape=box]
    NewFeatureClass [shape=ellipse]
    UserClass -> NewFeatureClass [label="implements"] 
}}

Notes:
- Only output valid DOT code
- Please include as much information as possible to help the user understand the changes needed.
- Please include instructions on how to make the changes to the code.
- Please include a visualization of the AST that highlights the changes.
- Use colors to highlight the changes.
- Use shapes to highlight the changes.
- Use labels to highlight the changes.
- Use arrows to highlight the changes.

<Feedback from user>
{render_feedback()}
</Feedback from user>

<Example outputs>
digraph G {{
    graph [pad="0.5", nodesep="0.5", ranksep="2"];
    node [shape=box];
    struct1 [label="split_by_token function | Adjust the behavior of n_chunks and chunk_len", fillcolor=lightblue, style=filled];
    struct2 [label="n_chunks calculation | Add a different logic to reduce chunks", fillcolor=yellow, style=filled];
    struct3 [label="chunk_len calculation | Modify logic based on the new n_chunks", fillcolor=yellow, style=filled];
    struct4 [label="chunks list comprehension | No changes required", fillcolor=green, style=filled];
    struct5 [label="Returns | No changes required", fillcolor=green, style=filled];
    struct1 -> struct2;
    struct2 -> struct3;
    struct3 -> struct4;
    struct4 -> struct5;
    label = "\n\nFlowchart of the changes needed on split_by_token function in indexer.py to fix the bug with token splitting.\n\nYellow: Code adjustment suggested\nGreen: No changes needed";
    fontsize = 28;
}}
</Example output>

Finally your out must be valid, parseable Graphviz DOT code. It may not incldue any text before or after the graphviz code.
"""

print(prompt)
out = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{'role': 'user', 'content': prompt.strip()}],
    max_tokens=2000,
)

parsed_content = out['choices'][0]['message']['content']
print(parsed_content)


print(parsed_content)
with open('output.dot', 'w') as f:
    f.write(parsed_content)
os.system('dot -Tpng output.dot -o output.png')



# """
# Given:

# - User's bug, request for changes, or new feature request
# - User's code, semantically retrieved from their bug report/request
# - User's code's AST

# Goal:
# - Generate a list of possible changes to the user's code that would fix their bug,
# fulfill their request, or implement their feature request
# - Generate a visualization of the user's code's AST that highlights the changes
# - Annotate the visualization with instructions on how to make the changes to the diagrams.

# Do this using a AI chatbot that can be trained to understand the user's request and
# generate the changes and visualization.
# The agent will annotate the visualization with instructions on how to make the changes.

# """