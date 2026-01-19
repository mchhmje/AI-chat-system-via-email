import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr

import requests
import json
from google import genai

import time
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
MY_EMAIL = os.environ.get("MY_EMAIL")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json",
    "X-Title": "My Python Script"
}

GEMINI_MODEL = "gemini-3-flash-preview"
client = genai.Client(api_key=GEMINI_API_KEY)

# email
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"

    # --- מילון הפרסונות (התוכן) ---
PERSONAS = {
    # --- SIMPLE ---
    'פשט': 'ROLE: Expert Science Communicator using The Feynman Technique. TASK: Explain the concept to a smart 12-year-old. RULES: Ban professional jargon. Use analogies from cooking, sports, or daily life. GOAL: An "Aha!" moment. TONE: Encouraging, clear. LANGUAGE: Hebrew.',
    'תמצת': 'ROLE: Executive Intelligence Briefer. METHOD: The Pyramid Principle. TASK: Maximize info density. STRUCTURE: 1) The "Bottom Line Up Front" (BLUF). 2) Key Data Points. 3) Actionable Conclusions. FORMAT: Bullet points only. TONE: Sharp, direct. LANGUAGE: Hebrew.',
    'בקר': 'ROLE: Red Team Lead / Devil\'s Advocate. TASK: Ruthlessly dismantle the user\'s premise. IDENTIFY: Logical fallacies, security risks, financial gaps, and social biases. GOAL: Stress-test the idea. TONE: Fair but critical. LANGUAGE: Hebrew.',
    'התחלה': 'ROLE: Writing Coach & Hook Specialist. TASK: Generate 3 distinct opening hooks for a story based on the input. VARIATIONS: 1) In Medias Res (Action). 2) Atmospheric/Mystery. 3) Character voice/Dialogue. TONE: Inspiring. LANGUAGE: Hebrew.',
    'תגובה': 'ROLE: Senior Communications Director. TASK: Draft a response that is polite but firm, protecting the sender\'s interests while maintaining relationship. METHOD: Validate -> State boundary/answer -> Propose next step. TONE: Professional, Diplomatic. LANGUAGE: Hebrew.',
    'ברכה': 'ROLE: Personal Poet. TASK: Write a warm, specific greeting card. AVOID: Generic AI phrases. FOCUS: Shared memories, specific traits of the recipient, and genuine emotion. TONE: Warm, celebratory. LANGUAGE: Hebrew.',

    # --- ANALYSIS ---
    'חפש': 'ROLE: Chief Librarian & Fact-Checker. MENTAL MODEL: "Trust but Verify". TASK: Retrieve precise facts. STRICT RULES: 1) Cite potential sources. 2) CROSS-EXAMINATION: Explicitly state if sources conflict or data is disputed. 3) Separate fact from theory. TONE: Dry, Objective. LANGUAGE: Hebrew.',
    'נתח': 'ROLE: Elite Deep-Dive Analyst. MENTAL MODEL: First Principles Thinking. TASK: Break the topic down to basic truths. STRUCTURE: 1) Historical Context (The Why). 2) Core Mechanics (The How). 3) Implications. TONE: Professional, authoritative depth. LANGUAGE: Hebrew.',
    'תורה': 'ROLE: Torah Librarian & Researcher (Baki). RULES: 1) Hierarchy: Tanach->Chazal->Rishonim->Poskim. 2) SEPARATION: Quote text first, then explain. 3) NO INVENTIONS: If unknown, say so. 4) COMPLEXITY: Must present Machloket (conflicting opinions) if exists. TONE: Reverent, Scholar-to-Scholar. LANGUAGE: Hebrew.',
    'תשובה': 'ROLE: Solution Architect. METHOD: Root Cause Analysis. TASK: Provide a practical solution. STRUCTURE: 1) The Problem Definition. 2) The Fix (Immediate). 3) Prevention (Long term). 4) Necessary Resources. TONE: Practical. LANGUAGE: Hebrew.',
    'תכנן': 'ROLE: Strategic Operations Director. METHOD: Backward Design. TASK: Create a roadmap from Goal to Now. STRUCTURE: 1) Milestones. 2) Immediate Actions (Next 24h). 3) Risk Assessment (What could go wrong?). TONE: Organized, Commanding. LANGUAGE: Hebrew.',
    'קוד': 'ROLE: Senior Staff Engineer. METHOD: SOLID Principles. TASK: Write production-ready code. STRUCTURE: 1) Brief Logic Overview. 2) The Code (Clean, Commented, Optimized). 3) Edge Cases & Security Warnings. LANGUAGE: Code in English, explanations in Hebrew.',

    # --- CREATIVE ---
    'תיאור': 'ROLE: Literary Fiction Author (Jewish Historical Prose). STYLE: Archaic yet accessible. METAPHORS: Nature (roots, stone), Agriculture, Crafts. RULES: 1) Measure time by Light/Prayer (NO clocks). 2) Focus on Weight, Texture, Scent. 3) Atmosphere: Heavy, Nostalgic. TONE: Reflective.',
    'דמות': 'ROLE: Psychological Character Architect. TASK: Build a multi-layered profile. INCLUDE: 1) The Surface (Scars/Mannerisms). 2) The "Ghost" (Past trauma). 3) The "Lie" (Self-deception). 4) The Want vs. The Need. AVOID: Clichés. TONE: Psychological.',
    'סיפור': 'ROLE: Genre Fiction Best-Seller. TASK: Write a scene with high tension. STRUCTURE: Hook -> Inciting Incident -> Rising Action -> Twist. RULES: "Show, Don\'t Tell". Use sensory details to build suspense. TONE: Narrative, Gripping.',
    'שיר': 'ROLE: Hebrew Paytan & Poet. STYLE: Biblical/Medieval influence. TASK: Write a structured poem with rhythm and deep emotion. FOCUS: Vivid metaphors, musicality, high register Hebrew. FORMAT: Stanzas. TONE: Lyrical, Elevated.',
    'הומור': 'ROLE: Head Writer for Satire/Stand-up. TASK: Create a substantial long-form piece (Sketch/Routine). RULES: Build a narrative, escalate absurdity, use observational humor. AVOID: One-liners or "Dad jokes". TONE: Witty, Sharp.',
    'צור': 'ROLE: Master Creative Writer. METHOD: Sensory Writing. TASK: Create immersive content. RULES: Avoid generic AI tropes. Use specific details over generalizations. Focus on subtext and human connection. TONE: Artistic.',

    # --- ITERATIVE ---
    'נובלה': 'ROLE: Serial Novelist. TASK: Write the NEXT chapter of the story based on previous context. RULES: Maintain continuity of plot, character voice, and tone. Advance the plot significantly. End on a mini-cliffhanger. TONE: Storytelling.',
    'קורס': 'ROLE: Master Tutor (Constructivist Teaching). GOAL: Teach the concept fully in one module. STRUCTURE: 1) Deep Dive (Mechanics/Logic). 2) Mental Model (Analogy). 3) Real-world Application. 4) Thought Experiment. TONE: Educational, Authoritative.',

    # העורך והממזג
    'עורך_על': """ROLE: Lead Meta-Analyst & Editor.
    CONTEXT: You have received inputs from multiple AI agents (e.g., GROQ, Llama, GPT) regarding a user query.
    GOAL: Produce a comprehensive answer that synthesizes the wisdom of all agents while GIVING CREDIT where due.
    INSTRUCTIONS:
    1. ATTRIBUTION: When a specific model provides a unique insight, cite it (e.g., "כפי שציין Llama..." or "בעוד ש-GROQ מדגיש...").
    2. CONFLICT HANDLING: If models disagree, present the conflict explicitly ("מודל X טוען A, אך מודל Y מציע B. הסבירות היא...").
    3. STRUCTURE: Start with a clear bottom line, then move to a deep synthesis of the points.
    4. LENGTH & DEPTH: Do not shorten content. Keep the richness of the original arguments.
    5. REVIEW & CORRECTION: When information provided is incorrect or incomplete, you must add and correct it, and indicate that you did it yourself.
    OUTPUT: A rich, Hebrew article-style response referencing the source models."""
}
DEFAULT_PERSONA = 'You are a kind and efficient assistant, writing in maximum detail and length, with a concern for rich content and a well built reading sequence.'
LENGTH_INSTRUCTION = "\nIMPORTANT: Write a VERY LONG, DETAILED, and COMPREHENSIVE response. Do not act lazy. Use at least 800 words."

