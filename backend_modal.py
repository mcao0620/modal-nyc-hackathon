import modal
import os
import tiktoken
from retrieval_tool import ContextGrabber
from graph_parser import SimpleASTGraphBuilder
from indexer import SimpleRepoIndexer
import time
#from pydantic import BaseModel
from typing import Dict
stub = modal.Stub(name="example")
import openai
openai.api_key = os.environ["OPENAI_API_KEY"]


#@stub.function(timeout=60 * 5)
#@modal.web_endpoint(method="POST", label="example")
#def example(body):
    #print(body)
    #return {"message": "Hello world!"}
#class DataModel(BaseModel):
    #title: str
    #metadata: str
slack_sdk_image = modal.Image.debian_slim().pip_install("openai","tiktoken","networkx","llama_index","matplotlib","plotly","scipy","scikit-learn")#,"os","typing","tiktoken","networkx","ast","re","dataclasses","llama","llama_index"

@stub.function(timeout=60 * 5, image=slack_sdk_image,secret=modal.Secret.from_name("secret-keys"))
@modal.web_endpoint(method="POST", label="getticket")
def return_llm_output(item: Dict):
    openai.key = os.environ["OPENAI_API_KEY"]
    print(item)
    title = item["title"]
    metadata = item["metadata"]
    url = item["url"]
    if not os.path.exists("documents.json"):
        token_counter = tiktoken.encoding_for_model("gpt-3.5-turbo")
        indexer = SimpleRepoIndexer(
            url, token_counter
        )
        indexer.index_repo()
    if not os.path.exists("graph.gml"):
        token_counter = tiktoken.encoding_for_model("gpt-3.5-turbo")
        graph_builder = SimpleASTGraphBuilder(url, token_counter)
        graph_builder.build_graph("graph.gml")

    cg = ContextGrabber("graph.gml","documents.json")

    issue_title = "Get response and input token costs from OpenAI website via a webcrawler, using the model id."
    issue_metadata = "prompt_token_cost, response_token_cost, model_id, ChatGPT(AbstractLanguageModel)"

    response, relevant_chunks, helpful_chunks = cg.workflow(issue_title,issue_metadata)
    output_json = {
        "response": response,
        "relevant_chunks": relevant_chunks,
        "helpful_chunks": helpful_chunks
    }
    return output_json