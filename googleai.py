import base64
import mimetypes
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", '')
GOOGLE_API_MODEL = os.getenv("GOOGLE_API_MODEL", '')
print(f"GOOGLE_API_KEY: {GOOGLE_API_KEY}")
print(f"GOOGLE_API_MODEL: {GOOGLE_API_MODEL}")

def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")

def generate_stream(prompt):
    client = genai.Client(
        api_key=GOOGLE_API_KEY,
    )
    model = GOOGLE_API_MODEL
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f""" {prompt}"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            # "image",
            "text",
        ],
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data:
            file_name = "ENTER_FILE_NAME"
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            print(f"data_buffer: {data_buffer}")
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            save_binary_file(f"{file_name}{file_extension}", data_buffer)
        else:
            print(chunk.candidates[0].content.parts[0].text)
            print(chunk.text)
def generate(prompt):
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY",'')
    GOOGLE_API_MODEL = os.getenv("GOOGLE_API_MODEL",'')
    print(f"GOOGLE_API_KEY: {GOOGLE_API_KEY}")
    print(f"GOOGLE_API_MODEL: {GOOGLE_API_MODEL}")
    client = genai.Client(
        api_key=GOOGLE_API_KEY,
    )
    model = GOOGLE_API_MODEL
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f""" {prompt}"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            # "image",
            "text",
        ],
        response_mime_type="text/plain",
    )
    response= client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    print(type(response),response.text)
#兼容openai

def generate_openai(prompt):
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY",'')
    client = OpenAI(
        api_key=GOOGLE_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    response = client.chat.completions.create(
        # model="gemini-2.0-flash",
        model=GOOGLE_API_MODEL,
        messages=[
            {"role": "system", "content": "你是我最好的助手，你能最好的帮我解决一切问题."},
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ]
    )

    print(response.choices[0].message.content)

if __name__ == "__main__":
    generate_openai('来时路上，风景如画')
