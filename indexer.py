# Use OpenAI API to create embeddings
# import openai
import json
import cohere
import github
import os
from dataclasses import asdict

from model import CodeDocument


class SimpleRepoIndexer:
    def __init__(self, repo_url, local_dir="/tmp"):
        self.cohere = cohere.Client("m0G40aTscBxasUvQVsStdN3dQ4jIHUNTjj3Yd2Iv")
        self.repo_url = repo_url
        self.local_dir = local_dir
        self.repo_name = self.repo_url.split("/")[-1].replace(".git", "")
        self.local_repo_path = os.path.join(self.local_dir, self.repo_name)

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
        embeddings = self.cohere.embed(file_contents).embeddings
        documents = [
            CodeDocument(path=path, file_contents=contents, embedding=emb)
            for path, contents, emb in zip(file_paths, file_contents, embeddings)
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
    indexer = SimpleRepoIndexer("https://github.com/spcl/graph-of-thoughts")
    indexer.index_repo()
