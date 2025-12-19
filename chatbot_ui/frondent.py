import streamlit as st  
from backend import chatbot, retrive_all_threads
from langchain_core.messages import HumanMessage
import uuid


#***************** Utility Functions ***************************

def generate_thred_id():
    return str(uuid.uuid4())

def reset_chat():
    thred_id = generate_thred_id()
    st.session_state['thred_id'] = thred_id
    add_thred(st.session_state['thred_id'])
    st.session_state['messages_history'] = []

def add_thred(thred_id):
    if thred_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thred_id)

def load_con(thred_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thred_id}})
    values = state.values

    # Try to get messages safely
    messages = values.get("messages", [])  # fallback to empty list

    temp_messages = []
    for message in messages:
        if isinstance(message, HumanMessage):
            role = "user"
        else:
            role = "assistant"
        temp_messages.append({"role": role, "content": message.content})
    return temp_messages


#***************** Session Setup ***************************

if "messages_history" not in st.session_state:
    st.session_state["messages_history"] = []

if "thred_id" not in st.session_state:
    st.session_state["thred_id"] = generate_thred_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrive_all_threads()

add_thred(st.session_state["thred_id"])

#***************** Sidebar UI ***************************

st.sidebar.title("ChatBot")
if st.sidebar.button("NEW CHAT"):
    reset_chat()  

st.sidebar.header("My Conversations")
for idx, thred_id in enumerate(st.session_state["chat_threads"], start=1):
    conv = load_con(thred_id)
    if conv:
        preview = next((m["content"] for m in conv if m["role"] == "user"), "")
        label = f"Chat {idx}: {preview[:25]}..."
    else:
        label = f"Chat {idx}"
    
    if st.sidebar.button(label, key=thred_id):
        st.session_state["thred_id"] = thred_id
        st.session_state["messages_history"] = conv


#***************** Chat Window ***************************

for mes in st.session_state["messages_history"]:
    with st.chat_message(mes["role"]):
        st.text(mes["content"])

user_input = st.chat_input("Type here.......") 
if user_input:
    # Save user input
    st.session_state["messages_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    config = {"configurable": {"thread_id": st.session_state["thred_id"]}}

    # Stream assistant response
    def stream_generator():
        for message_chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="messages"
        ):
            yield message_chunk.content

    with st.chat_message("assistant"):
        ai_mes = st.write_stream(stream_generator())

    # Save assistant reply
    st.session_state["messages_history"].append({"role": "assistant", "content": ai_mes})
