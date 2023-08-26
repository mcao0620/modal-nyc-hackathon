from llama_index import Document
from llama_index.node_parser import SimpleNodeParser
from llama_index.text_splitter import CodeSplitter

text_splitter = CodeSplitter(
    language="python",
    chunk_lines=40,
    chunk_lines_overlap=15,
    max_chars=1500,
)

node_parser = SimpleNodeParser.from_defaults(text_splitter=text_splitter)

def foo():
    print('hello world')

# nodes = node_parser.get_nodes_from_documents(
#     documents=[
#         Document(text="def foo():\n    print('hello world')\n\nfoo()")
#     ],
#     show_progress=True,
# )

# print(nodes[0].text)
