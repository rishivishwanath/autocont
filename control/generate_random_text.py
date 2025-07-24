import requests
from utils import get_env_var
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from supabase import create_client, Client
import json
import redis
from langchain_google_genai import ChatGoogleGenerativeAI

def gen_text(article_text):
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash",  google_api_key=get_env_var("GOOGLE_API_KEY"))


    # News anchor-style system prompt
    system_template = ( f"""
You are a creative and concise script writer specializing in short-form video content like Instagram Reels, YouTube Shorts, and TikTok videos. Your goal is to write engaging scripts that hook viewers within the first 3 seconds and deliver clear, emotionally compelling, or entertaining messages within 30 to 60 seconds.

Keep the tone punchy, conversational, virality, relatability, and attention retention.


Format your output like this,but give it as a single paragraph without any headers or stage directions:
Brief, attention-grabbing line or question (max 2 seconds) 
Main script, including pacing cues or scene shifts if needed (15–45 seconds) 
Optional call to action, funny twist, or ending remark (5–10 seconds)

Avoid long narration blocks. Focus on dynamic, scriptable lines that creators can act out or voice over.
                       
The information of the article should be conveyed in less than 30 seconds of speech and should be as interesting as possible.
                       
"""

    )

    # Build prompt and invoke model
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", article_text)
    ])

    messages = prompt_template.format_messages() 
    response = model.invoke(messages)            
    print(response.content)
    return response.content