AI_MODELS = ["groq/compound", "llama-3.3-70b-versatile", "openai/gpt-oss-20b"]

# ----- הגדרות השפה -----
LANG_INSTRUCTIONS_HE = """
[SYSTEM: FORMATTING RULES]
1. OUTPUT FORMAT: The output is meant to be text attached to an email, Without subject and signature - just the text itself.
2. NO MARKDOWN: Do NOT use asterisks (**), hashes (#), or backticks (`).
3. EMPHASIS: Use CAPITALIZATION for headers. Use bullet points (-) for lists.
4. LANGUAGE: REPLY MUST BE IN HEBREW ONLY.
"""

def clean_text(text_bytes):
    """מפענח טקסט מקודד (ג'יבריש) לעברית/אנגלית קריאה"""
    if not text_bytes: return ""

    decoded_list = decode_header(text_bytes)
    text_segment, encoding = decoded_list[0]

    if encoding:
        return text_segment.decode(encoding)
    elif isinstance(text_segment, bytes):
        return text_segment.decode('utf-8')
    else:
        return text_segment # זה כבר str


def get_email_body(msg):
    """רץ בתוך עץ המייל ומוצא את הטקסט הפשוט"""
    if msg.is_multipart():
        for part in msg.walk():
            # מתעלמים מקבצים מצורפים, מחפשים טקסט פשוט
            if part.get_content_maintype() == 'multipart': continue
            if part.get('Content-Disposition') is not None: continue
            if part.get_content_type() == 'text/plain':
                try:
                    return part.get_payload(decode=True).decode()
                except:
                    return "[Error decoding body]"

    else:
        return msg.get_payload(decode=True).decode()
    return "[No text body found]"


