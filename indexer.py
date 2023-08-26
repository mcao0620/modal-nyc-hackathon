# Use OpenAI API to create embeddings
# import openai
import json
import openai
import github
import tiktoken

import os
from dataclasses import asdict

from model import CodeDocument

def get_embedding(text, model="text-embedding-ada-002"):
    embedding = openai.Embedding.create(input=text, model=model,api_key=os.getenv("OPENAI_API_KEY"))
    return embedding["data"][0]["embedding"]

def split_by_token(text,tokenizer):
    #heuristic
    text_token_len = len(tokenizer.encode(text))
    n_chunks = text_token_len // 8000 + 1
    if n_chunks > 1:
        words = text.split(" ")
        chunk_len = len(words) // n_chunks
        chunks = [words[i:i+chunk_len] for i in range(0,len(words),chunk_len)]
        return [" ".join(chunk) for chunk in chunks]
    else:
        return [text]

class SimpleRepoIndexer:
    def __init__(self, repo_url, token_counter, local_dir="/tmp"):
        #self.embedding = cohere.Client("m0G40aTscBxasUvQVsStdN3dQ4jIHUNTjj3Yd2Iv")
        self.repo_url = repo_url
        self.local_dir = local_dir
        self.repo_name = self.repo_url.split("/")[-1].replace(".git", "")
        self.local_repo_path = os.path.join(self.local_dir, self.repo_name)
        self.token_counter = token_counter

    def clone_repo(self):
        # g = github.
        # repo = g.get_repo(self.repo_url)
        print("Cloning repo...")
        os.system(f"git clone {self.repo_url} {self.local_repo_path}")

    def create_embeddings(self):
        # todo: Figure out how to stroe the file contents
        file_contents = []
        file_paths = []

        print("Extracting file contents...")
        # this gets the file contents
        for root, _, files in os.walk(self.local_repo_path):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path, "r") as f:
                        content = f.read()
                        file_contents.append(content)
                        file_paths.append(path.removeprefix(f"{self.local_repo_path}/"))
        # TODO: This isn't probably working,
        # this creates the embeddings
        print("Creating embeddings...")
        embeddings = []
        new_paths = []
        new_contents = []
        for content in file_contents:
            fragments = split_by_token(content,self.token_counter)
            for fragment in fragments:
                embeddings.append(get_embedding(fragment))
                new_paths.append(path)
                new_contents.append(fragment)
        documents = [
            CodeDocument(path=path, file_contents=contents, embedding=emb)
            for path, contents, emb in zip(new_paths, new_contents, embeddings)
        ]
        # return document dataclasses
        return documents

    def store_docs_to_disk(self, documents):
        json_data = json.dumps([asdict(doc) for doc in documents])
        with open("documents.json", "w") as json_file:
            json_file.write(json_data)

    def index_repo(self):
        self.clone_repo()
        documents = self.create_embeddings()
        self.store_docs_to_disk(documents)


if __name__ == "__main__":
    token_counter = tiktoken.encoding_for_model("gpt-3.5-turbo")
    indexer = SimpleRepoIndexer("https://github.com/spcl/graph-of-thoughts", token_counter)
    indexer.index_repo()
