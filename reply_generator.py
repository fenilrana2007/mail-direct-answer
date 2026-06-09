import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)

def generate_ai_reply(incoming_sender: str, incoming_subject: str, incoming_body: str) -> str:
    """
    Generate an AI reply to an incoming email using Groq LLM (Llama-3.1).
    Falls back to a polite template if the API key is not configured or fails.
    
    Args:
        incoming_sender (str): Sender of the incoming email.
        incoming_subject (str): Subject of the incoming email.
        incoming_body (str): Content of the incoming email.
        
    Returns:
        str: The generated email reply.
    """
    # Truncate incoming email body to prevent Groq TPM limit errors on large emails
    if incoming_body and len(incoming_body) > 1500:
        incoming_body = incoming_body[:1500] + "\n[Email body truncated for length...]"

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    sender_name = os.getenv("SENDER_NAME", "Job Seeker")
    
    if not api_key or "your_groq" in api_key or api_key == "":
        logger.info("GROQ_API_KEY not configured. Using standard reply fallback.")
        return (
            f"Hi,\n\n"
            f"Thank you for your email!\n\n"
            f"I received your message and would love to connect. Please let me know what times work best for you to explore this opportunity further.\n\n"
            f"Best regards,\n"
            f"{sender_name}"
        )
        
    try:
        logger.info("Generating AI reply using Groq LLM Llama-3...")
        client = Groq(api_key=api_key)
        
        prompt = f"""
You are an expert professional assistant and career networking strategist.
Write a highly targeted, professional, and authentic email reply to the incoming email below.

Incoming Email Details:
- From: {incoming_sender}
- Subject: {incoming_subject}
- Message Body:
\"\"\"
{incoming_body}
\"\"\"

Sender Info (You):
- Name: {sender_name}

Anatomy & Constraint Rules:
- Keep the response under 120 words.
- Maintain an authentic, professional, humble, and warm tone.
- Directly address the specific inquiry or context of the incoming email (e.g. scheduling a call, answering a recruiter, scheduling an interview).
- End with exactly one clear, low-friction next step (e.g., sharing calendar availability, asking a relevant follow-up).
- Return ONLY the raw body of the email. Do not include any subject headers or markdown formatting.
"""
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=250
        )
        
        reply_body = chat_completion.choices[0].message.content.strip()
        return reply_body
        
    except Exception as e:
        logger.error(f"Groq LLM reply generation failed: {e}. Using template fallback.")
        return (
            f"Hi,\n\n"
            f"Thank you for your message! I would love to connect and discuss this further. What dates or times work best for a brief call next week?\n\n"
            f"Best regards,\n"
            f"{sender_name}"
        )
