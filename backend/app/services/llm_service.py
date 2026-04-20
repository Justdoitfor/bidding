from langchain_openai import ChatOpenAI
from app.core.config import settings

def get_qwen_llm():
    """
    Initialize the Qwen API client using LangChain's ChatOpenAI wrapper.
    Qwen is compatible with the OpenAI API format.
    """
    return ChatOpenAI(
        model=settings.QWEN_MODEL_NAME,
        api_key=settings.QWEN_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        temperature=0.1, # Low temperature for more deterministic, factual answers in RAG
        max_tokens=1024,
        streaming=True
    )

async def generate_rag_answer_stream(context: str, query: str):
    """
    Generate an answer using Qwen based on the provided context, yielding chunks asynchronously.
    """
    llm = get_qwen_llm()
    
    prompt = f"""
    你是一个专业的招投标与企业信息问答助手。
    请严格根据以下【参考资料】来回答用户的【问题】。
    如果【参考资料】中没有包含相关信息，请直接回答“抱歉，我没有找到相关信息”，不要编造答案。
    
    【参考资料】：
    {context}
    
    【问题】：
    {query}
    
    回答：
    """
    
    async for chunk in llm.astream(prompt):
        yield chunk.content

def generate_rag_answer(context: str, query: str) -> str:
    """
    Generate an answer using Qwen based on the provided context.
    """
    llm = get_qwen_llm()
    
    prompt = f"""
    你是一个专业的招投标与企业信息问答助手。
    请严格根据以下【参考资料】来回答用户的【问题】。
    如果【参考资料】中没有包含相关信息，请直接回答“抱歉，我没有找到相关信息”，不要编造答案。
    
    【参考资料】：
    {context}
    
    【问题】：
    {query}
    
    回答：
    """
    
    response = llm.invoke(prompt)
    return response.content
