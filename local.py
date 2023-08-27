import os

with open(".env") as f:
    for line in f:
        if line.strip():
            key, value = line.strip().split("=")
            os.environ[key] = value
from retrieval_tool import ContextGrabber
import tiktoken
from graph_parser import SimpleASTGraphBuilder
from indexer import SimpleRepoIndexer
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def index(url):
    token_counter = tiktoken.encoding_for_model("gpt-3.5-turbo")
    indexer = SimpleRepoIndexer(url, token_counter)
    indexer.index_repo()


def build_documents_and_graph(url):
    # build documents.json
    if not os.path.exists("documents.json"):
        index(url)

    if not os.path.exists("graph.gml"):
        token_counter = tiktoken.encoding_for_model("gpt-3.5-turbo")
        graph_builder = SimpleASTGraphBuilder(
            "https://github.com/spcl/graph-of-thoughts", token_counter
        )
        graph_builder.build_graph("graph.gml")


def run(issue_title, issue_metadata):
    cg = ContextGrabber("graph.gml", "documents.json")

    try:
        response, relevant_chunks, helpful_chunks = cg.workflow(
            issue_title, issue_metadata
        )
        print(
            f"Workflow executed successfully. Response: {response}, Relevant Chunks: {relevant_chunks}, Helpful Chunks: {helpful_chunks}"
        )
        with open("results.md", "w") as f:
            f.write(f"# Workflow Results\n")
            f.write(f"## Response\n{response}\n")
            f.write(f"## Relevant Chunks\n{relevant_chunks}\n")
            f.write(f"## Helpful Chunks\n{helpful_chunks}\n")
        return response, relevant_chunks, helpful_chunks
    except Exception as e:
        print(f"Error executing workflow: {str(e)}")
