import streamlit as st
from app.qa_bot import qa_chain  # directly import the chain for streaming
from langchain_core.messages import AIMessage, HumanMessage

# Page config
st.set_page_config(page_title="Nurse QA Bot", page_icon="🩺", layout="wide")

# Session state for chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🩺 Friendly Nurse QA Assistant")
st.markdown("Ask anything about your health and get kind, simple responses.")

question = st.chat_input("💬 Ask your question")

if question:
    # Show user message
    st.session_state.chat_history.append(HumanMessage(content=question))
    with st.chat_message("user"):
        st.markdown(question)

    # Stream the response
    with st.chat_message("assistant"):
        stream = qa_chain.stream({"query": question})
        full_response = ""
        response_area = st.empty()

        for chunk in stream:
            token = chunk.get("result", "")
            full_response += token
            response_area.markdown(full_response + "▌")

        # Add final assistant message
        st.session_state.chat_history.append(AIMessage(content=full_response))
        response_area.markdown(full_response)

# Display all previous chat
for msg in st.session_state.chat_history:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content)
