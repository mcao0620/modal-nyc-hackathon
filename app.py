import streamlit as st
import requests
import json
import os
import random
import time

from local import build_documents_and_graph, run


def create_ticket(repo_url, context):
    description = """# Hello world! ```code goes here```"""
    st.text(create_linear_issue("Issue Title", description))


def create_linear_issue(title, description):
    url = "https://api.linear.app/graphql"
    headers = {
        "Authorization": "lin_api_MHmTMlrHIWG0EuMLzoQbgIdvuo31b5P4iyQws2M6",
        "Content-Type": "application/json",
        "Linear-Integration": "my_application",
    }

    query = """
    mutation CreateIssue($title: String!, $description: String!, $teamId: String!) {
      issueCreate(input: {
        title: $title,
        description: $description,
        teamId: $teamId
      }) {
        success
        issue {
          id
          title
          description
        }
      }
    }
    """

    variables = {
        "title": title,
        "description": description,
        "teamId": "1a89e221-62b3-48b7-adb4-1ddaa4875e1f",
    }

    response = requests.post(
        url, headers=headers, json={"query": query, "variables": variables}
    )

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return f"Failed to create issue. Status code: {response.status_code}, Error: {response.text}"


def query_relevant_code(repo_url, context):
    if repo_url != "https://github.com/spcl/graph-of-thoughts":
        st.error("Sorry, I can't access that repo.")
    st.text(context)


# App body
st.header("Codebase-Aware Ticket Enrichment")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "What GitHub repo are you working on?",
        }
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def add_user_input(user_input):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)


def respond(response):
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = response
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})


prompt_input = st.chat_input("Type here")
if prompt_input:
    add_user_input(prompt_input)
    if "question_state" not in st.session_state:
        respond("Okay, one moment...")
        build_documents_and_graph(prompt_input)
        respond("Please describe the changes you would like to make:")
        st.session_state.question_state = "QUERY_ISSUE"
    elif st.session_state.question_state == "QUERY_ISSUE":
        st.session_state.issue_title = prompt_input
        respond("What metadata or entities are helpful/relevant to this change?")
        st.session_state.question_state = "QUERY_METADATA"
    elif st.session_state.question_state == "QUERY_METADATA":
        respond("Okay, one moment...")
        response, relevant_chunks, helpful_chunks = run(
            st.session_state.issue_title, prompt_input
        )
        with st.chat_message("assistant"):
            r = ""

            r += "# Helpful chunks: \n\n"
            for chunk in helpful_chunks:
                r += f"```{chunk}```"
                r += "\n\n\n"

            r += "# Relevant chunks: \n\n"
            for chunk in relevant_chunks:
                r += f"```{chunk}```"
                r += "\n\n\n"

            st.session_state.messages.append({"role": "assistant", "content": r})
            st.markdown(r)
        respond("Woo!")
        st.session_state.question_state = "CREATE_TICKET"
    elif st.session_state.question_state == "CREATE_TICKET":
        respond("You've made it to the end!")


#     user_input = st.chat_input("https://")
#     if user_input:
#         add_user_input(user_input)
#         st.session_state.url = user_input
#         st.session_state.question_state = "QUERY_REPO"

#     st.session_state.changes = st.chat_input(
#         "Please describe the changes you would like to make:"
#     )
#     if st.session_state.changes:
#         st.session_state.question_state = "QUERY_REPO"

# elif st.session_state.question_state == "QUERY_REPO":
#     if "changes" in st.session_state:
#         # INSERT PROCESSING CODE HERE
#         with st.chat_message("assistant"):
#             response = "Okay, one moment..."
#             st.session_state.messages.append({"role": "assistant", "content": response})
#             st.markdown(response)

#         build_documents_and_graph(st.session_state.url)

#         respond("Please describe the changes you would like to make:")
#         st.session_state.question_state = "QUERY_CONTEXT"

# elif st.session_state.question_state == "QUERY_CONTEXT":
#     st.text("hello")
#     user_input2 = st.chat_input("What's going on?")
#     if user_input2:
#         add_user_input(user_input2)
#         # INSERT PROCESSING CODE HERE
#         with st.chat_message("assistant"):
#             response = "Okay, one moment..."
#             st.session_state.messages.append({"role": "assistant", "content": response})
#             st.markdown(response)
#         response, relevant_chunks, helpful_chunks = run(st.session_state.url)
#         with st.chat_message("assistant"):
#             st.session_state.messages.append(
#                 {"role": "assistant", "content": relevant_chunks}
#             )
#         respond("What next?", "QUERY_NEXT")

# elif st.session_state.question_state == "QUERY_NEXT":
#     if user_input3 := st.chat_input("What next?"):
#         pass

# st.text("made it to end ")
