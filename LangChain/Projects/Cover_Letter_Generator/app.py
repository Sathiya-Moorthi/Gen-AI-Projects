# cover_letter_gen.py
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

# Page config
st.set_page_config(
    page_title="📄 Cover Letter Generator + 🌐 Company Research",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ====== SIDEBAR ======
with st.sidebar:
    st.image("https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/apple/325/page-facing-up_1f4c4.png", width=60)
    st.header("⚙️ Settings")
    
    api_key = os.getenv("OPENAI_API_KEY") or st.text_input(
        "OpenAI API Key", type="password", placeholder="sk-..."
    )
    
    tavily_key = os.getenv("TAVILY_API_KEY") or st.text_input(
        "Tavily API Key", type="password", 
        help="Free at [tavily.com](https://app.tavily.com)",
        placeholder="tvly-..."
    )
    
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-3.5-turbo"], index=0)
    temperature = st.slider("Creativity", 0.0, 1.0, 0.4, 0.1)
    
    # Define research_enabled HERE, inside the sidebar
    research_enabled = st.toggle("🌐 Enable Company Research", value=bool(tavily_key))
    
    st.markdown("---")
    st.caption("🔒 All data stays local. Research only if enabled.")

# ====== VALIDATION ======
# Now we can safely check research_enabled because it is defined
if not api_key:
    st.warning("🔑 Please enter your OpenAI API key.")
    st.stop()

if research_enabled and not tavily_key:
    st.warning("🔍 Please enter your Tavily API key to enable company research.")
    st.stop()

# ====== TOOLS & CHAINS ======
llm = ChatOpenAI(model=model, temperature=temperature, api_key=api_key)

if research_enabled:
    tavily = TavilySearch(
        max_results=3,
        search_depth="advanced",
        include_answer=True,
    )

COVER_LETTER_PROMPT = """You are **CoverCraft**, an expert career advisor.

### 🎯 TASK
Write a compelling, personalized cover letter using:
- Job description
- Candidate background
- Company insights (if provided)
- Desired tone

### 📌 Company Insights (if available):
{research}

### 📝 Requirements
1. Structure:
   - Opening: Role + enthusiasm + how you found it
   - Why this company? → Use insights above
   - Why you? Match 2–3 skills to job needs
   - Closing: Call-to-action

2. Rules:
   - 250–350 words
   - Use placeholders: [Your Name], [Email], etc.
   - Tone: {tone}
   - NEVER invent facts — only use provided info

### OUTPUT FORMAT (STRICT):
[Your Name]
[Contact Info]

[Date]

[Hiring Manager]
[Company]
[Address]

Dear [Hiring Manager],

[Paragraph 1]

[Paragraph 2: Why this company?]

[Paragraph 3: Why you?]

[Paragraph 4]

Sincerely,
[Your Name]


Job & Background:
{input}
"""

prompt = ChatPromptTemplate.from_template(COVER_LETTER_PROMPT)

def get_research(company: str) -> str:
    if not research_enabled or not company.strip():
        return "No company research performed."
    try:
        st.info(f"🔍 Researching **{company}**…")
        query = f"{company} mission values recent news 2025"
        results = tavily.invoke({"query": query})
        
        answer = results[0].get("content", "") if results and isinstance(results[0], dict) else ""
        snippets = "\n".join([r.get("content", "")[:200] + "…" for r in results[:2]])
        
        return f"**Tavily Summary**:\n{answer}\n\n**Key Points**:\n{snippets}"
    except Exception as e:
        return f"⚠️ Research failed: {str(e)}"

# ====== MAIN UI ======
st.title("📄 Cover Letter Generator + 🌐 Company Research")
st.markdown("Generate ATS-friendly, *research-informed* cover letters that stand out.")

tab_guide, tab_free = st.tabs(["📝 Quick Builder", "💬 Describe Freely"])

# === TAB 1: Guided ===
with tab_guide:
    st.subheader("✨ Fill key details")
    
    col1, col2 = st.columns(2)
    with col1:
        role = st.text_input("Job Title", placeholder="e.g., Senior Product Manager")
        company = st.text_input("Company Name", placeholder="e.g., Notion, SpaceX")
    with col2:
        tone = st.selectbox("Tone", ["Professional", "Enthusiastic", "Confident", "Humble"], index=1)
        years_exp = st.number_input("Years of Experience", 0, 50, 5)
    
    job_desc = st.text_area("Job Description", placeholder="Paste key requirements...", height=100)
    resume_bg = st.text_area("Your Background", placeholder="• Skill 1\n• Achievement...", height=100)
    
    generate = st.button("✨ Generate Cover Letter", type="primary", use_container_width=True)

# === TAB 2: Freeform ===
with tab_free:
    st.subheader("🎯 Or describe freely")
    free_input = st.text_area(
        "Include company name for research!",
        placeholder="Applying to Stripe for Growth PM role. I have 4 years in fintech, grew MRR by 200%. Love their mission of 'economic infrastructure for the internet'. Want confident tone.",
        height=120
    )
    generate_free = st.button("✨ Generate", type="primary", key="free", use_container_width=True)

# ====== GENERATION ======
if generate or generate_free:
    with st.spinner("✍️ Crafting your cover letter…"):
        if generate:
            if not job_desc or not resume_bg:
                st.error("⚠️ Job description and background are required.")
                st.stop()
            input_data = {
                "input": f"Job: {role}\nCompany: {company}\nDescription:\n{job_desc}\n\nMy Background:\n{resume_bg}",
                "company": company,
            }
        else:
            if not free_input:
                st.error("⚠️ Please describe.")
                st.stop()
            import re
            company_match = re.search(r"(?:at|for|to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", free_input, re.IGNORECASE)
            company_guess = company_match.group(1) if company_match else ""
            input_data = {
                "input": free_input,
                "company": company_guess,
            }
            tone = "Professional"

        # ✅ Build chain here — with known 'tone'
        if research_enabled:
            chain = (
                RunnableParallel(
                    input=RunnablePassthrough(),
                    research=lambda x: get_research(x.get("company", "")),
                )
                | prompt.partial(tone=tone)
                | llm
                | StrOutputParser()
            )
        else:
            chain = (
                {"input": RunnablePassthrough(), "research": lambda _: "Disabled"}
                | prompt.partial(tone=tone)
                | llm
                | StrOutputParser()
            )

        try:
            response = ""
            placeholder = st.empty()
            placeholder.info("📝 Writing…")
            for chunk in chain.stream(input_data):
                response += chunk
                placeholder.markdown(f"📝 **Drafting...**\n\n```\n{response}▌\n```")
            placeholder.empty()
            
            st.session_state.cover_letter = response.strip()
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ====== OUTPUT ======
if "cover_letter" in st.session_state:
    st.markdown("---")
    st.subheader("📄 Your Cover Letter")
    
    draft = st.text_area("Edit as needed", value=st.session_state.cover_letter, height=500)
    
    # Filename
    try:
        first_line = draft.strip().split('\n')[0]
        name = first_line.replace('[Your Name]', 'Applicant')[:20]
        fname = f"cover_letter_{name.replace(' ', '_')}"
    except:
        fname = "cover_letter"

    col1, col2, col3 = st.columns(3)

    # === .txt Download ===
    with col1:
        st.download_button(
            "📥 Download (.txt)",
            draft,
            file_name=f"{fname}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # === Copy to Clipboard ===
    with col3:
        js_safe = (
            draft
            .replace('\\', '\\\\')
            .replace('`', '\\`')
            .replace('\n', '\\n')
            .replace('\r', '')
            .replace('{', '\\{')
            .replace('}', '\\}')
        )
        copy_button_html = f"""
        <script>
        function copyToClipboard() {{
            const text = `{js_safe}`;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.getElementById('copy-btn');
                btn.innerHTML = '✅ Copied!';
                btn.style.backgroundColor = '#4CAF50';
                setTimeout(() => {{
                    btn.innerHTML = '<span>📋</span> Copy';
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
            <span>📋</span> Copy
        </button>
        """
        st.components.v1.html(copy_button_html, height=60)

st.caption("✅ Powered by LangChain + Tavily + OpenAI • 🔒 Private & secure")