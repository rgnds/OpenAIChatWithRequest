from openai_chat import *

key = None
with open("key.txt","r",encoding="utf-8") as f:
    key = f.read().strip()
client = OpenAI(api_key=key,base_url="https://api.deepseek.com/")

for piece in client.chat.create(
    model = "deepseek-chat",
    stream = True,
    messages = [{"role": "user", "content": "用三个词形容苹果公司"}]
):
    print(piece, end="" ,flush=True)
    # print()