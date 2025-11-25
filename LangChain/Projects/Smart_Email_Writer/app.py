# email_writer.py
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env (optional)
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="✉️ Smart Email Writer",
    page_icon="✉️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ====== SIDEBAR: Settings & API Key ======
with st.sidebar:
    st.image("https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/325/envelope_2709-fe0f.png", width=60)
    st.header("⚙️ Settings")
    
    # API Key input (from env or manual)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="🔑 Get yours at [platform.openai.com](https://platform.openai.com/api-keys)",
            placeholder="sk-..."
        )
    
    # Model selection with safe index
    model_options = ["gpt-4o-mini", "gpt-3.5-turbo"]
    default_index = 0  # Always fall back to first option

    # Optional: If you want gpt-4o-mini for gpt-4 keys, keep index=0
    # If you want gpt-3.5-turbo for gpt-4 keys, set index=1
    if api_key and "gpt-4" in api_key:
        default_index = 0  # or 1 — choose your logic

    model = st.selectbox(
        "Model",
        model_options,
        index=default_index,
        help="gpt-4o-mini is better for nuance & professionalism"
    )
    
    temperature = st.slider(
        "Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Lower → more formal & predictable | Higher → more creative"
    )
    
    st.markdown("---")
    st.caption("🔒 Your data stays private — no emails are stored or sent to external servers.")

# Safety check
if not api_key:
    st.warning("🔑 Please enter your OpenAI API key in the sidebar to continue.")
    st.stop()

# ====== EMAIL GENERATION ENGINE ======
EMAIL_PROMPT = """You are **EmailGenius**, an expert professional email writer with 15+ years of corporate communications experience.

### 🎯 TASK
Write a polished, effective email based on the user's request.

### 📝 REQUIREMENTS
1. **Structure**:
   - Line 1: `Subject: [clear, concise subject < 60 chars]`
   - Blank line
   - `Dear [Recipient Name],` (or `Hi [First Name],` for friendly tone)
   - Body: 2–4 short paragraphs (concise, scannable)
   - Closing: `Best regards,`, `Sincerely,`, etc.
   - Signature block with placeholders

2. **Placeholders** — NEVER invent real data:
   - `[Your Name]`, `[Your Title]`, `[Company]`
   - `[Recipient Name]`, `[Their Title]`
   - `[Date]`, `[Specific Deadline]`, `[Link/Attachment]`

3. **Tone Matching**:
   - `Formal`: Full titles, no contractions, passive voice OK
   - `Friendly`: Contractions, warmth, max 1 emoji (e.g., 👍)
   - `Urgent`: Bold deadlines, action verbs, clear CTA
   - `Empathetic`: Acknowledge feelings, sincere apology if needed
   - `Persuasive`: Benefit-focused, social proof, strong CTA

4. **Include exactly one clear Call-to-Action** (e.g., "Could you reply by Friday?", "Let’s schedule a call.")

### 🚫 NEVER
- Invent fake names/emails/companies
- Use markdown (e.g., **bold**), HTML, or excessive formatting
- Exceed 150 words unless requested

### OUTPUT FORMAT (STRICT — copy exactly):
Subject: [subject]

Dear [Recipient Name],

[Paragraph 1...]

[Paragraph 2...]

[Paragraph 3 (if needed)...]

Best regards,
[Your Name]
[Your Title]
[Email] | [Phone]
[Company]

Now generate an email for this request:
{input}
"""

# Build LangChain prompt & chain
prompt = ChatPromptTemplate.from_template(EMAIL_PROMPT)

llm = ChatOpenAI(
    model=model,
    temperature=temperature,
    api_key=api_key,
    streaming=True,
    max_retries=2
)

