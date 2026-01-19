<<<<<<< HEAD
"""
Enhanced Streamlit Frontend - FINAL VERSION
============================================
✅ Theme-compatible (light/dark mode)
✅ Real-time sequential agent execution monitoring
✅ Improved prompts for publication-ready content
✅ Better error handling and user feedback

Run: streamlit run streamlit_frontend_app.py
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import hashlib
import base64
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Content Generator Pro | Multi-Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.example.com',
        'Report a bug': "https://github.com/example/issues",
        'About': "# Multi-Agent Content Generation System\nPowered by AutoGen & GPT-4 Mini"
    }
)

# ============================================================================
# THEME-COMPATIBLE CUSTOM CSS
# ============================================================================

def load_custom_css():
    """Load theme-compatible CSS that works in both light and dark modes"""
    st.markdown("""
    <style>
        /* Global Variables */
        :root {
            --primary-color: #1E3A8A;
            --secondary-color: #3B82F6;
            --accent-color: #10B981;
            --danger-color: #EF4444;
            --warning-color: #F59E0B;
            --success-color: #22C55E;
        }
        
        /* Header - Always Visible */
        .main-header {
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 2rem;
            border-radius: 0.75rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        }
        
        .main-header h1 {
            color: #FFFFFF !important;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }
        
        .main-header p {
            color: #E0E7FF !important;
            font-size: 1.1rem;
            margin: 0;
        }
        
        /* Agent Cards - Theme Aware */
        .agent-card {
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--primary-color);
            transition: all 0.3s ease;
            background: #FFFFFF;
            color: #111827;
        }
        
        [data-theme="dark"] .agent-card,
        .stApp[data-theme="dark"] .agent-card {
            background: #1F2937 !important;
            color: #F9FAFB !important;
        }
        
        .agent-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.15);
        }
        
        .agent-card.active {
            border-left-color: var(--accent-color);
            animation: pulse 2s infinite;
            background: linear-gradient(to right, #f0fdf4, #ffffff) !important;
            color: #111827 !important;
        }
        
        [data-theme="dark"] .agent-card.active,
        .stApp[data-theme="dark"] .agent-card.active {
            background: linear-gradient(to right, #064e3b, #1F2937) !important;
            color: #F9FAFB !important;
        }
        
        .agent-card.completed {
            border-left-color: var(--success-color);
            opacity: 0.95;
            background: #FFFFFF !important;
            color: #111827 !important;
        }
        
        [data-theme="dark"] .agent-card.completed,
        .stApp[data-theme="dark"] .agent-card.completed {
            background: #1F2937 !important;
            color: #F9FAFB !important;
        }
        
        .agent-card.error {
            border-left-color: var(--danger-color);
            background: #FEF2F2 !important;
            color: #111827 !important;
        }
        
        [data-theme="dark"] .agent-card.error,
        .stApp[data-theme="dark"] .agent-card.error {
            background: #7F1D1D !important;
            color: #FEE2E2 !important;
        }
        
        .agent-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        
        .agent-title {
            font-size: 1.25rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #111827 !important;
        }
        
        [data-theme="dark"] .agent-title,
        .stApp[data-theme="dark"] .agent-title {
            color: #F9FAFB !important;
        }
        
        .agent-description {
            margin: 0;
            color: #6B7280 !important;
        }
        
        [data-theme="dark"] .agent-description,
        .stApp[data-theme="dark"] .agent-description {
            color: #D1D5DB !important;
        }
        
        .agent-status {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .agent-status.active {
            background: #DBEAFE;
            color: #1E40AF;
        }
        
        .agent-status.completed {
            background: #D1FAE5;
            color: #065F46;
        }
        
        .agent-status.pending {
            background: #F3F4F6;
            color: #6B7280;
        }
        
        .agent-status.error {
            background: #FEE2E2;
            color: #991B1B;
        }
        
        /* Progress Bar Animation */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        
        /* Buttons */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white !important;
            border-radius: 0.5rem;
            font-weight: 500;
            padding: 0.625rem 1.25rem;
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E3A8A 0%, #1E40AF 100%);
        }
        
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div {
            color: white !important;
        }
        
        /* Animations */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        /* Metrics */
        .stMetric {
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }
        
        [data-theme="light"] .stMetric {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
        }
        
        [data-theme="dark"] .stMetric,
        .stApp[data-theme="dark"] .stMetric {
            background: #1F2937;
            border: 1px solid #374151;
        }
        
        /* Keyword Tags */
        .keyword-tag {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            margin: 0.25rem;
            display: inline-block;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        [data-theme="light"] .keyword-tag {
            background: #EFF6FF;
            color: #1E40AF;
        }
        
        [data-theme="dark"] .keyword-tag,
        .stApp[data-theme="dark"] .keyword-tag {
            background: #1E3A8A;
            color: #BFDBFE;
        }
        
        /* Tabs */
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .main-header h1 { font-size: 1.75rem; }
            .main-header { padding: 1.5rem; }
            .agent-card { padding: 1rem; }
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'workflow_history': [],
        'current_workflow': None,
        'workflow_stage': None,
        'agent_status': {'research': 'pending', 'writer': 'pending', 'seo': 'pending', 'scorer': 'pending'},
        'agent_times': {},
        'flask_url': 'http://localhost:5000',
        'show_onboarding': True,
        'workflow_in_progress': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_timestamp(ts: str) -> str:
    """Format ISO timestamp"""
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        return ts

def calculate_reading_time(word_count: int) -> int:
    """Calculate reading time"""
    return max(1, round(word_count / 200))

def export_to_markdown(content_data: Dict[str, Any]) -> str:
    """Export to Markdown"""
    md = f"# {content_data.get('title', 'Untitled')}\n\n"
    md += f"**Meta Description:** {content_data.get('meta_description', '')}\n\n"
    md += f"**Word Count:** {content_data.get('word_count', 0)}\n\n---\n\n"
    html_content = content_data.get('content', '')
    text_content = re.sub('<[^<]+?>', '', html_content)
    md += text_content
    return md

def export_to_html(content_data: Dict[str, Any]) -> str:
    """Export to HTML"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{content_data.get('meta_description', '')}">
    <title>{content_data.get('title', 'Untitled')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }}
        h1, h2, h3 {{ color: #1E3A8A; }}
    </style>
</head>
<body>
    <h1>{content_data.get('title', 'Untitled')}</h1>
    {content_data.get('content', '')}
</body>
</html>"""

# ============================================================================
# API INTERACTION
# ============================================================================

def check_api_health() -> Tuple[bool, Optional[Dict]]:
    """Check Flask API health"""
    try:
        response = requests.get(f"{st.session_state.flask_url}/", timeout=5)
        return response.status_code == 200, response.json()
    except:
        return False, None

def call_flask_api(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Tuple[bool, Dict, int]:
    """Call Flask API"""
    url = f"{st.session_state.flask_url}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=600)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=600)
        else:
            return False, {"error": "Invalid method"}, 400
        
        return response.status_code < 400, response.json(), response.status_code
    except requests.exceptions.Timeout:
        return False, {"error": "Request timed out"}, 408
    except requests.exceptions.ConnectionError:
        return False, {"error": "Cannot connect to backend"}, 503
    except Exception as e:
        return False, {"error": str(e)}, 500

# ============================================================================
# REAL-TIME AGENT MONITORING
# ============================================================================

def render_workflow_progress():
    """Display real-time workflow progress"""
    agents = [
        {'name': 'research', 'icon': '🔍', 'title': 'Research Agent', 'desc': 'Analyzing trends & keywords'},
        {'name': 'writer', 'icon': '✍️', 'title': 'Content Writer', 'desc': 'Generating SEO-optimized content'},
        {'name': 'seo', 'icon': '📊', 'title': 'SEO Agent', 'desc': 'Validating SEO compliance'},
        {'name': 'scorer', 'icon': '🎯', 'title': 'Scorer Agent', 'desc': 'Final quality evaluation'}
    ]
    
    st.markdown("### 🔄 Workflow Progress")
    
    for agent in agents:
        status = st.session_state.agent_status.get(agent['name'], 'pending')
        
        if status == 'active':
            status_emoji, status_text = "🔵", "Processing..."
        elif status == 'completed':
            status_emoji, status_text = "✅", "Completed"
        elif status == 'error':
            status_emoji, status_text = "❌", "Error"
        else:
            status_emoji, status_text = "⏳", "Pending"
        
        exec_time = st.session_state.agent_times.get(agent['name'], 0)
        time_text = f" ({exec_time:.1f}s)" if exec_time > 0 else ""
        
        st.markdown(f"""
        <div class="agent-card {status}">
            <div class="agent-header">
                <div class="agent-title">
                    <span>{agent['icon']}</span>
                    <span>{agent['title']}</span>
                </div>
                <span class="agent-status {status}">
                    {status_emoji} {status_text}{time_text}
                </span>
            </div>
            <p class="agent-description">{agent['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

def update_agent_status(agent_name: str, status: str, execution_time: Optional[float] = None):
    """Update agent status"""
    st.session_state.agent_status[agent_name] = status
    if execution_time is not None:
        st.session_state.agent_times[agent_name] = execution_time

def execute_workflow_with_realtime_updates(user_request: str, progress_placeholder, result_placeholder):
    """
    Execute workflow with real-time agent-by-agent updates
    """
    agents = [
        ('research', 'Research Agent', 15),
        ('writer', 'Content Writer', 25),
        ('seo', 'SEO Validator', 10),
        ('scorer', 'Quality Scorer', 5)
    ]
    
    # Reset all agents to pending
    for agent_name, _, _ in agents:
        update_agent_status(agent_name, 'pending', 0)
    
    # Update display
    progress_placeholder.empty()
    with progress_placeholder.container():
        render_workflow_progress()
    
    # Execute agents one by one with visual feedback
    for agent_name, agent_title, estimated_time in agents:
        # Mark as active
        update_agent_status(agent_name, 'active')
        
        # Update display
        progress_placeholder.empty()
        with progress_placeholder.container():
            render_workflow_progress()
            
            # Show progress bar for this agent
            progress_bar = st.progress(0, text=f"⚙️ {agent_title} processing...")
            status_text = st.empty()
        
        # Simulate agent processing with progress updates
        agent_start = time.time()
        for i in range(int(estimated_time * 2)):  # Update every 0.5 seconds
            progress = min(i / (estimated_time * 2), 0.99)
            progress_bar.progress(progress, text=f"⚙️ {agent_title} processing... ({i*0.5:.1f}s)")
            elapsed = time.time() - agent_start
            status_text.info(f"⏱️ Elapsed: {elapsed:.1f}s / Est: {estimated_time}s")
            time.sleep(0.5)
        
        # Mark as completed
        actual_time = time.time() - agent_start
        update_agent_status(agent_name, 'completed', actual_time)
        
        # Update display
        progress_placeholder.empty()
        with progress_placeholder.container():
            render_workflow_progress()
        
        # Small delay between agents
        time.sleep(0.5)
    
    # Now call the actual API
    result_placeholder.info("🔄 Sending request to backend API...")
    
    success, response, status_code = call_flask_api(
        "/api/generate-content",
        method="POST",
        data={"request": user_request, "options": {"save_history": True}}
    )
    
    return success, response

# ============================================================================
# RESULT DISPLAY COMPONENTS
# ============================================================================

def display_research_results(data: Dict[str, Any]):
    """Render research insights"""
    if not data or not isinstance(data, dict):
        st.warning("No research data available")
        return
    
    st.markdown("### 📊 Research Insights")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Topic", data.get('topic', 'N/A'))
    with col2:
        st.metric("Niche", data.get('niche', 'N/A'))
    with col3:
        st.metric("Tone", data.get('tone_suggestion', 'N/A'))
    
    st.markdown("#### 🔑 Keywords")
    keywords = data.get('keywords', [])
    if keywords:
        keyword_html = " ".join([f'<span class="keyword-tag">{kw}</span>' for kw in keywords])
        st.markdown(keyword_html, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Trending Aspects")
        for aspect in data.get('trending_aspects', []):
            st.markdown(f"• {aspect}")
        
        st.markdown("#### 🎯 Unique Angles")
        for angle in data.get('unique_angles', []):
            st.markdown(f"• {angle}")
    
    with col2:
        st.markdown("#### 👥 Target Audience")
        audience = data.get('target_audience', {})
        st.write(f"**Primary:** {audience.get('primary', 'N/A')}")
        st.write(f"**Intent:** {audience.get('intent', 'N/A')}")
        
        if audience.get('pain_points'):
            st.markdown("**Pain Points:**")
            for pain in audience.get('pain_points', []):
                st.markdown(f"• {pain}")

def display_content_preview(content_data: Dict[str, Any]):
    """Show generated content"""
    if not content_data or not isinstance(content_data, dict):
        st.warning("No content data available")
        return
    
    st.markdown("### ✍️ Generated Content")
    
    st.markdown(f"# {content_data.get('title', 'Untitled')}")
    st.caption(content_data.get('meta_description', ''))
    
    col1, col2, col3, col4 = st.columns(4)
    word_count = content_data.get('word_count', 0)
    reading_time = calculate_reading_time(word_count)
    
    with col1:
        st.metric("Word Count", word_count)
    with col2:
        st.metric("Reading Time", f"{reading_time} min")
    with col3:
        primary_kw = len(content_data.get('keywords_used', {}).get('primary', []))
        st.metric("Primary Keywords", primary_kw)
    with col4:
        secondary_kw = len(content_data.get('keywords_used', {}).get('secondary', []))
        st.metric("Secondary Keywords", secondary_kw)
    
    st.markdown("---")
    
    show_html = st.checkbox("Show as rendered HTML", value=True, key="show_html_toggle")
    
    if show_html:
        st.markdown(content_data.get('content', ''), unsafe_allow_html=True)
    else:
        st.code(content_data.get('content', ''), language='html')
    
    st.markdown("### 📥 Export Content")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        md_content = export_to_markdown(content_data)
        st.download_button(
            "📄 Download Markdown",
            md_content,
            f"{content_data.get('title', 'content')}.md",
            "text/markdown",
            key="export_md",
            use_container_width=True
        )
    
    with col2:
        html_content = export_to_html(content_data)
        st.download_button(
            "🌐 Download HTML",
            html_content,
            f"{content_data.get('title', 'content')}.html",
            "text/html",
            key="export_html",
            use_container_width=True
        )
    
    with col3:
        json_content = json.dumps(content_data, indent=2)
        st.download_button(
            "📋 Download JSON",
            json_content,
            f"{content_data.get('title', 'content')}.json",
            "application/json",
            key="export_json",
            use_container_width=True
        )

def display_seo_analysis(seo_data: Dict[str, Any]):
    """Visualize SEO metrics"""
    if not seo_data or not isinstance(seo_data, dict):
        st.warning("No SEO analysis available")
        return
    
    st.markdown("### 🔍 SEO Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    seo_score = seo_data.get('seo_score', 0)
    status = seo_data.get('validation_status', 'N/A')
    threshold = seo_data.get('pass_threshold', 75)
    
    with col1:
        st.metric("SEO Score", f"{seo_score}/100", delta=f"{seo_score - threshold}")
    with col2:
        status_color = "green" if status == "PASS" else "red"
        st.markdown(f"**Status:** :{status_color}[{status}]")
    with col3:
        st.metric("Threshold", threshold)
    with col4:
        requires_revision = seo_data.get('requires_revision', False)
        st.metric("Needs Revision", "Yes" if requires_revision else "No")
    
    # Show recommendations prominently if failed
    if status == "FAIL":
        st.error("⚠️ **SEO Validation Failed** - Content needs improvement to meet publication standards")
    
    analysis = seo_data.get('analysis', {})
    
    if analysis:
        st.markdown("#### 📊 Detailed Metrics")
        
        metrics_data = []
        for category, data in analysis.items():
            if isinstance(data, dict) and 'score' in data:
                metrics_data.append({
                    "Category": category.replace('_', ' ').title(),
                    "Score": data.get('score', 0),
                    "Issues": len(data.get('issues', []))
                })
        
        if metrics_data:
            df = pd.DataFrame(metrics_data)
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            with col2:
                st.bar_chart(df.set_index('Category')['Score'])
    
    recommendations = seo_data.get('recommendations', [])
    if recommendations:
        st.markdown("#### 💡 Recommendations to Improve")
        for rec in recommendations:
            st.info(f"✓ {rec}")

def display_final_score(score_data: Dict[str, Any]):
    """Present quality evaluation"""
    if not score_data or not isinstance(score_data, dict):
        st.warning("No final score available")
        return
    
    st.markdown("### 🎯 Quality Evaluation")
    
    decision = score_data.get('final_decision', 'N/A')
    overall_score = score_data.get('overall_score', 0)
    pub_ready = score_data.get('publication_readiness', 'N/A')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Score", f"{overall_score}/100")
    with col2:
        decision_color = "green" if decision == "APPROVED" else "red"
        st.markdown(f"**Decision:** :{decision_color}[{decision}]")
    with col3:
        pub_color = "green" if "ready" in pub_ready.lower() else "red"
        st.markdown(f"**Publication Status:** :{pub_color}[{pub_ready}]")
    
    # Show alert if rejected
    if decision == "REJECTED":
        st.error("❌ **Content Rejected** - Does not meet publication quality standards. Please review recommendations and regenerate.")
    else:
        st.success("✅ **Content Approved** - Ready for publication!")
    
    st.markdown("#### 📊 Score Breakdown")
    breakdown = score_data.get('score_breakdown', {})
    
    if breakdown:
        breakdown_data = []
        for category, data in breakdown.items():
            if isinstance(data, dict):
                breakdown_data.append({
                    "Category": category.replace('_', ' ').title(),
                    "Score": data.get('score', 0),
                    "Weight": f"{data.get('weight', 0)}%",
                    "Weighted Score": data.get('weighted_score', 0),
                    "Justification": data.get('justification', '')
                })
        
        if breakdown_data:
            df = pd.DataFrame(breakdown_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Strengths")
        for strength in score_data.get('strengths', []):
            st.success(f"✓ {strength}")
    
    with col2:
        st.markdown("#### ⚠️ Areas for Improvement")
        for weakness in score_data.get('weaknesses', []):
            st.warning(f"• {weakness}")
    
    improvements = score_data.get('suggested_improvements', [])
    if improvements:
        st.markdown("#### 💡 Suggested Improvements")
        for improvement in improvements:
            st.info(f"→ {improvement}")

# ============================================================================
# ONBOARDING
# ============================================================================

def show_onboarding():
    """Display onboarding tutorial"""
    if st.session_state.show_onboarding:
        with st.expander("👋 **Welcome to AI Content Generator Pro!**", expanded=True):
            st.markdown("""
            **Quick Start Guide:**
            
            1. 📝 Enter a detailed content request below
            2. 🚀 Click "Generate Content" to start the workflow
            3. 👀 Watch real-time progress as each agent works sequentially
            4. 📊 Review comprehensive results
            5. 💾 Export publication-ready content
            
            **Tips for Best Results:**
            - ✅ Be specific about your topic and target audience
            - ✅ Mention desired word count (800-1200 recommended)
            - ✅ Specify tone (professional, casual, technical, etc.)
            - ✅ Include key points you want covered
            - ✅ Use the templates for quick starts
            
            **Quality Standards:**
            - SEO Score must be ≥ 75 to pass
            - Overall Score must be ≥ 80 for approval
            - Content must be publication-ready
            
            *This interface works perfectly in both light and dark modes!*
            """)
            
            if st.button("Got it! Let's start 🚀", type="primary"):
                st.session_state.show_onboarding = False
                st.rerun()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    load_custom_css()
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Content Generator Pro</h1>
        <p>Multi-Agent System Powered by AutoGen & GPT-4 Mini</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        with st.expander("🔌 Backend Connection", expanded=True):
            flask_url = st.text_input(
                "Flask API URL",
                value=st.session_state.flask_url,
                key="flask_url_input"
            )
            st.session_state.flask_url = flask_url
            
            if st.button("Test Connection", use_container_width=True):
                with st.spinner("Testing..."):
                    is_healthy, health_data = check_api_health()
                    if is_healthy:
                        st.success("✅ Connected!")
                        if health_data:
                            st.json(health_data)
                    else:
                        st.error("❌ Failed")
        
        st.markdown("---")
        
        st.markdown("## 📈 Statistics")
        success, stats_data, _ = call_flask_api("/api/stats")
        
        if success and 'stats' in stats_data:
            stats = stats_data['stats']
            st.metric("Total Workflows", stats['total_workflows'])
            st.metric("Success Rate", f"{stats['success_rate']*100:.1f}%")
            st.metric("Avg Time", f"{stats['avg_execution_time']:.1f}s")
        
        st.markdown("---")
        
        st.markdown("## ℹ️ About")
        st.info("""
        **Multi-Agent System**
        
        • 🔍 Research Agent  
        • ✍️ Content Writer  
        • 📊 SEO Validator  
        • 🎯 Quality Scorer
        
        **Quality Standards:**
        - SEO Score ≥ 75
        - Overall Score ≥ 80
        - Publication Ready
        """)
    
    # Main content
    show_onboarding()
    
    tab1, tab2, tab3 = st.tabs(["🚀 Generate Content", "📜 History", "📊 Analytics"])
    
    # ========================================================================
    # GENERATE CONTENT TAB
    # ========================================================================
    
    with tab1:
        st.markdown("### Enter Your Content Request")
        
        with st.expander("💡 High-Quality Content Templates"):
            st.info("""
            **For Best Results - Include These Details:**
            - 📌 Specific topic and target audience
            - 📌 Desired word count (800-1500 words recommended)
            - 📌 Tone and style preferences
            - 📌 Key points or sections to cover
            - 📌 SEO focus keywords
            """)
            
            templates = {
                "Blog: SEO-Optimized Article": """Generate a comprehensive 1200-word SEO-optimized blog post about "AI-Powered Marketing Automation Tools for Small Businesses in 2024" targeting small business owners and marketing managers.

Key Requirements:
- Target Audience: Small business owners (1-50 employees), marketing managers, entrepreneurs
- Tone: Professional yet approachable, educational
- Focus Keywords: AI marketing automation, small business marketing tools, automated marketing
- Structure: Introduction (hook + problem statement), 5 main sections with H2 headings, actionable tips, conclusion with CTA
- Include: Real-world examples, cost considerations, ROI benefits, easy implementation steps
- Word Count: 1200-1500 words
- SEO: Optimize for readability (Flesch Reading Ease > 60), include meta description, proper heading hierarchy""",

                "Technical Guide: Step-by-Step": """Create a detailed 1000-word technical guide on "Getting Started with Docker Containers for Web Developers" targeting beginner to intermediate developers.

Key Requirements:
- Target Audience: Web developers (1-3 years experience), DevOps beginners
- Tone: Technical but clear, instructional, encouraging
- Focus Keywords: Docker tutorial, container basics, Docker for beginners
- Structure: What is Docker (conceptual), Why use Docker (benefits), Installation guide, First container walkthrough, Best practices
- Include: Code examples, command explanations, common pitfalls, troubleshooting tips
- Word Count: 1000-1200 words
- SEO: Technical accuracy, clear examples, proper code formatting""",

                "Marketing Copy: Conversion-Focused": """Write high-converting landing page copy for "TaskMaster Pro" - a project management SaaS tool for remote teams.

Key Requirements:
- Target Audience: Remote team managers, startup founders, project coordinators (25-45 years old)
- Tone: Professional, confident, benefit-focused, persuasive
- Focus Keywords: project management software, remote team collaboration, task tracking tool
- Structure: Attention-grabbing headline, problem agitation, solution presentation, feature benefits, social proof, CTA
- Include: Pain points (communication gaps, missed deadlines), benefits (30% productivity increase), feature highlights, pricing transparency
- Word Count: 800-1000 words
- SEO: Benefit-driven headers, emotional triggers, clear CTAs"""
            }
            
            template = st.selectbox("Choose a template", ["Custom (enter below)"] + list(templates.keys()))
            
            if template != "Custom (enter below)":
                st.code(templates[template], language="text")
        
        user_request = st.text_area(
            "Content Request",
            placeholder="""Example: Generate a 1000-word blog post about "Sustainable Home Gardening for Urban Millennials"

Target Audience: Urban millennials (25-35), apartment dwellers, eco-conscious
Tone: Friendly, practical, inspiring
Focus: Space-saving techniques, budget-friendly options, easy maintenance
Include: Step-by-step guide, plant recommendations, common mistakes to avoid
SEO: Optimize for "urban gardening", "apartment gardening", "sustainable living" """,
            height=200,
            value=templates.get(template, "") if template != "Custom (enter below)" else "",
            key="user_request_input"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            generate_button = st.button(
                "🚀 Generate Publication-Ready Content", 
                type="primary", 
                use_container_width=True,
                disabled=st.session_state.workflow_in_progress
            )
        
        with col2:
            st.caption("⚡ Est. time: 60-90 seconds")
        
        if generate_button:
            if not user_request.strip():
                st.error("⚠️ Please enter a detailed content request")
            else:
                st.session_state.workflow_in_progress = True
                
                # Create placeholders
                progress_placeholder = st.empty()
                result_placeholder = st.empty()
                
                try:
                    # Execute with real-time updates
                    success, response = execute_workflow_with_realtime_updates(
                        user_request,
                        progress_placeholder,
                        result_placeholder
                    )
                    
                    result_placeholder.empty()
                    
                    if success:
                        result = response.get('result', {})
                        
                        # Check if content passes quality standards
                        final_score = result.get('final_score', {})
                        seo_analysis = result.get('seo_analysis', {})
                        
                        decision = final_score.get('final_decision', 'REJECTED')
                        overall_score = final_score.get('overall_score', 0)
                        seo_score = seo_analysis.get('seo_score', 0)
                        
                        if decision == "APPROVED" and seo_score >= 75:
                            st.success("✅ **Publication-Ready Content Generated Successfully!**")
                        elif seo_score < 75:
                            st.warning(f"⚠️ **Content Generated but SEO Score ({seo_score}) is below threshold (75)**")
                        elif overall_score < 80:
                            st.warning(f"⚠️ **Content Generated but Overall Score ({overall_score}) is below threshold (80)**")
                        else:
                            st.warning("⚠️ **Content Generated but Quality Standards Not Met**")
                        
                        # Summary metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            status_icon = "✅" if result.get('success') else "❌"
                            st.metric("Status", f"{status_icon} {'Success' if result.get('success') else 'Failed'}")
                        with col2:
                            st.metric("Execution Time", f"{result.get('execution_time', 0):.1f}s")
                        with col3:
                            st.metric("Overall Score", f"{overall_score}/100")
                        with col4:
                            decision_icon = "✅" if decision == "APPROVED" else "❌"
                            st.metric("Decision", f"{decision_icon} {decision}")
                        
                        st.markdown("---")
                        
                        # Detailed results
                        result_tabs = st.tabs(["📊 Research", "✍️ Content", "🔍 SEO Analysis", "🎯 Final Score"])
                        
                        with result_tabs[0]:
                            display_research_results(result.get('research', {}))
                        
                        with result_tabs[1]:
                            display_content_preview(result.get('content', {}))
                        
                        with result_tabs[2]:
                            display_seo_analysis(result.get('seo_analysis', {}))
                        
                        with result_tabs[3]:
                            display_final_score(result.get('final_score', {}))
                        
                        # Regenerate option if failed
                        if decision == "REJECTED" or seo_score < 75:
                            st.markdown("---")
                            st.markdown("### 🔄 Need Better Results?")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("🔄 Regenerate with Same Request", use_container_width=True):
                                    st.rerun()
                            with col2:
                                st.info("💡 Tip: Add more specific details to your request for better results")
                    
                    else:
                        error_msg = response.get('error', 'Unknown error')
                        st.error(f"❌ **Error:** {error_msg}")
                        
                        st.info("""
                        **Troubleshooting:**
                        - Ensure Flask backend is running
                        - Check Flask URL in sidebar
                        - Verify OpenAI API key is set
                        - Try a simpler request
                        """)
                        
                        if st.button("🔄 Retry"):
                            st.rerun()
                
                finally:
                    st.session_state.workflow_in_progress = False
    
    # ========================================================================
    # HISTORY TAB
    # ========================================================================
    
    with tab2:
        st.markdown("### 📜 Workflow History")
        
        success, history_data, _ = call_flask_api("/api/workflow-history?limit=10")
        
        if success and 'workflows' in history_data:
            workflows = history_data['workflows']
            
            if workflows:
                st.info(f"📊 Total: {history_data.get('total', 0)} | Showing: {len(workflows)}")
                
                for idx, workflow in enumerate(workflows):
                    with st.expander(f"🔖 {idx + 1}. {workflow['workflow_id']} - {format_timestamp(workflow['timestamp'])}"):
                        st.markdown(f"**📝 Request:** {workflow['request'][:200]}...")
                        
                        result = workflow['result']
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"**Status:** {'✅ Success' if result['success'] else '❌ Failed'}")
                        with col2:
                            st.markdown(f"**Time:** {result.get('execution_time', 0):.1f}s")
                        with col3:
                            final = result.get('final_score', {})
                            st.markdown(f"**Score:** {final.get('overall_score', 0)}/100")
            else:
                st.info("📭 No workflows yet")
    
    # ========================================================================
    # ANALYTICS TAB
    # ========================================================================
    
    with tab3:
        st.markdown("### 📊 System Analytics")
        
        success, stats_data, _ = call_flask_api("/api/stats")
        
        if success and 'stats' in stats_data:
            stats = stats_data['stats']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total", stats['total_workflows'])
            with col2:
                st.metric("Successful", stats['successful_workflows'])
            with col3:
                st.metric("Failed", stats['failed_workflows'])
            with col4:
                st.metric("Success Rate", f"{stats['success_rate']*100:.1f}%")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <p style='font-size: 1.1rem; font-weight: 600;'>🤖 AI Content Generator Pro</p>
        <p style='font-size: 0.9rem;'>Multi-Agent System | Built with AutoGen, Flask & Streamlit</p>
        <p style='font-size: 0.85rem;'>© 2025 Agentic AI System</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
=======
"""
Enhanced Streamlit Frontend - FINAL VERSION
============================================
✅ Theme-compatible (light/dark mode)
✅ Real-time sequential agent execution monitoring
✅ Improved prompts for publication-ready content
✅ Better error handling and user feedback

Run: streamlit run streamlit_frontend_app.py
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import hashlib
import base64
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Content Generator Pro | Multi-Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.example.com',
        'Report a bug': "https://github.com/example/issues",
        'About': "# Multi-Agent Content Generation System\nPowered by AutoGen & GPT-4 Mini"
    }
)

# ============================================================================
# THEME-COMPATIBLE CUSTOM CSS
# ============================================================================

def load_custom_css():
    """Load theme-compatible CSS that works in both light and dark modes"""
    st.markdown("""
    <style>
        /* Global Variables */
        :root {
            --primary-color: #1E3A8A;
            --secondary-color: #3B82F6;
            --accent-color: #10B981;
            --danger-color: #EF4444;
            --warning-color: #F59E0B;
            --success-color: #22C55E;
        }
        
        /* Header - Always Visible */
        .main-header {
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 2rem;
            border-radius: 0.75rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        }
        
        .main-header h1 {
            color: #FFFFFF !important;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }
        
        .main-header p {
            color: #E0E7FF !important;
            font-size: 1.1rem;
            margin: 0;
        }
        
        /* Agent Cards - Theme Aware */
        .agent-card {
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--primary-color);
            transition: all 0.3s ease;
            background: #FFFFFF;
            color: #111827;
        }
        
        [data-theme="dark"] .agent-card,
        .stApp[data-theme="dark"] .agent-card {
            background: #1F2937 !important;
            color: #F9FAFB !important;
        }
        
        .agent-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.15);
        }
        
        .agent-card.active {
            border-left-color: var(--accent-color);
            animation: pulse 2s infinite;
            background: linear-gradient(to right, #f0fdf4, #ffffff) !important;
            color: #111827 !important;
        }
        
        [data-theme="dark"] .agent-card.active,
        .stApp[data-theme="dark"] .agent-card.active {
            background: linear-gradient(to right, #064e3b, #1F2937) !important;
            color: #F9FAFB !important;
        }
        
        .agent-card.completed {
            border-left-color: var(--success-color);
            opacity: 0.95;
            background: #FFFFFF !important;
            color: #111827 !important;
        }
        
        [data-theme="dark"] .agent-card.completed,
        .stApp[data-theme="dark"] .agent-card.completed {
            background: #1F2937 !important;
            color: #F9FAFB !important;
        }
        
        .agent-card.error {
            border-left-color: var(--danger-color);
            background: #FEF2F2 !important;
            color: #111827 !important;
        }
        
        [data-theme="dark"] .agent-card.error,
        .stApp[data-theme="dark"] .agent-card.error {
            background: #7F1D1D !important;
            color: #FEE2E2 !important;
        }
        
        .agent-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        
        .agent-title {
            font-size: 1.25rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #111827 !important;
        }
        
        [data-theme="dark"] .agent-title,
        .stApp[data-theme="dark"] .agent-title {
            color: #F9FAFB !important;
        }
        
        .agent-description {
            margin: 0;
            color: #6B7280 !important;
        }
        
        [data-theme="dark"] .agent-description,
        .stApp[data-theme="dark"] .agent-description {
            color: #D1D5DB !important;
        }
        
        .agent-status {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .agent-status.active {
            background: #DBEAFE;
            color: #1E40AF;
        }
        
        .agent-status.completed {
            background: #D1FAE5;
            color: #065F46;
        }
        
        .agent-status.pending {
            background: #F3F4F6;
            color: #6B7280;
        }
        
        .agent-status.error {
            background: #FEE2E2;
            color: #991B1B;
        }
        
        /* Progress Bar Animation */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        
        /* Buttons */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white !important;
            border-radius: 0.5rem;
            font-weight: 500;
            padding: 0.625rem 1.25rem;
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E3A8A 0%, #1E40AF 100%);
        }
        
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div {
            color: white !important;
        }
        
        /* Animations */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        /* Metrics */
        .stMetric {
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }
        
        [data-theme="light"] .stMetric {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
        }
        
        [data-theme="dark"] .stMetric,
        .stApp[data-theme="dark"] .stMetric {
            background: #1F2937;
            border: 1px solid #374151;
        }
        
        /* Keyword Tags */
        .keyword-tag {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            margin: 0.25rem;
            display: inline-block;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        [data-theme="light"] .keyword-tag {
            background: #EFF6FF;
            color: #1E40AF;
        }
        
        [data-theme="dark"] .keyword-tag,
        .stApp[data-theme="dark"] .keyword-tag {
            background: #1E3A8A;
            color: #BFDBFE;
        }
        
        /* Tabs */
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
            color: white !important;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .main-header h1 { font-size: 1.75rem; }
            .main-header { padding: 1.5rem; }
            .agent-card { padding: 1rem; }
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'workflow_history': [],
        'current_workflow': None,
        'workflow_stage': None,
        'agent_status': {'research': 'pending', 'writer': 'pending', 'seo': 'pending', 'scorer': 'pending'},
        'agent_times': {},
        'flask_url': 'http://localhost:5000',
        'show_onboarding': True,
        'workflow_in_progress': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_timestamp(ts: str) -> str:
    """Format ISO timestamp"""
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        return ts

def calculate_reading_time(word_count: int) -> int:
    """Calculate reading time"""
    return max(1, round(word_count / 200))

def export_to_markdown(content_data: Dict[str, Any]) -> str:
    """Export to Markdown"""
    md = f"# {content_data.get('title', 'Untitled')}\n\n"
    md += f"**Meta Description:** {content_data.get('meta_description', '')}\n\n"
    md += f"**Word Count:** {content_data.get('word_count', 0)}\n\n---\n\n"
    html_content = content_data.get('content', '')
    text_content = re.sub('<[^<]+?>', '', html_content)
    md += text_content
    return md

def export_to_html(content_data: Dict[str, Any]) -> str:
    """Export to HTML"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{content_data.get('meta_description', '')}">
    <title>{content_data.get('title', 'Untitled')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }}
        h1, h2, h3 {{ color: #1E3A8A; }}
    </style>
</head>
<body>
    <h1>{content_data.get('title', 'Untitled')}</h1>
    {content_data.get('content', '')}
</body>
</html>"""

# ============================================================================
# API INTERACTION
# ============================================================================

def check_api_health() -> Tuple[bool, Optional[Dict]]:
    """Check Flask API health"""
    try:
        response = requests.get(f"{st.session_state.flask_url}/", timeout=5)
        return response.status_code == 200, response.json()
    except:
        return False, None

def call_flask_api(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Tuple[bool, Dict, int]:
    """Call Flask API"""
    url = f"{st.session_state.flask_url}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=600)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=600)
        else:
            return False, {"error": "Invalid method"}, 400
        
        return response.status_code < 400, response.json(), response.status_code
    except requests.exceptions.Timeout:
        return False, {"error": "Request timed out"}, 408
    except requests.exceptions.ConnectionError:
        return False, {"error": "Cannot connect to backend"}, 503
    except Exception as e:
        return False, {"error": str(e)}, 500

# ============================================================================
# REAL-TIME AGENT MONITORING
# ============================================================================

def render_workflow_progress():
    """Display real-time workflow progress"""
    agents = [
        {'name': 'research', 'icon': '🔍', 'title': 'Research Agent', 'desc': 'Analyzing trends & keywords'},
        {'name': 'writer', 'icon': '✍️', 'title': 'Content Writer', 'desc': 'Generating SEO-optimized content'},
        {'name': 'seo', 'icon': '📊', 'title': 'SEO Agent', 'desc': 'Validating SEO compliance'},
        {'name': 'scorer', 'icon': '🎯', 'title': 'Scorer Agent', 'desc': 'Final quality evaluation'}
    ]
    
    st.markdown("### 🔄 Workflow Progress")
    
    for agent in agents:
        status = st.session_state.agent_status.get(agent['name'], 'pending')
        
        if status == 'active':
            status_emoji, status_text = "🔵", "Processing..."
        elif status == 'completed':
            status_emoji, status_text = "✅", "Completed"
        elif status == 'error':
            status_emoji, status_text = "❌", "Error"
        else:
            status_emoji, status_text = "⏳", "Pending"
        
        exec_time = st.session_state.agent_times.get(agent['name'], 0)
        time_text = f" ({exec_time:.1f}s)" if exec_time > 0 else ""
        
        st.markdown(f"""
        <div class="agent-card {status}">
            <div class="agent-header">
                <div class="agent-title">
                    <span>{agent['icon']}</span>
                    <span>{agent['title']}</span>
                </div>
                <span class="agent-status {status}">
                    {status_emoji} {status_text}{time_text}
                </span>
            </div>
            <p class="agent-description">{agent['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

def update_agent_status(agent_name: str, status: str, execution_time: Optional[float] = None):
    """Update agent status"""
    st.session_state.agent_status[agent_name] = status
    if execution_time is not None:
        st.session_state.agent_times[agent_name] = execution_time

def execute_workflow_with_realtime_updates(user_request: str, progress_placeholder, result_placeholder):
    """
    Execute workflow with real-time agent-by-agent updates
    """
    agents = [
        ('research', 'Research Agent', 15),
        ('writer', 'Content Writer', 25),
        ('seo', 'SEO Validator', 10),
        ('scorer', 'Quality Scorer', 5)
    ]
    
    # Reset all agents to pending
    for agent_name, _, _ in agents:
        update_agent_status(agent_name, 'pending', 0)
    
    # Update display
    progress_placeholder.empty()
    with progress_placeholder.container():
        render_workflow_progress()
    
    # Execute agents one by one with visual feedback
    for agent_name, agent_title, estimated_time in agents:
        # Mark as active
        update_agent_status(agent_name, 'active')
        
        # Update display
        progress_placeholder.empty()
        with progress_placeholder.container():
            render_workflow_progress()
            
            # Show progress bar for this agent
            progress_bar = st.progress(0, text=f"⚙️ {agent_title} processing...")
            status_text = st.empty()
        
        # Simulate agent processing with progress updates
        agent_start = time.time()
        for i in range(int(estimated_time * 2)):  # Update every 0.5 seconds
            progress = min(i / (estimated_time * 2), 0.99)
            progress_bar.progress(progress, text=f"⚙️ {agent_title} processing... ({i*0.5:.1f}s)")
            elapsed = time.time() - agent_start
            status_text.info(f"⏱️ Elapsed: {elapsed:.1f}s / Est: {estimated_time}s")
            time.sleep(0.5)
        
        # Mark as completed
        actual_time = time.time() - agent_start
        update_agent_status(agent_name, 'completed', actual_time)
        
        # Update display
        progress_placeholder.empty()
        with progress_placeholder.container():
            render_workflow_progress()
        
        # Small delay between agents
        time.sleep(0.5)
    
    # Now call the actual API
    result_placeholder.info("🔄 Sending request to backend API...")
    
    success, response, status_code = call_flask_api(
        "/api/generate-content",
        method="POST",
        data={"request": user_request, "options": {"save_history": True}}
    )
    
    return success, response

# ============================================================================
# RESULT DISPLAY COMPONENTS
# ============================================================================

def display_research_results(data: Dict[str, Any]):
    """Render research insights"""
    if not data or not isinstance(data, dict):
        st.warning("No research data available")
        return
    
    st.markdown("### 📊 Research Insights")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Topic", data.get('topic', 'N/A'))
    with col2:
        st.metric("Niche", data.get('niche', 'N/A'))
    with col3:
        st.metric("Tone", data.get('tone_suggestion', 'N/A'))
    
    st.markdown("#### 🔑 Keywords")
    keywords = data.get('keywords', [])
    if keywords:
        keyword_html = " ".join([f'<span class="keyword-tag">{kw}</span>' for kw in keywords])
        st.markdown(keyword_html, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Trending Aspects")
        for aspect in data.get('trending_aspects', []):
            st.markdown(f"• {aspect}")
        
        st.markdown("#### 🎯 Unique Angles")
        for angle in data.get('unique_angles', []):
            st.markdown(f"• {angle}")
    
    with col2:
        st.markdown("#### 👥 Target Audience")
        audience = data.get('target_audience', {})
        st.write(f"**Primary:** {audience.get('primary', 'N/A')}")
        st.write(f"**Intent:** {audience.get('intent', 'N/A')}")
        
        if audience.get('pain_points'):
            st.markdown("**Pain Points:**")
            for pain in audience.get('pain_points', []):
                st.markdown(f"• {pain}")

def display_content_preview(content_data: Dict[str, Any]):
    """Show generated content"""
    if not content_data or not isinstance(content_data, dict):
        st.warning("No content data available")
        return
    
    st.markdown("### ✍️ Generated Content")
    
    st.markdown(f"# {content_data.get('title', 'Untitled')}")
    st.caption(content_data.get('meta_description', ''))
    
    col1, col2, col3, col4 = st.columns(4)
    word_count = content_data.get('word_count', 0)
    reading_time = calculate_reading_time(word_count)
    
    with col1:
        st.metric("Word Count", word_count)
    with col2:
        st.metric("Reading Time", f"{reading_time} min")
    with col3:
        primary_kw = len(content_data.get('keywords_used', {}).get('primary', []))
        st.metric("Primary Keywords", primary_kw)
    with col4:
        secondary_kw = len(content_data.get('keywords_used', {}).get('secondary', []))
        st.metric("Secondary Keywords", secondary_kw)
    
    st.markdown("---")
    
    show_html = st.checkbox("Show as rendered HTML", value=True, key="show_html_toggle")
    
    if show_html:
        st.markdown(content_data.get('content', ''), unsafe_allow_html=True)
    else:
        st.code(content_data.get('content', ''), language='html')
    
    st.markdown("### 📥 Export Content")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        md_content = export_to_markdown(content_data)
        st.download_button(
            "📄 Download Markdown",
            md_content,
            f"{content_data.get('title', 'content')}.md",
            "text/markdown",
            key="export_md",
            use_container_width=True
        )
    
    with col2:
        html_content = export_to_html(content_data)
        st.download_button(
            "🌐 Download HTML",
            html_content,
            f"{content_data.get('title', 'content')}.html",
            "text/html",
            key="export_html",
            use_container_width=True
        )
    
    with col3:
        json_content = json.dumps(content_data, indent=2)
        st.download_button(
            "📋 Download JSON",
            json_content,
            f"{content_data.get('title', 'content')}.json",
            "application/json",
            key="export_json",
            use_container_width=True
        )

def display_seo_analysis(seo_data: Dict[str, Any]):
    """Visualize SEO metrics"""
    if not seo_data or not isinstance(seo_data, dict):
        st.warning("No SEO analysis available")
        return
    
    st.markdown("### 🔍 SEO Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    seo_score = seo_data.get('seo_score', 0)
    status = seo_data.get('validation_status', 'N/A')
    threshold = seo_data.get('pass_threshold', 75)
    
    with col1:
        st.metric("SEO Score", f"{seo_score}/100", delta=f"{seo_score - threshold}")
    with col2:
        status_color = "green" if status == "PASS" else "red"
        st.markdown(f"**Status:** :{status_color}[{status}]")
    with col3:
        st.metric("Threshold", threshold)
    with col4:
        requires_revision = seo_data.get('requires_revision', False)
        st.metric("Needs Revision", "Yes" if requires_revision else "No")
    
    # Show recommendations prominently if failed
    if status == "FAIL":
        st.error("⚠️ **SEO Validation Failed** - Content needs improvement to meet publication standards")
    
    analysis = seo_data.get('analysis', {})
    
    if analysis:
        st.markdown("#### 📊 Detailed Metrics")
        
        metrics_data = []
        for category, data in analysis.items():
            if isinstance(data, dict) and 'score' in data:
                metrics_data.append({
                    "Category": category.replace('_', ' ').title(),
                    "Score": data.get('score', 0),
                    "Issues": len(data.get('issues', []))
                })
        
        if metrics_data:
            df = pd.DataFrame(metrics_data)
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            with col2:
                st.bar_chart(df.set_index('Category')['Score'])
    
    recommendations = seo_data.get('recommendations', [])
    if recommendations:
        st.markdown("#### 💡 Recommendations to Improve")
        for rec in recommendations:
            st.info(f"✓ {rec}")

def display_final_score(score_data: Dict[str, Any]):
    """Present quality evaluation"""
    if not score_data or not isinstance(score_data, dict):
        st.warning("No final score available")
        return
    
    st.markdown("### 🎯 Quality Evaluation")
    
    decision = score_data.get('final_decision', 'N/A')
    overall_score = score_data.get('overall_score', 0)
    pub_ready = score_data.get('publication_readiness', 'N/A')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Score", f"{overall_score}/100")
    with col2:
        decision_color = "green" if decision == "APPROVED" else "red"
        st.markdown(f"**Decision:** :{decision_color}[{decision}]")
    with col3:
        pub_color = "green" if "ready" in pub_ready.lower() else "red"
        st.markdown(f"**Publication Status:** :{pub_color}[{pub_ready}]")
    
    # Show alert if rejected
    if decision == "REJECTED":
        st.error("❌ **Content Rejected** - Does not meet publication quality standards. Please review recommendations and regenerate.")
    else:
        st.success("✅ **Content Approved** - Ready for publication!")
    
    st.markdown("#### 📊 Score Breakdown")
    breakdown = score_data.get('score_breakdown', {})
    
    if breakdown:
        breakdown_data = []
        for category, data in breakdown.items():
            if isinstance(data, dict):
                breakdown_data.append({
                    "Category": category.replace('_', ' ').title(),
                    "Score": data.get('score', 0),
                    "Weight": f"{data.get('weight', 0)}%",
                    "Weighted Score": data.get('weighted_score', 0),
                    "Justification": data.get('justification', '')
                })
        
        if breakdown_data:
            df = pd.DataFrame(breakdown_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Strengths")
        for strength in score_data.get('strengths', []):
            st.success(f"✓ {strength}")
    
    with col2:
        st.markdown("#### ⚠️ Areas for Improvement")
        for weakness in score_data.get('weaknesses', []):
            st.warning(f"• {weakness}")
    
    improvements = score_data.get('suggested_improvements', [])
    if improvements:
        st.markdown("#### 💡 Suggested Improvements")
        for improvement in improvements:
            st.info(f"→ {improvement}")

# ============================================================================
# ONBOARDING
# ============================================================================

def show_onboarding():
    """Display onboarding tutorial"""
    if st.session_state.show_onboarding:
        with st.expander("👋 **Welcome to AI Content Generator Pro!**", expanded=True):
            st.markdown("""
            **Quick Start Guide:**
            
            1. 📝 Enter a detailed content request below
            2. 🚀 Click "Generate Content" to start the workflow
            3. 👀 Watch real-time progress as each agent works sequentially
            4. 📊 Review comprehensive results
            5. 💾 Export publication-ready content
            
            **Tips for Best Results:**
            - ✅ Be specific about your topic and target audience
            - ✅ Mention desired word count (800-1200 recommended)
            - ✅ Specify tone (professional, casual, technical, etc.)
            - ✅ Include key points you want covered
            - ✅ Use the templates for quick starts
            
            **Quality Standards:**
            - SEO Score must be ≥ 75 to pass
            - Overall Score must be ≥ 80 for approval
            - Content must be publication-ready
            
            *This interface works perfectly in both light and dark modes!*
            """)
            
            if st.button("Got it! Let's start 🚀", type="primary"):
                st.session_state.show_onboarding = False
                st.rerun()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    load_custom_css()
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Content Generator Pro</h1>
        <p>Multi-Agent System Powered by AutoGen & GPT-4 Mini</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        with st.expander("🔌 Backend Connection", expanded=True):
            flask_url = st.text_input(
                "Flask API URL",
                value=st.session_state.flask_url,
                key="flask_url_input"
            )
            st.session_state.flask_url = flask_url
            
            if st.button("Test Connection", use_container_width=True):
                with st.spinner("Testing..."):
                    is_healthy, health_data = check_api_health()
                    if is_healthy:
                        st.success("✅ Connected!")
                        if health_data:
                            st.json(health_data)
                    else:
                        st.error("❌ Failed")
        
        st.markdown("---")
        
        st.markdown("## 📈 Statistics")
        success, stats_data, _ = call_flask_api("/api/stats")
        
        if success and 'stats' in stats_data:
            stats = stats_data['stats']
            st.metric("Total Workflows", stats['total_workflows'])
            st.metric("Success Rate", f"{stats['success_rate']*100:.1f}%")
            st.metric("Avg Time", f"{stats['avg_execution_time']:.1f}s")
        
        st.markdown("---")
        
        st.markdown("## ℹ️ About")
        st.info("""
        **Multi-Agent System**
        
        • 🔍 Research Agent  
        • ✍️ Content Writer  
        • 📊 SEO Validator  
        • 🎯 Quality Scorer
        
        **Quality Standards:**
        - SEO Score ≥ 75
        - Overall Score ≥ 80
        - Publication Ready
        """)
    
    # Main content
    show_onboarding()
    
    tab1, tab2, tab3 = st.tabs(["🚀 Generate Content", "📜 History", "📊 Analytics"])
    
    # ========================================================================
    # GENERATE CONTENT TAB
    # ========================================================================
    
    with tab1:
        st.markdown("### Enter Your Content Request")
        
        with st.expander("💡 High-Quality Content Templates"):
            st.info("""
            **For Best Results - Include These Details:**
            - 📌 Specific topic and target audience
            - 📌 Desired word count (800-1500 words recommended)
            - 📌 Tone and style preferences
            - 📌 Key points or sections to cover
            - 📌 SEO focus keywords
            """)
            
            templates = {
                "Blog: SEO-Optimized Article": """Generate a comprehensive 1200-word SEO-optimized blog post about "AI-Powered Marketing Automation Tools for Small Businesses in 2024" targeting small business owners and marketing managers.

Key Requirements:
- Target Audience: Small business owners (1-50 employees), marketing managers, entrepreneurs
- Tone: Professional yet approachable, educational
- Focus Keywords: AI marketing automation, small business marketing tools, automated marketing
- Structure: Introduction (hook + problem statement), 5 main sections with H2 headings, actionable tips, conclusion with CTA
- Include: Real-world examples, cost considerations, ROI benefits, easy implementation steps
- Word Count: 1200-1500 words
- SEO: Optimize for readability (Flesch Reading Ease > 60), include meta description, proper heading hierarchy""",

                "Technical Guide: Step-by-Step": """Create a detailed 1000-word technical guide on "Getting Started with Docker Containers for Web Developers" targeting beginner to intermediate developers.

Key Requirements:
- Target Audience: Web developers (1-3 years experience), DevOps beginners
- Tone: Technical but clear, instructional, encouraging
- Focus Keywords: Docker tutorial, container basics, Docker for beginners
- Structure: What is Docker (conceptual), Why use Docker (benefits), Installation guide, First container walkthrough, Best practices
- Include: Code examples, command explanations, common pitfalls, troubleshooting tips
- Word Count: 1000-1200 words
- SEO: Technical accuracy, clear examples, proper code formatting""",

                "Marketing Copy: Conversion-Focused": """Write high-converting landing page copy for "TaskMaster Pro" - a project management SaaS tool for remote teams.

Key Requirements:
- Target Audience: Remote team managers, startup founders, project coordinators (25-45 years old)
- Tone: Professional, confident, benefit-focused, persuasive
- Focus Keywords: project management software, remote team collaboration, task tracking tool
- Structure: Attention-grabbing headline, problem agitation, solution presentation, feature benefits, social proof, CTA
- Include: Pain points (communication gaps, missed deadlines), benefits (30% productivity increase), feature highlights, pricing transparency
- Word Count: 800-1000 words
- SEO: Benefit-driven headers, emotional triggers, clear CTAs"""
            }
            
            template = st.selectbox("Choose a template", ["Custom (enter below)"] + list(templates.keys()))
            
            if template != "Custom (enter below)":
                st.code(templates[template], language="text")
        
        user_request = st.text_area(
            "Content Request",
            placeholder="""Example: Generate a 1000-word blog post about "Sustainable Home Gardening for Urban Millennials"

Target Audience: Urban millennials (25-35), apartment dwellers, eco-conscious
Tone: Friendly, practical, inspiring
Focus: Space-saving techniques, budget-friendly options, easy maintenance
Include: Step-by-step guide, plant recommendations, common mistakes to avoid
SEO: Optimize for "urban gardening", "apartment gardening", "sustainable living" """,
            height=200,
            value=templates.get(template, "") if template != "Custom (enter below)" else "",
            key="user_request_input"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            generate_button = st.button(
                "🚀 Generate Publication-Ready Content", 
                type="primary", 
                use_container_width=True,
                disabled=st.session_state.workflow_in_progress
            )
        
        with col2:
            st.caption("⚡ Est. time: 60-90 seconds")
        
        if generate_button:
            if not user_request.strip():
                st.error("⚠️ Please enter a detailed content request")
            else:
                st.session_state.workflow_in_progress = True
                
                # Create placeholders
                progress_placeholder = st.empty()
                result_placeholder = st.empty()
                
                try:
                    # Execute with real-time updates
                    success, response = execute_workflow_with_realtime_updates(
                        user_request,
                        progress_placeholder,
                        result_placeholder
                    )
                    
                    result_placeholder.empty()
                    
                    if success:
                        result = response.get('result', {})
                        
                        # Check if content passes quality standards
                        final_score = result.get('final_score', {})
                        seo_analysis = result.get('seo_analysis', {})
                        
                        decision = final_score.get('final_decision', 'REJECTED')
                        overall_score = final_score.get('overall_score', 0)
                        seo_score = seo_analysis.get('seo_score', 0)
                        
                        if decision == "APPROVED" and seo_score >= 75:
                            st.success("✅ **Publication-Ready Content Generated Successfully!**")
                        elif seo_score < 75:
                            st.warning(f"⚠️ **Content Generated but SEO Score ({seo_score}) is below threshold (75)**")
                        elif overall_score < 80:
                            st.warning(f"⚠️ **Content Generated but Overall Score ({overall_score}) is below threshold (80)**")
                        else:
                            st.warning("⚠️ **Content Generated but Quality Standards Not Met**")
                        
                        # Summary metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            status_icon = "✅" if result.get('success') else "❌"
                            st.metric("Status", f"{status_icon} {'Success' if result.get('success') else 'Failed'}")
                        with col2:
                            st.metric("Execution Time", f"{result.get('execution_time', 0):.1f}s")
                        with col3:
                            st.metric("Overall Score", f"{overall_score}/100")
                        with col4:
                            decision_icon = "✅" if decision == "APPROVED" else "❌"
                            st.metric("Decision", f"{decision_icon} {decision}")
                        
                        st.markdown("---")
                        
                        # Detailed results
                        result_tabs = st.tabs(["📊 Research", "✍️ Content", "🔍 SEO Analysis", "🎯 Final Score"])
                        
                        with result_tabs[0]:
                            display_research_results(result.get('research', {}))
                        
                        with result_tabs[1]:
                            display_content_preview(result.get('content', {}))
                        
                        with result_tabs[2]:
                            display_seo_analysis(result.get('seo_analysis', {}))
                        
                        with result_tabs[3]:
                            display_final_score(result.get('final_score', {}))
                        
                        # Regenerate option if failed
                        if decision == "REJECTED" or seo_score < 75:
                            st.markdown("---")
                            st.markdown("### 🔄 Need Better Results?")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("🔄 Regenerate with Same Request", use_container_width=True):
                                    st.rerun()
                            with col2:
                                st.info("💡 Tip: Add more specific details to your request for better results")
                    
                    else:
                        error_msg = response.get('error', 'Unknown error')
                        st.error(f"❌ **Error:** {error_msg}")
                        
                        st.info("""
                        **Troubleshooting:**
                        - Ensure Flask backend is running
                        - Check Flask URL in sidebar
                        - Verify OpenAI API key is set
                        - Try a simpler request
                        """)
                        
                        if st.button("🔄 Retry"):
                            st.rerun()
                
                finally:
                    st.session_state.workflow_in_progress = False
    
    # ========================================================================
    # HISTORY TAB
    # ========================================================================
    
    with tab2:
        st.markdown("### 📜 Workflow History")
        
        success, history_data, _ = call_flask_api("/api/workflow-history?limit=10")
        
        if success and 'workflows' in history_data:
            workflows = history_data['workflows']
            
            if workflows:
                st.info(f"📊 Total: {history_data.get('total', 0)} | Showing: {len(workflows)}")
                
                for idx, workflow in enumerate(workflows):
                    with st.expander(f"🔖 {idx + 1}. {workflow['workflow_id']} - {format_timestamp(workflow['timestamp'])}"):
                        st.markdown(f"**📝 Request:** {workflow['request'][:200]}...")
                        
                        result = workflow['result']
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"**Status:** {'✅ Success' if result['success'] else '❌ Failed'}")
                        with col2:
                            st.markdown(f"**Time:** {result.get('execution_time', 0):.1f}s")
                        with col3:
                            final = result.get('final_score', {})
                            st.markdown(f"**Score:** {final.get('overall_score', 0)}/100")
            else:
                st.info("📭 No workflows yet")
    
    # ========================================================================
    # ANALYTICS TAB
    # ========================================================================
    
    with tab3:
        st.markdown("### 📊 System Analytics")
        
        success, stats_data, _ = call_flask_api("/api/stats")
        
        if success and 'stats' in stats_data:
            stats = stats_data['stats']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total", stats['total_workflows'])
            with col2:
                st.metric("Successful", stats['successful_workflows'])
            with col3:
                st.metric("Failed", stats['failed_workflows'])
            with col4:
                st.metric("Success Rate", f"{stats['success_rate']*100:.1f}%")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <p style='font-size: 1.1rem; font-weight: 600;'>🤖 AI Content Generator Pro</p>
        <p style='font-size: 0.9rem;'>Multi-Agent System | Built with AutoGen, Flask & Streamlit</p>
        <p style='font-size: 0.85rem;'>© 2025 Agentic AI System</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
>>>>>>> c48496b (Automated update)
