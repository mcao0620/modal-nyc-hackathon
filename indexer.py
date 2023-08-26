# Use OpenAI API to create embeddings

import json
import openai
import tiktoken
from openai.embeddings_utils import cosine_similarity

import os
from dataclasses import asdict
from llama import node_parser
from llama_index import Document
import ast_util

from model import CodeChunk


def get_embeddings(text, model="text-embedding-ada-002"):
    embedding = openai.Embedding.create(
        input=text, model=model, api_key=os.getenv("OPENAI_API_KEY")
    )
    return embedding["data"][0]["embedding"]


def split_by_token(text, tokenizer):
    # heuristic
    text_token_len = len(tokenizer.encode(text))
    n_chunks = text_token_len // 8000 + 1
    if n_chunks > 1:
        words = text.split(" ")
        chunk_len = len(words) // n_chunks
        chunks = [words[i : i + chunk_len] for i in range(0, len(words), chunk_len)]
        return [" ".join(chunk) for chunk in chunks]
    else:
        return [text]


class SimpleRepoIndexer:
    def __init__(self, repo_url, token_counter, local_dir="/tmp"):
        self.repo_url = repo_url
        self.local_dir = local_dir
        self.repo_name = self.repo_url.split("/")[-1].replace(".git", "")
        self.local_repo_path = os.path.join(self.local_dir, self.repo_name)
        self.token_counter = token_counter

    def clone_repo(self):
        print("Cloning repo...")
        os.system(f"git clone {self.repo_url} {self.local_repo_path}")

    def create_embeddings(self):
        # todo: Figure out how to stroe the file contents
        chunk_contents = []
        chunk_paths = []

        print("Extracting file contents...")
        print("Creating ASTs...")
        ast_dicts = []
        # this gets the file contents
        for root, _, files in os.walk(self.local_repo_path):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    print("Creating AST for file:", path)
                    ast_tree = ast_util.parse_to_ast(path)
                    if ast_tree:
                        ast_dict = ast_util.ast_to_dict(ast_tree)
                        #print(ast_dict)
                        ast_dicts.append(ast_dict)
                    with open(path, "r") as f:
                        content = f.read()
                        # file_contents.append(content)
                        chunks = node_parser.get_nodes_from_documents(
                            documents=[Document(text=content)]
                        )
                        chunk_contents.extend([chunk.text for chunk in chunks])
                        chunk_paths.extend(
                            [
                                path.removeprefix(f"{self.local_repo_path}/")
                                for _ in range(len(chunks))
                            ]
                        )

        print("Creating embeddings...")
        print("NANI")
        print(os.getenv("OPENAI_API_KEY"))
        embedding_response = openai.Embedding.create(
            input=chunk_contents,
            model="text-embedding-ada-002",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        
        embeddings = [emb["embedding"] for emb in embedding_response["data"]]


        documents = [
            CodeChunk(path=path, chunk_contents=contents,
                      embedding=emb, ast_dict=ast_dict)
            for path, contents, emb, ast_dict 
            in zip(chunk_paths, chunk_contents, embeddings, ast_dicts)
        ]
        # return document dataclasses
        return documents

    def store_chunks_to_disk(self, documents):
        print("Storing chunks to disk...")
        json_data = json.dumps([asdict(doc) for doc in documents], cls=ast_util.ASTEncoder)
        with open("documents.json", "w") as json_file:
            json_file.write(json_data)

    def index_repo(self):
        self.clone_repo()
        documents = self.create_embeddings()
        self.store_chunks_to_disk(documents)

class VectorHit:
    def __init__(self, document_json_path):
        with open(document_json_path, "r") as json_file:
            self.documents = json.load(json_file)
        self.doc_lists = [doc["chunk_contents"] for doc in self.documents]
        self.embeddings = [doc["embedding"] for doc in self.documents]
        self.paths = [doc["path"] for doc in self.documents]
    
    def _cosine_sim(self, a, b):
        return cosine_similarity(a, b)
    
    def get_query_chunks(self, query,top_k = 3):
        query_embedding = get_embeddings(query)
        sims = []
        for i in range(len(self.doc_lists)):
            sims.append(self._cosine_sim(query_embedding, self.embeddings[i]))
        
        top_k_indices = sorted(range(len(sims)), key=lambda i: sims[i])[-top_k:]
        return [self.doc_lists[i] for i in top_k_indices]

    def get_similar_chunks(self, code_chunk, top_k = 3):
        chunk_idx = self.doc_lists.index(code_chunk)
        chunk_embedding = self.embeddings[chunk_idx]
        sims = []
        for i in range(len(self.doc_lists)):
            sims.append(self._cosine_sim(chunk_embedding, self.embeddings[i]))
        
        top_k_indices = sorted(range(len(sims)), key=lambda i: sims[i])[-top_k:]
        return [self.doc_lists[i] for i in top_k_indices]


if __name__ == "__main__":
    token_counter = tiktoken.encoding_for_model("gpt-3.5-turbo")
    indexer = SimpleRepoIndexer(
        "https://github.com/spcl/graph-of-thoughts", token_counter
    )
    indexer.index_repo()
