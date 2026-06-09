import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)

def generate_email_template(record: dict) -> dict:
    recipient_name = record.get("recipient_name", "there")
    company = record.get("company", "your company")
    role = record.get("role", "the open position")
    personalization_note = record.get("personalization_note", "").strip()
    candidate_name = record.get("candidate_name", "Applicant")
    candidate_background = record.get("candidate_background", "development and technology")
    portfolio_url = record.get("portfolio_url", "")
    
    # 1. Subject Line: Short and specific
    subject = f"Outreach: {role} role at {company}"
    
    # 2. Hook & Body Assembly
    # The structure follows Hook -> Intro -> Value / Fit Statement -> One Clear Ask -> Signature
    hook_sentence = f"I noticed {company} is hiring for the {role} role."
    if personalization_note:
        hook_sentence += f" {personalization_note}"
        
    body = f"Hi {recipient_name},\n\n"
    body += f"{hook_sentence}\n\n"
    body += f"I'm {candidate_name}, and I'm {candidate_background}.\n\n"
    body += f"The role stood out because it aligns perfectly with my interest in building practical, high-impact systems at {company}.\n\n"
    body += "Would you be open to a brief look at my portfolio or pointing me toward the right person on the hiring team?\n\n"
    body += "Best,\n"
    body += f"{candidate_name}"
    
    if portfolio_url:
        body += f"\n{portfolio_url}"
        
    return {
        "subject": subject,
        "body": body,
        "word_count": len(body.split())
    }

def generate_email(record: dict) -> dict:
    """
    Generate subject line and personalized body for a cold email.
    Leverages Groq LLM if GROQ_API_KEY is configured, falling back to templates.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or "your_groq" in api_key or api_key == "":
        logger.info("Using standard template generator.")
        return generate_email_template(record)
        
    try:
        logger.info("Generating personalized email using Groq LLM Llama-3...")
        client = Groq(api_key=api_key)
        
        recipient_name = record.get("recipient_name", "there")
        company = record.get("company", "your company")
        role = record.get("role", "the open position")
        personalization_note = record.get("personalization_note", "").strip()
        candidate_name = record.get("candidate_name", "Applicant")
        candidate_background = record.get("candidate_background", "development and technology")
        portfolio_url = record.get("portfolio_url", "")
        
        prompt = f"""
You are an expert career advisor and cold outreach strategist.
Write a highly targeted, professional, and authentic cold email outreach to a recruiter.

Target Details:
- Recipient Name: {recipient_name}
- Target Company: {company}
- Target Role: {role}
- Personalization Hook Details: {personalization_note}

Sender Details:
- Sender Name: {candidate_name}
- Sender Background: {candidate_background}
- Portfolio/GitHub: {portfolio_url}

Strict Constraints:
- Under 130 words.
- Start with a compelling personalized opening line based on the Personalization Hook Details. Do NOT use generic intro sentences like "Hope this finds you well".
- Briefly connect the candidate's background directly to the company's role.
- Make exactly ONE clear, low-friction request (e.g. asking for a quick feedback chat or pointing to the correct person).
- Include the candidate's name and portfolio link at the end.
- Return ONLY the raw body of the email. Do not include any subject headers or markdown styling.
"""
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=250
        )
        
        body = chat_completion.choices[0].message.content.strip()
        subject = f"Outreach: {role} role at {company}"
        
        # Word Count Validator
        word_count = len(body.split())
        if word_count > 150:
            logger.warning(
                f"WARNING: Generated email for {company} is {word_count} words long, which exceeds the 150-word threshold constraint!"
            )
            
        return {
            "subject": subject,
            "body": body,
            "word_count": word_count
        }
        
    except Exception as e:
        logger.error(f"Groq LLM generation failed: {e}. Falling back to template.")
        return generate_email_template(record)
