from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import GoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from app.settings import GOOGLE_API_KEY

def create_content(prompt: str) -> str:
    """Generate email content using Google Generative AI for various actions like user registration, 
    product addition, order placement, payment, and order status.
    
    Args:
        prompt (str): The input prompt for the generative AI model.
    
    Returns:
        str: The generated email content in HTML format.
    """
    chat_template = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "You are a helpful assistant. Generate email content related to user registration, "
                "product addition, order placement, payment, and order status. The email content should "
                "be formatted in HTML, not markdown, and should be clear, informative, and professional. "
                "Read the prompt then generate the email content."
            )
        ),
        HumanMessagePromptTemplate.from_template("{prompt}"),
    ])
    
    llm = GoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=GOOGLE_API_KEY,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        },
    )

    chat_message = chat_template.format_messages(prompt=prompt)
    
    return llm.invoke(chat_message)
