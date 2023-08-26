import os

import ast
import networkx as nx

import re

class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.graph = nx.DiGraph()
        self.current_function = None
        self.instantiated_classes = {}

    def visit_FunctionDef(self, node):
        if self.current_function is None:  # Only top-level functions are added as nodes directly
            self.current_function = node.name
            self.graph.add_node(self.current_function)
        self.generic_visit(node)
        if self.current_function == node.name:  # Only set to None if it's top-level to avoid affecting nested functions
            self.current_function = None

    def visit_ClassDef(self, node):
        # Treat methods inside classes
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.visit(item)

    def visit_Assign(self, node):
        # Capture class instantiations
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            class_name = node.value.func.id
            #variable_name = node.targets[0].id
            if isinstance(node.targets[0], ast.Name):
                variable_name = node.targets[0].id
            elif isinstance(node.targets[0], ast.Subscript):
                # Handle the subscript target appropriately.
                # Depending on your needs, you can extract the value or slice or just ignore it.
                variable_name = None  # or however you wish to handle subscripts
            else:
                # Handle other types of assignment targets or just skip them.
                variable_name = None
            self.instantiated_classes[variable_name] = class_name
            if self.current_function:
                self.graph.add_edge(self.current_function, class_name)
        self.generic_visit(node)

    def visit_Call(self, node):
        # Capture simple function calls
        if isinstance(node.func, ast.Name):  
            called_function = node.func.id
            if self.current_function:
                self.graph.add_edge(self.current_function, called_function)
        
        elif isinstance(node.func, ast.Attribute):  # for methods or attribute calls
            method = node.func.attr
            obj_name = None

            if isinstance(node.func.value, ast.Name):  # direct obj method call
                obj_name = node.func.value.id
            
            if obj_name in self.instantiated_classes:
                class_name = self.instantiated_classes[obj_name]
                method_name = f"{class_name}.{method}"
                if self.current_function:
                    self.graph.add_edge(self.current_function, method_name)
        self.generic_visit(node)

def generate_function_graph(code):
    tree = ast.parse(code)
    visitor = FunctionCallVisitor()
    visitor.visit(tree)
    return visitor.graph

class SimpleASTGraphBuilder:
    def __init__(self, repo_url, token_counter, local_dir="/tmp"):
        self.repo_url = repo_url
        self.local_dir = local_dir
        self.repo_name = "placeholder"#self.repo_url.split("/")[-1].replace(".git", "")
        self.local_repo_path = os.path.join(self.local_dir, self.repo_name)
        self.token_counter = token_counter

    # this is actually used!
    def build_graph(self, path):
        self._get_stringified_repo()
        self.ast_graph =  generate_function_graph(self.repo_string)
        self.save_graph(path)
    
    def save_graph(self, path):
        nx.write_gml(self.ast_graph, path)

    def _get_stringified_repo(self):
        repo_string = ""
        for root, _, files in os.walk(self.local_repo_path):
                for file in files:
                    if file.endswith(".py"):
                        path = os.path.join(root, file)
                        with open(path, "r") as f:
                            content = f.read()
                            repo_string += content
        self.repo_string = repo_string

class GraphNeighborHit:
    def __init__(self, graph_path):
        self.load_graph(graph_path)

    def load_graph(self, path):
        self.graph = nx.read_gml(path)

    def get_neighbor_chunks(self, code_chunk, code_chunks, neighbor_depth = 1):
        neighbors = self._get_all_neighbor_names(code_chunk, depth = neighbor_depth)
        if len(neighbors) == 0:
            return []
        else:
            return self._get_chunks(neighbors, [c for c in code_chunks if c != code_chunk])

    def _get_all_neighbor_names(self, code_chunk, depth=1):
        unique_elements = list(set(code_chunk.split(" ")))
        node_names = [node for node in self.graph.nodes if node in unique_elements]
        if len(node_names) == 0:
            return []
        else:
            neighbors = []
            for node_name in node_names:
                neighbors.extend(list(self._get_neighbors(self.graph, node_name, depth=depth)))
            return neighbors
    
    def _get_chunks(self,neighbors,chunks):
        class_pattern = r'class (\w+):'
        method_pattern = r'def (\w+)\(.*\):'

        chunk_indices_for_neighbors = []
        for chunk in chunks:
            class_defs = re.findall(class_pattern, chunk)
            method_defs = re.findall(method_pattern, chunk)
            for neighbor in neighbors:
                if neighbor in class_defs or neighbor in method_defs:
                    chunk_indices_for_neighbors.append(chunks.index(chunk))
        
        return chunks[list(set(chunk_indices_for_neighbors))]

    def _get_neighbors(self,graph, node_name, depth=1):
        node = graph.nodes[node_name]
        neighbors = set()
        if depth == 0:
            return neighbors
        for neighbor in list(graph.neighbors(node)):
            print(neighbor)
            neighbors.add(neighbor)
            neighbors = neighbors.union(self._get_neighbors(graph, neighbor, depth=depth-1))
        return neighbors
        
    