def parse_thread_from_body(full_body):
    """
    כאשר מייל מורכב משיחה של תגובות, הפונקציה מחלצת רשימה מסודרת של הפניות
    """
    if full_body == "[No text body found]" or full_body == "[Error decoding body]":
        return full_body if type(full_body) == list else [full_body]
    
    lines = full_body.splitlines()
    conversation = []
    
    current_block_lines = []
    current_depth = 0
    
    for line in lines:
        stripped_line = line.lstrip() # מוריד רווחים בהתחלה
        
        # ספירת כמה '>' יש בהתחלה
        depth = 0
        for char in stripped_line:
            if char == '>': 
                depth += 1
            else:
                break        
        clean_content = stripped_line[depth:].strip() # מנקים את החיצים מהטקסט עצמו

        # התעלמות משורות "לכלוך" של כותרות מייל
        if clean_content.startswith("On ") and "wrote:" in clean_content:
            continue # מדלגים על שורת ה-"בתאריך X כתב:"
        if clean_content == "":
            continue # מדלגים על שורות ריקות לגמרי
            
        if depth != current_depth: # אם העומק השתנה, סימן שעברנו להודעה אחרת בשרשור
            if current_block_lines: # שומרים את מה שאספנו עד עכשיו
                full_msg = "\n".join(current_block_lines)
                conversation.append(full_msg)
            current_block_lines = [] # מאפסים ומתחילים בלוק חדש
            current_depth = depth
        current_block_lines.append(clean_content) # מוסיפים את השורה לבלוק הנוכחי

    if current_block_lines: # לא לשכוח לשמור את הבלוק האחרון שנשאר בסוף הלולאה
        full_msg = "\n".join(current_block_lines)
        conversation.append(full_msg)

    conversation_order = list(reversed(conversation)) # ה-AI צריך לקרוא מהעבר להווה (2, 1, 0).
    return conversation_order


def subject_splitter(subject):
    """
    הפונקציה מקבלת נושא שמכיל (אולי) מילת מפתח, ומספר הרצות
    הפונקציה דואגת להחזיר מילון שמכיל את הפרסונה, את מספר המודלים והאם מיזוג נדרש
    """
    subject_parts = subject.split(" ")
    setting = {
        "persona": DEFAULT_PERSONA,
        "runs": 3,
        "merging": True,
    }

    for persona in PERSONAS: # בדיקה האם קיימת פרסונה
        if persona in subject_parts:
            setting["persona"] = PERSONAS[persona]
            break

    for part in subject_parts: # בדיקה האם נבחר מספר ריצות
        if part.isdigit():
            num = int(part)
            setting["runs"] = min(num, 3)
            break
    
    if "-" in subject_parts: # בדיקה האם נבחר שלא לעשות merging
        setting["merging"] = False

    return setting


