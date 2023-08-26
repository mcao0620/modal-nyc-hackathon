import streamlit as st
import requests
import json
import os
import random
import time

from local import run

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


def respond(response, new_question_state):


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
    st.session_state.question_state = new_question_state


if "question_state" not in st.session_state:
    if user_input := st.chat_input("https://"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Display user message in chat message container
        with st.chat_message("assistant"):
            response = "Okay, one moment..." 
            st.session_state.messages.append({"role": "assistant", "content": response}) 
            st.markdown(response) 

        with st.chat_message("user"):
            st.markdown(user_input) 
            st.session_state.url = user_input
            respond("Please describe the changes you would like to make:", "QUERY_CONTEXT")
            run(st.session_state.url)

elif st.session_state.question_state == "QUERY_CONTEXT":
    if user_input := st.chat_input("What's going on?"):
        respond("What next?", "QUERY_NEXT")
        # st.session_state.question_state = ""

elif st.session_state.question_state == "QUERY_NEXT":
    if user_input := st.chat_input("What next?"):
        pass
