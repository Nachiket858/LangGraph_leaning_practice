from langgraph.graph import StateGraph, START,END
from typing import TypedDict ,Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import  SqliteSaver
import sqlite3


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash",
                               api_key=api_key)


# define state

class ChatState(TypedDict): 
    messages : Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState) -> ChatState:
    messages  =  state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}


conn = sqlite3.connect(database="chatbot.db",check_same_thread=False)
checkpoint = SqliteSaver(conn)

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)



chatbot  =  graph.compile(checkpointer=checkpoint)



# test
# config = {"configurable": {"thread_id":"1" }}
# res= chatbot.invoke({"messages": [HumanMessage(content="my name ")]},

#             config=config,

#         )
# print(res)
def retrive_all_threads():
    all_threads =  set()
    for check in checkpoint.list(None):
        all_threads.add(check.config['configurable']['thread_id'])
    return list(all_threads)


