# from agent.llm.clients import gemini
#
# import os
# os.environ["http_proxy"] = "http://http://127.0.0.1:10809"
# os.environ["https_proxy"] = "http://http://127.0.0.1:10809"
#
# print("test langchain")
messages = [
                ("system", "Translate the user sentence to French."),
                ("human", "I love programming."),
]
#
#
# client = gemini.GeminiClient()
# res = client.get_client().invoke(messages)
# print(res)
#
import qa_chat
from petercat_utils.data_class import ChatData
from agent.bot import get_bot

input_data = ChatData(messages , "openai")

get_bot(input_data)


result = qa_chat.agent_chat(
        input_data,
        "auth_token",
        bot,
    )