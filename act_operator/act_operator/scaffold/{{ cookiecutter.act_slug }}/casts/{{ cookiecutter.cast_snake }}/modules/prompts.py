"""[Optional] Prompt templates tailored to the {{ cookiecutter.cast_name }} graph.

Guidelines:
    - Create LangChain `PromptTemplate` or LCEL prompt definitions.
    - Consume these templates from the chain/node modules.

Official document URL:
    - Messages: https://docs.langchain.com/oss/python/langchain/messages
    - OpenAI prompt engineering: https://platform.openai.com/docs/guides/prompt-engineering
    - Gemini prompt engineering: https://ai.google.dev/gemini-api/docs/prompting-strategies?hl=ko
    - Claude prompt engineering: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering
"""

# from langchain.messages import SystemMessage, HumanMessage, AIMessage


def get_sample_dictionary_format_prompt():
    # system_content = "You are a proact operator expert"
    # user_content = "Do Proactive"
    # ai_content = "I will."
    # return [
    #     {"role": "system", "content": system_content},
    #     {"role": "user", "content": user_content},
    #     {"role": "ai", "content": ai_content},
    # ]
    pass


def get_sample_messages_prompt():
    # system = "You are a proact operator expert"
    # human = "Do Proactive"
    # ai = "I will."
    # return [SystemMessage(system), HumanMessage(human), AIMessage(ai)]
    pass