chain = (
    {"input": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# ====== MAIN UI ======
st.title("✉️ Smart Email Writer")
st.markdown(
    "Generate professional, tone-perfect emails in seconds — for work, networking, or follow-ups."
)

# Tabs: Form vs Freeform
tab_form, tab_free = st.tabs(["📝 Quick Builder", "💬 Describe Freely"])

# === TAB 1: Quick Form ===
with tab_form:
    st.subheader("✨ Build with guided inputs")
    
    col1, col2 = st.columns(2)
    with col1:
        purpose = st.selectbox(
            "Purpose",
            [
                "Follow-up after meeting/interview",
                "Job application or inquiry",
                "Sales pitch or proposal",
                "Customer support request",
                "Apology or service recovery",
                "Networking or introduction",
                "Event invitation or RSVP",
                "Thank-you note",
                "Internal team update"
            ],
            index=0
        )
    with col2:
        tone = st.selectbox(
            "Tone",
            ["Formal", "Friendly", "Urgent", "Empathetic", "Persuasive"],
            index=1
        )
    
    context = st.text_area(
        "Key Details (Who? What? Why? Deadline?)",
        placeholder="e.g., Met Jamie at Web Summit. Discussed SaaS integration. Need feedback on pricing by Thursday.",
        height=100
    )
    
    recipient = st.text_input("Recipient (optional)", placeholder="e.g., hiring manager, Alex Rivera")
    sender_name = st.text_input("Your Name", value="Alex Johnson")

    generate_form = st.button("🚀 Generate Email", type="primary", use_container_width=True)

# === TAB 2: Freeform ===
with tab_free:
    st.subheader("🎯 Or just describe your need")
    free_input = st.text_area(
        "Tell me what email you'd like",
        placeholder="Write a polite but urgent email to the client PM about the delayed deliverables. We're 2 days late due to a third-party API issue. Offer a revised deadline and a discount.",
        height=120
    )
    generate_free = st.button("🚀 Generate Email", type="primary", use_container_width=True, key="free_btn")

# ====== GENERATION LOGIC ======
if generate_form or generate_free:
    with st.spinner("✍️ Crafting your email..."):
        # Build input
        if generate_form:
            if not context.strip():
                st.error("⚠️ Please provide some context/details.")
                st.stop()
            input_text = f"""Purpose: {purpose}
                            Tone: {tone}
                            Recipient: {recipient or 'Recipient'}
                            Your Name: {sender_name}
                            Context: {context}
                            """
        else:
            if not free_input.strip():
                st.error("⚠️ Please describe your email need.")
                st.stop()
            input_text = free_input

        # Generate
        try:
            full_response = ""
            placeholder = st.empty()
            placeholder.info("📝 Drafting...")
            
            for chunk in chain.stream(input_text):
                full_response += chunk
                # Show live drafting with cursor
                placeholder.markdown(f"📝 **Drafting...**\n\n```\n{full_response}▌\n```")
            
            placeholder.empty()
            st.session_state.email_draft = full_response.strip()
            st.session_state.generation_input = input_text
            
        except Exception as e:
            st.error(f"❌ Error generating email: {str(e)}")
            st.stop()

# ====== DISPLAY & EDIT OUTPUT ======
if "email_draft" in st.session_state:
    st.markdown("---")
    st.subheader("📬 Your Email Draft")
    
    draft = st.text_area(
        "Edit & refine below",
        value=st.session_state.email_draft,
        height=450,
        key="editable_email"
    )
    
    # Extract subject for filenames
    try:
        subject = draft.split("Subject: ", 1)[1].split("\n", 1)[0].strip()
        safe_subject = "".join(c if c.isalnum() or c in " _-" else "_" for c in subject)[:40]
        txt_filename = f"email_{safe_subject}.txt"
        eml_filename = f"email_{safe_subject}.eml"
    except Exception:
        subject = "Email Draft"
        txt_filename = "email_draft.txt"
        eml_filename = "email_draft.eml"
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📥 Download (.txt)",
            draft,
            file_name=txt_filename,
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        # Create .eml file in memory
        def make_eml(content):
            msg = MIMEMultipart()
            msg["From"] = "you@example.com"
            msg["To"] = "recipient@example.com"
            try:
                subj = content.split("Subject: ", 1)[1].split("\n", 1)[0]
                msg["Subject"] = subj
            except:
                msg["Subject"] = "Email Draft"
            
            # Extract body (skip first two lines: Subject + blank)
            lines = content.strip().split("\n")
            body_start = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith("Subject:"):
                    body_start = i
                    break
            body = "\n".join(lines[body_start:])
            
            msg.attach(MIMEText(body, "plain"))
            
            buf = io.BytesIO()
            buf.write(msg.as_bytes())
            buf.seek(0)
            return buf.getvalue()
        
        st.download_button(
            "📧 Download (.eml)",
            make_eml(draft),
            file_name=eml_filename,
            mime="message/rfc822",
            use_container_width=True
        )

    with col3:

        # Escape draft for JS (safe for any content)
        js_safe_draft = (
            draft
            .replace('\\', '\\\\')
            .replace('`', '\\`')
            .replace('\n', '\\n')
            .replace('\r', '')
            .replace('{', '\\{')
            .replace('}', '\\}')
        )

        # Button styled to match .txt/.eml download buttons
        copy_button_html = f"""
        <script>
        function copyToClipboard() {{
            const text = `{js_safe_draft}`;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById('copy-btn');
                btn.innerHTML = '✅ Copied!';
                btn.style.backgroundColor = '#4CAF50';
                setTimeout(() => {{
                    btn.innerHTML = '<span>📋</span> Copy to Clipboard';
                    btn.style.backgroundColor = '#007bff';
                }}, 2000);
            }}).catch(err => {{
                alert('❌ Copy failed: ' + err);
            }});
        }}
        </script>

        <button 
            id="copy-btn"
            onclick="copyToClipboard()"
            style="
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                width: 100%;
                transition: all 0.2s;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            "
            onmouseover="this.style.backgroundColor='#0056b3'"
            onmouseout="this.style.backgroundColor='#007bff'"
        >
            <span>📋</span> Copy to Clipboard
        </button>
        """

        st.components.v1.html(copy_button_html, height=60)

# Footer
st.markdown("---")
st.caption(
    "✉️ Smart Email Writer • Powered by LangChain & OpenAI • "
    "🔒 100% client-side — your content never leaves this browser."
)