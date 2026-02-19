import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    await cl.Message(f"Received: {message.content}").send()

@cl.on_chat_start
async def start():
    await cl.Message("✓ Chainlit UI is running with voice dependencies installed!").send()