def send_reply(original_sender, original_subject, original_message_id, reply_text):
    """
    שולח מייל תגובה עם התגובה של הAI
    שולח את ההודעה כתגובה
    """
    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = original_sender
    msg['In-Reply-To'] = original_message_id
    msg['References'] = original_message_id
    if not original_subject.startswith("Re:"):
        msg['Subject'] = f"Re: {original_subject}"
    else:
        msg['Subject'] = original_subject

    body = MIMEText(reply_text, 'plain', 'utf-8')
    msg.attach(body)

    try:
        server = smtplib.SMTP(SMTP_SERVER, 587)
        server.starttls()
        server.login(MY_EMAIL, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True

    except Exception as e:
        print(e)
        return False

# ---- פונקציות AI -----
def response_extractor(response_data):
    choices_list = response_data.get("choices", [])
    if choices_list:
        choices = choices_list[0]
        content = choices.get("message", {}).get("content", "Error getting response.")
        return content
    else:
        return "Error extracting response"


def run_gemini(full_response):
    print(f"running {GEMINI_MODEL}")
    try:
        response = client.models.generate_content(
            model = GEMINI_MODEL,
            contents = PERSONAS["עורך_על"] + "\nThe responses of AI models to test:\n" + full_response + LANG_INSTRUCTIONS_HE + LENGTH_INSTRUCTION
        )
        return response.text
    except:
        try:
            response = client.models.generate_content(
                model = "gemini-2.5-flash",
                contents = PERSONAS["עורך_על"] + "\nThe responses of AI models to test:\n" + full_response + LANG_INSTRUCTIONS_HE
            )
            return response.text
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"


def run_ai(payload):
    """
    מקבל payload ושולח לאחד המודלים של GROQ
    """
    try:
        response = requests.post(GROQ_URL, headers=GROQ_HEADERS, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            content = response_extractor(response_data)
            return content
        else:
            return f"Error: {response.status_code}"

    except Exception as e:
        return f"Error: {e}"


def handle_first_message(body, subject):
    setting = subject_splitter(subject)
    wanted_runs = setting["runs"]
    merging = setting["merging"]
    runs = 0
    full_response = f"שאלה מקורית: {body}\n\n"
    while wanted_runs > runs:
        model = AI_MODELS[runs % 3]
        print(f"running {model}")
        payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": setting["persona"] + LENGTH_INSTRUCTION},
            {"role": "user", "content": body + LANG_INSTRUCTIONS_HE}
            ]
        }
        response = run_ai(payload)
        full_response += model + "\n\n" + response + "\n\n"
        runs += 1
        time.sleep(1)
    
    if merging:
        merging_response = run_gemini(full_response)
        full_response += "ניתוח התגובות" + "\n\n" + merging_response
    
    return full_response


def handle_conversation(conversation):
    messages = [{"role": "system", "content": DEFAULT_PERSONA + " " + LENGTH_INSTRUCTION + LANG_INSTRUCTIONS_HE}]
    if len(conversation) % 2 == 0: # אם זוגי - ההודעה הראשונה הייתה של המודל
        conversation_index = ["assistant", "user"]
    else: # אם אי זוגי - ההודעה הראשונה הייתה של המשתמש 
        conversation_index = ["user", "assistant"]
    for i in range(len(conversation)):
        part_message = {"role": conversation_index[i % 2], "content": conversation[i]}
        if i == len(conversation) - 1:
            part_message["content"] += LANG_INSTRUCTIONS_HE + LENGTH_INSTRUCTION
        messages.append(part_message)
    payload = {"model": AI_MODELS[0], "messages": messages}
    print(f"running {AI_MODELS[0]}")
    response = run_ai(payload)
    return response


def main_program():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(MY_EMAIL, EMAIL_PASS)
        mail.select('"to the bot"')
        status, data = mail.search(None, 'UNSEEN')
        if status != 'OK':
            print("Label 'to the bot' not found!")
            return

        email_ids = data[0].split()
        if not data[0]:
            print("No new emails.")
            return
        else:
            print("found new emails")

        for email_id in email_ids:
            _, msg_data = mail.fetch(email_id, '(RFC822)')
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = clean_text(msg["Subject"])
            message_id = msg.get("Message-ID")
            from_name, from_email = parseaddr(msg["From"])
            from_name = clean_text(from_name) # לא שימושי
            body = get_email_body(msg)
            conversation_order = parse_thread_from_body(body)
            if len(conversation_order) <= 1: 
                full_response =  handle_first_message(body, subject)
            else:
                full_response =  handle_conversation(conversation_order)

            # שליחת תגובה
            reply_success = send_reply(
                    original_sender = from_email,
                    original_subject = subject,
                    original_message_id = message_id,
                    reply_text = full_response
                )
            if reply_success:
                mail.store(email_id, '+X-GM-LABELS', '"handled by the bot"')
                mail.store(email_id, '-X-GM-LABELS', '"to the bot"')
                mail.store(email_id, '+FLAGS', '\\Seen')
                print("sent")
            else:
                mail.store(email_id, '+X-GM-LABELS', '"error when handled by the bot"')
                mail.store(email_id, '-X-GM-LABELS', '"to the bot"')
                mail.store(email_id, '+FLAGS', '\\Unseen')
                mail.store(email_id, '-FLAGS', '\\Seen')

    except Exception as e:
        print(f"Critical Error in main_program: {e}")

    finally:
        try:
            mail.close() # סגירת התיקייה
            mail.logout() # סגירת החיבור
        except:
            pass

main_program()


# ==== Functions ====



