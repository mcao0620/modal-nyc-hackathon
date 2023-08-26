#Ok, have json of data model and pickled networkx graph
# Graph Builder: SimpleASTGraphBuilder(repo_url, token_counter)
#     # build_graph(self,path): -> nx.Graph #.gpickle
# Graph Neighbor Hit: GraphNeighborHit
    # get_neighbor_chunks(self, code_chunk, code_chunks, neighbor_depth = 1)
# Vector Hit: VectorHit(document_json_path)
    # get_query_chunks(self, query,top_k = 3)
    # get_similar_chunks(self, code_chunk, top_k = 3)
from indexer import VectorHit
from graph_parser import GraphNeighborHit
import os
import openai
openai.api_key = os.environ["OPENAI_API_KEY"]
import numpy as np
import tiktoken
# Fill it in locally 5:20
# test 5:30
# Modalize the context grabber: 6:00

def get_inference(sys_prompt,user_prompt):
    messages = []
    messages.append({"role": "system", "content": sys_prompt})
    messages.append({"role": "user", "content": user_prompt})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    return completion["choices"][0]["message"]["content"]

class ContextGrabber:
    def __init__(self,graph_path,doc_path) -> None:
        self.GNH = GraphNeighborHit(graph_path)
        self.VH = VectorHit(doc_path)
        self.structured_query = None
        self.semantically_similar_chunks = None
        self.graph_neighbor_chunks = None
        self.all_chunks = None
        self.all_scores = None
        self.selected_chunks = None
    
    def get_chunk_context_chunks(self):
        self.graph_neighbor_chunks = []
        for chunk in self.semantically_similar_chunks:
            self.graph_neighbor_chunks.extend(self.GNH.get_neighbor_chunks(chunk,self.VH.doc_lists))

    def get_query_match_chunks(self,structured_query,top_k = 3):
        self.semantically_similar_chunks = self.VH.get_query_chunks(structured_query,top_k)
    
    def truncate_source(self,source_text):
        encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
        bits = source_text.split(" ")
        truncated_source = ""
        while len(encoder.encode(truncated_source)) < 2000 and len(bits) > 0:
            truncated_source += bits.pop(0) + " "
        return truncated_source



    def structure_context_hit_query(self,issue_title,issue_metadata):
        #human_query
        #keyword search for issue metadata
        kws = issue_title.split(" ") +  issue_metadata.split(" ")
        kw_chunks = []

        for kw in kws:
            for doc in self.VH.doc_lists:
                if kw in doc:
                    kw_chunks.append(doc)
        u_chunks = list(set(kw_chunks))
        chunks_string = self.truncate_source("\n".join(u_chunks))
        structure_sys_prompt = """
        You are an staff software engineer at Google. You're one of the best coders alive, and are an expert at navigating ambiguity. A product manager with an uncertain amount of technical experience has asked you to flesh out a ticket specification"""+"You will be given a description of the issue and some code snippets which may or may not be related to the issue. You must construct a technical specification from the available information. Keep it concise, and draw from the code sources whenever possible, including the relevant snippet sections."
        structure_user_prompt = """
        Issue description: """+issue_title + """\n\n Code Snippets: """+chunks_string + "\n\n Your technical specification: "

        query = get_inference(structure_sys_prompt,structure_user_prompt)
        self.structured_query = query

    def score_contex_chunks(self):
        self.all_scores = []
        sys_prompt = """
        You are an staff software engineer at Google. You're one of the best coders alive, and are an expert at navigating ambiguity."""+ """You are given trying to help a junior engineer complete a task. You will be given a technical specification corresponding to that task, and a code snippet which may or may not be related to the task. Think step by step about the extent to which the code snippet is relevant to the task and must be attended to by the engineer completing the spec. Then, respond with an integer score from 0 to 10 that represents the extent to which you believe the snippet is relevant. Do NOT respond with anything other than an integer."""
        for chunk in self.all_chunks:
            user_prompt = """
            Technical specification: """+self.structured_query + """\n\n Code snippet: """+chunk + """\n\n Score: """
            score = get_inference(sys_prompt,user_prompt)
            if type(score) == int:
                self.all_scores.append(score)
            elif score in ["0","1","2","3","4","5","6","7","8","9","10"]:
                self.all_scores.append(int(score))
            else:
                self.all_scores.append(0)
        
        #either get top 5 or all above 7, whichever is more
        self.selected_chunks = []

        if len([s for s in self.all_scores if s > 7]) > 5: #get above 7
            for i in range(len(self.all_scores)):
                if self.all_scores[i] > 7:
                    self.selected_chunks.append(self.all_chunks[i])
        else: #get top 5
            end = np.min([5,len(self.all_scores)])
            self.selected_chunks.extend([self.all_chunks[i] for i in sorted(range(len(self.all_scores)), key=lambda i: self.all_scores[i])[-end:]])

    def compose_response(self,query):
        #get additional context if useful
        response_sys_prompt = """
        You are an expert software engineer turned project manager at Google. You're the best alive at both roles. You are trying to create a task ticket for a task that will help a junior engineer complete the task as rapidly and thoroughly as possible. You will be given a preliminary technical specification and some code snippets from the codebase that pertain to the task. \n"""+""" You will respond with a complete ticket. Break down the problem into step-by-step subtasks. For each subtask, describe the subtask, provide an estimated priority score on an integer scale from 1 to 10, and then provide the code snippets that are relevant to that subtask if any.\n"""+""" Format everything in markdown. Be concise yet thorough. Do not ramble or add unnecessary information. \n
        """
        response_user_prompt = f"""
        Technical specification: {query} \n\n Code snippets: \n\n"""+self.truncate_source("\n\n".join(self.selected_chunks))
        response = get_inference(response_sys_prompt,response_user_prompt)

        #describe what needs to be done step by step
        #prioritize steps
        #give the context necessary to solve, give snippets as needed

        #return markdown response, essential context, additional context
        return response, self.selected_chunks, [chunk for chunk in self.all_chunks if chunk not in self.selected_chunks]


    def workflow(self,issue_title,issue_metadata):
        self.structure_context_hit_query(issue_title,issue_metadata)

        self.get_query_match_chunks(self.structured_query)

        self.get_chunk_context_chunks()

        self.all_chunks = list(set(self.semantically_similar_chunks + self.graph_neighbor_chunks))
        self.score_contex_chunks()

        response, selected_chunks, additional_chunks = self.compose_response(self.structured_query)
        
        return response, selected_chunks, additional_chunks