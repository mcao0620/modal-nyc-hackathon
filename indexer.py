# Use OpenAI API to create embeddings

import json
import openai
import tiktoken

import os
from dataclasses import asdict
from llama import node_parser
from llama_index import Document

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
        # this gets the file contents
        for root, _, files in os.walk(self.local_repo_path):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
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
        embedding_response = openai.Embedding.create(
            input=chunk_contents,
            model="text-embedding-ada-002",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        embeddings = [emb["embedding"] for emb in embedding_response["data"]]

        documents = [
            CodeChunk(path=path, chunk_contents=contents, embedding=emb)
            for path, contents, emb in zip(chunk_paths, chunk_contents, embeddings)
        ]
        # return document dataclasses
        return documents

    def store_chunks_to_disk(self, documents):
        print("Storing chunks to disk...")
        json_data = json.dumps([asdict(doc) for doc in documents])
        with open("documents.json", "w") as json_file:
            json_file.write(json_data)

    def index_repo(self):
        self.clone_repo()
        documents = self.create_embeddings()
        self.store_chunks_to_disk(documents)


if __name__ == "__main__":
    token_counter = tiktoken.encoding_for_model("gpt-3.5-turbo")
    indexer = SimpleRepoIndexer(
        "https://github.com/spcl/graph-of-thoughts", token_counter
    )
    indexer.index_repo()
