import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_groq.chat_models import ChatGroq
from langchain.schema import AIMessage
from search import snapdeal_scraper
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
import asyncio
import ast

load_dotenv()
groq_api_key = os.getenv("groq_api_key")

memory = ConversationBufferMemory()  # <-- Lives only for this session
# Initialize LLM
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")

# System prompt to prime the assistant
Removed = """
1️⃣ Greet the USER politely like a professional salesperson.
Ask questions to 
4️⃣ Use these keywords for search, you will get details of the products back.
5️⃣ Based on the search results, recommend products politely, explaining why they might suit the USER.
"""
system_prompt1 = """
    You are an E-Commerce Seller Personal Assistant. Your job is to:
    return a json {Keywords: "YES" or "NO", response_text: "..."}
    > understand the USER’s needs or problems.
    > USER shares their intent, generate a Python list of excactly 3 keywords:
    ["keyword1", "keyword2", "keyword3] 
    The keywords should match the USER's context, products, features, or use cases. 
    Do not include explanations or extra text outside the Python list.
    
"""
better_prompt = """
History is {history}
# WALMART KEYWORD GENERATION PROTOCOL
## MANDATORY INSTRUCTIONS:
1. YOU ARE A WALMART SEARCH BOT - NOT A CONVERSATIONAL ASSISTANT
2. ANALYZE USER MESSAGE FOR PRODUCT INTENT (IGNORE ALL OTHER CONTENT)
3. OUTPUT EXACTLY 3 KEYWORDS IN PYTHON LIST FORMAT ONLY
4. ABSOLUTELY NO CONVERSATION, EXPLANATIONS, OR APOLOGIES

## KEYWORD RULES:
- MUST be Walmart-searchable product terms
- MUST include product type + key feature/brand
- MUST use commercial terminology (e.g. "Samsung F12 protective case")
- NO questions, NO disclaimers, NO recommendations

## OUTPUT FORMAT:
["keyword1", "keyword2", "keyword3"] 

## EXAMPLES (USER → OUTPUT):
User: "Need size 10 running shoes with arch support" → ["men's running shoes size 10", "arch support sneakers", "athletic footwear"]
User: "Coffee maker under $50 with timer" → ["programmable coffee maker", "budget coffee machine", "timer coffee brewer"]

## CURRENT USER INPUT: {input}
"""

# Template for conversational turns
prompt = ChatPromptTemplate.from_template(better_prompt)

chain = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=prompt,
) 



def run_conversation():
    print("Assistant: Hi there! I’m your personal shopping assistant. How can I help you today?")
    
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ["exit", "quit"]:
            print("Assistant: Thank you for visiting! Have a great day.")
            break
        
        # Get LLM response
        response = chain.invoke(user_input)
        
        # Check if LLM generated keywords list
        try:
            # Safely evaluate Python list
            keywords = ast.literal_eval(response['response'])
            
            if isinstance(keywords, list):
                print(f"Assistant: Thank you! Let me find some options for you based on: {keywords}")
                # Use the optimized multi-keyword scraper
                from search import snapdeal_scraper_multi
                total_product_list = asyncio.run(snapdeal_scraper_multi(keywords))
                for p in total_product_list:
                    print(f"- {p['title']} ({p['price']}, {p['discount']}): {p['link']}")
                print("Assistant: Do any of these interest you, or would you like more options?")
                continue
            else:
                print("not a list")
        except:
            # Not a keyword list yet → continue conversation
            pass
        
        # If LLM is still gathering info
        print(f"Assistant: {response['response']}")
       

if __name__ == "__main__":
    run_conversation()
