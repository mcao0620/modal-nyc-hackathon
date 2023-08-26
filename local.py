import os

with open('.env') as f:
    for line in f:
        if line.strip():
            key, value = line.strip().split('=')
            os.environ[key] = value
from retrieval_tool import ContextGrabber
import tiktoken
from graph_parser import SimpleASTGraphBuilder
from indexer import SimpleRepoIndexer
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

#build documents.json
if not os.path.exists("documents.json"):
    token_counter = tiktoken.encoding_for_model("gpt-3.5-turbo")
    indexer = SimpleRepoIndexer(
        "https://github.com/spcl/graph-of-thoughts", token_counter
    )
    indexer.index_repo()
if not os.path.exists("graph.gml"):
    token_counter = tiktoken.encoding_for_model("gpt-3.5-turbo")
    graph_builder = SimpleASTGraphBuilder("https://github.com/spcl/graph-of-thoughts", token_counter)
    graph_builder.build_graph("graph.gml")

cg = ContextGrabber("graph.gml","documents.json")

issue_title = "Get response and input token costs from OpenAI website via a webcrawler, using the model id."
issue_metadata = "prompt_token_cost, response_token_cost, model_id, ChatGPT(AbstractLanguageModel)"

try:
    response, relevant_chunks, helpful_chunks = cg.workflow(issue_title,issue_metadata)
    print(f"Workflow executed successfully. Response: {response}, Relevant Chunks: {relevant_chunks}, Helpful Chunks: {helpful_chunks}")
except Exception as e:
    print(f"Error executing workflow: {str(e)}")


