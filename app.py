
import os
import gradio as gr

from dotenv import load_dotenv
from openai import OpenAI

from tools import tools, handle_tool_calls
from styles import CSS, JS, EXAMPLES
from context import TWIN_SYSTEM_PROMPT

# Load .env locally; Render uses environment variables
load_dotenv()

MODEL_NAME = "gpt-5.4-nano"

openai = OpenAI()

system = [
    {
        "role": "system",
        "content": TWIN_SYSTEM_PROMPT
    }
]


def chat(message, history):
    messages = system + history + [
        {"role": "user", "content": message}
    ]

    response = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools
    )

    while response.choices[0].finish_reason == "tool_calls":
        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls

        results = handle_tool_calls(tool_calls)

        messages.append(assistant_message)
        messages.extend(results)

        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools
        )

    return response.choices[0].message.content


if __name__ == "__main__":

    demo = gr.ChatInterface(
        fn=chat,
        examples=EXAMPLES,
        title="Digital Twin",
        description="Talk to my AI twin about my career",
        chatbot=gr.Chatbot(show_label=False),
    )

    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        share=False,
        css=CSS,
        js=JS,
        theme=gr.themes.Base()
    )
