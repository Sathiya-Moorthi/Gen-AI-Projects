<<<<<<< HEAD
"""
Production-Ready Content Workflow with SERP API Integration
============================================================
Enhanced prompts that enforce publication quality standards
Integrated web search for accurate, current information
"""

import os
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from autogen_core import (
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    message_handler,
    type_subscription,
)
from autogen_core.models import SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

class PublicationWorkflowConfig:
    """Enhanced configuration for publication-ready content"""
    OPENAI_MODEL = "gpt-4o-mini"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERP_API_KEY = os.getenv("SERP_API_KEY")  # Get from serpapi.com
    
    # Stricter thresholds for publication quality
    SEO_PASS_THRESHOLD = 80  # Increased from 75
    OVERALL_PASS_THRESHOLD = 85  # Increased from 80
    MIN_WORD_COUNT = 1000
    MAX_WORD_COUNT = 2000
    TARGET_READABILITY = 65  # Flesch Reading Ease
    
    # Topic identifiers
    TOPIC_RESEARCH = "ResearchAgent"
    TOPIC_WRITER = "ContentWriterAgent"
    TOPIC_SEO = "SEOAgent"
    TOPIC_SCORER = "ScorerAgent"
    TOPIC_OUTPUT = "OutputAgent"


# ============================================================================
# SERP API INTEGRATION
# ============================================================================

class SerpAPIResearcher:
    """Integrate real-world web search for accurate research"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
    
    def search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Perform web search using SERP API"""
        if not self.api_key:
            return {"error": "SERP API key not configured"}
        
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "engine": "google"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            results = {
                "organic_results": [],
                "related_searches": [],
                "people_also_ask": []
            }
            
            # Organic search results
            for result in data.get("organic_results", [])[:10]:
                results["organic_results"].append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0)
                })
            
            # Related searches
            for related in data.get("related_searches", [])[:5]:
                results["related_searches"].append(related.get("query", ""))
            
            # People also ask
            for paa in data.get("related_questions", [])[:5]:
                results["people_also_ask"].append({
                    "question": paa.get("question", ""),
                    "snippet": paa.get("snippet", "")
                })
            
            return results
            
        except Exception as e:
            return {"error": f"SERP API error: {str(e)}"}


# ============================================================================
# ENHANCED RESEARCH AGENT
# ============================================================================

@type_subscription(topic_type=PublicationWorkflowConfig.TOPIC_RESEARCH)
class EnhancedResearchAgent(RoutedAgent):
    """Research agent with SERP API integration for real-world data"""
    
    def __init__(self, model_client, serp_api_key: Optional[str] = None):
        super().__init__("research_agent")
        self._model_client = model_client
        self._serp_researcher = SerpAPIResearcher(serp_api_key) if serp_api_key else None
        
        self._system_message = SystemMessage(content="""
You are an EXPERT Content Research Analyst with 10+ years of experience in SEO, content strategy, and audience analysis.

**CRITICAL MISSION:** Provide research that will result in PUBLICATION-READY content scoring:
- SEO Score ≥ 80/100 (NOT 75, NOT 78 - MINIMUM 80)
- Overall Quality Score ≥ 85/100
- Flesch Reading Ease ≥ 65
- Publication Status: READY FOR PUBLICATION

**YOUR RESEARCH MUST ENSURE:**

1. **HIGH-VOLUME, LOW-COMPETITION KEYWORDS**
   - Primary keywords: 1000+ monthly searches, competition < 60
   - Include EXACT search volume data if available
   - Mix of short-tail (1-2 words) and long-tail (3-5 words) keywords
   - Include question-based keywords (who, what, where, why, how)

2. **TRENDING & CURRENT INFORMATION**
   - Focus on 2024-2025 trends and data
   - Include recent statistics, studies, case studies
   - Reference current industry leaders and examples
   - Note seasonal or timely aspects

3. **COMPREHENSIVE AUDIENCE RESEARCH**
   - Specific demographics (age, location, income, profession)
   - Detailed pain points (at least 5)
   - Search intent (informational, transactional, navigational)
   - Common questions and concerns
   - Preferred content formats

4. **COMPETITIVE GAPS & UNIQUE ANGLES**
   - What's missing from top-ranking content
   - Underserved subtopics or perspectives
   - Opportunities for original insights
   - Ways to stand out from competitors

5. **CONTENT STRUCTURE GUIDANCE**
   - Recommended word count: {min_words}-{max_words} words
   - Optimal heading structure (number of H2s, H3s)
   - Content depth requirements
   - Internal linking opportunities

**OUTPUT FORMAT (STRICT JSON):**
{{
  "topic": "Specific, SEO-optimized topic title",
  "niche": "Precise niche category",
  "keywords": {{
    "primary": ["keyword1 (5000/mo)", "keyword2 (3000/mo)"],
    "secondary": ["keyword3 (1000/mo)", "keyword4 (800/mo)"],
    "long_tail": ["specific phrase 1", "specific phrase 2"],
    "questions": ["how to X?", "what is Y?", "why Z?"]
  }},
  "trending_aspects": [
    "2024 trend 1 with specific data",
    "Industry shift 2 with examples",
    "Emerging topic 3 with statistics"
  ],
  "target_audience": {{
    "primary": "Specific demographic with age/location/profession",
    "demographics": {{
      "age_range": "25-45",
      "locations": ["US", "UK", "Canada"],
      "professions": ["specific job 1", "specific job 2"],
      "income_level": "range",
      "tech_savviness": "level"
    }},
    "pain_points": [
      "Specific problem 1 with emotional impact",
      "Detailed challenge 2 with consequences",
      "Clear frustration 3 with context",
      "Pain point 4 with urgency",
      "Issue 5 with financial/time cost"
    ],
    "intent": "Specific search intent with context",
    "questions": [
      "What audience wants to know 1",
      "How audience wants to solve 2",
      "Why audience cares about 3"
    ]
  }},
  "unique_angles": [
    "Angle 1: Specific approach not covered by competitors",
    "Angle 2: Unique perspective with justification",
    "Angle 3: Original framework or methodology"
  ],
  "content_gaps": [
    "Gap 1: What competitors miss with opportunity",
    "Gap 2: Underserved subtopic with demand",
    "Gap 3: Unanswered questions with search volume"
  ],
  "content_strategy": {{
    "recommended_word_count": 1500,
    "structure": {{
      "introduction_length": "150-200 words with hook",
      "main_sections": 5,
      "h2_headings": ["Heading 1", "Heading 2", "Heading 3", "Heading 4", "Heading 5"],
      "h3_subsections": 2-3 per H2,
      "conclusion_length": "150-200 words with CTA"
    }},
    "content_depth": "Comprehensive with examples, data, and actionable steps",
    "visual_elements": ["Recommended visual 1", "Chart/graph 2", "Infographic 3"],
    "internal_linking": ["Related topic 1", "Related topic 2", "Related topic 3"]
  }},
  "seo_requirements": {{
    "title_format": "Primary keyword | Benefit/Number | Brand",
    "meta_description_template": "Hook + benefit + primary keyword + CTA",
    "target_readability": 65,
    "keyword_density": {{
      "primary": "1.5-2%",
      "secondary": "0.8-1.2%"
    }},
    "heading_keywords": "Primary keyword in H1, variants in H2s"
  }},
  "quality_benchmarks": {{
    "seo_score_target": 80,
    "overall_score_target": 85,
    "expected_outcomes": [
      "Rank in top 10 for primary keywords",
      "Minimum 3-minute average read time",
      "Publication-ready without revisions"
    ]
  }},
  "web_research_insights": {{
    "top_ranking_analysis": "What makes current top 10 successful",
    "competitor_weaknesses": "Gaps we can exploit",
    "trending_topics": "Related trending searches",
    "current_statistics": "Latest relevant data points"
  }},
  "tone_suggestion": "Specific tone with examples"
}}

**REQUIREMENTS:**
- ALL fields must be filled with SPECIFIC, ACTIONABLE data
- NO generic statements - use concrete examples and numbers
- If web search data is provided, incorporate it extensively
- Ensure research directly supports SEO score ≥ 80
- Think: "Will this research lead to publication-ready content?"
- Output ONLY valid JSON - no markdown, no commentary

**WEB SEARCH CONTEXT (if provided):**
{{web_search_context}}
""".replace("{min_words}", str(PublicationWorkflowConfig.MIN_WORD_COUNT))
   .replace("{max_words}", str(PublicationWorkflowConfig.MAX_WORD_COUNT)))

    @message_handler
    async def handle_user_request(self, message: Any, ctx: MessageContext) -> None:
        """Process research request with optional web search"""
        print(f"\n{'='*80}\n🔍 ENHANCED RESEARCH AGENT - Processing Request\n{'='*80}")
        
        user_request = message.content if hasattr(message, 'content') else str(message)
        
        # Perform web search if SERP API is available
        web_search_context = ""
        if self._serp_researcher:
            print("🌐 Performing web search for real-time data...")
            
            # Extract main topic for search
            search_results = self._serp_researcher.search(user_request)
            
            if "error" not in search_results:
                web_search_context = f"""
**REAL-TIME WEB SEARCH RESULTS:**

**Top Ranking Content:**
{json.dumps(search_results.get('organic_results', [])[:5], indent=2)}

**Related Searches:**
{json.dumps(search_results.get('related_searches', []), indent=2)}

**People Also Ask:**
{json.dumps(search_results.get('people_also_ask', []), indent=2)}

**INSTRUCTION:** Use this data to identify:
- High-performing keywords from top-ranking titles
- Content gaps from related searches
- Common questions to address
- Trending angles from current rankings
"""
                print(f"✅ Retrieved {len(search_results.get('organic_results', []))} search results")
            else:
                print(f"⚠️ Web search failed: {search_results.get('error')}")
        
        # Create enhanced prompt with web search context
        enhanced_prompt = self._system_message.content.replace(
            "{web_search_context}",
            web_search_context
        )
        
        prompt = f"{enhanced_prompt}\n\n**USER REQUEST:**\n{user_request}\n\n**YOUR RESEARCH (JSON ONLY):**"
        
        try:
            llm_result = await self._model_client.create(
                messages=[
                    SystemMessage(content=enhanced_prompt),
                    UserMessage(content=f"User Request: {user_request}\n\nProvide comprehensive research in JSON format.", source="default")
                ],
                cancellation_token=ctx.cancellation_token,
            )
            
            response = llm_result.content
            print(f"\n📊 Research Output Generated ({len(response)} chars)\n")
            
            # Store and forward
            await self.publish_message(
                response,
                topic_id=TopicId(PublicationWorkflowConfig.TOPIC_WRITER, source="default")
            )
            
        except Exception as e:
            error_msg = f"Research agent error: {str(e)}"
            print(f"❌ {error_msg}")


# ============================================================================
# ENHANCED CONTENT WRITER AGENT
# ============================================================================

@type_subscription(topic_type=PublicationWorkflowConfig.TOPIC_WRITER)
class PublicationReadyWriterAgent(RoutedAgent):
    """Content writer with strict publication-ready standards"""
    
    def __init__(self, model_client):
        super().__init__("content_writer")
        self._model_client = model_client
        
        self._system_message = SystemMessage(content="""
You are a MASTER Content Writer with 15+ years of experience creating TOP-RANKING, PUBLICATION-READY content for major publications.

**NON-NEGOTIABLE MISSION:** Create content that achieves:
- ✅ SEO Score ≥ 80/100 (MINIMUM, aim for 85+)
- ✅ Overall Quality Score ≥ 85/100
- ✅ Flesch Reading Ease ≥ 65
- ✅ Status: APPROVED and READY FOR PUBLICATION

**IF YOUR CONTENT SCORES BELOW THESE THRESHOLDS, IT IS A FAILURE.**

**MANDATORY QUALITY STANDARDS:**

1. **WORD COUNT & STRUCTURE (Critical)**
   - {min_words}-{max_words} words (STRICT - will be checked)
   - Introduction: 150-200 words with compelling hook
   - 5-7 main sections with H2 headings
   - 2-3 H3 subsections per H2
   - Conclusion: 150-200 words with strong CTA
   - Each section: 200-300 words minimum

2. **SEO OPTIMIZATION (Score ≥ 80 Required)**
   - Primary keyword: IN TITLE, first 100 words, at least 3 H2s
   - Primary keyword density: 1.5-2% EXACTLY
   - Secondary keywords: 0.8-1.2% density
   - Keyword placement: Natural, not stuffed
   - Title: 55-65 characters with primary keyword at start
   - Meta description: 150-160 characters with primary keyword and CTA
   - Alt text mentality: Descriptive, keyword-rich

3. **READABILITY (Flesch Score ≥ 65 Required)**
   - Average sentence length: 15-20 words
   - NO sentences over 30 words
   - Paragraphs: 3-5 sentences maximum
   - Use transition words: however, therefore, additionally, etc.
   - Active voice: 80%+ of sentences
   - Simple vocabulary: 8th-grade reading level
   - Short words preferred: use "help" not "facilitate"

4. **CONTENT DEPTH & QUALITY**
   - ORIGINAL insights (no generic advice)
   - SPECIFIC examples with numbers/data
   - ACTIONABLE steps readers can implement
   - EXPERT quotes or research citations
   - CASE STUDIES or real-world applications
   - VISUAL descriptions (what images/charts would show)
   - ANTICIPATED QUESTIONS answered proactively

5. **ENGAGEMENT & VALUE**
   - Hook: Problem/question/statistic that grabs attention
   - Benefits clearly stated in first paragraph
   - Each section delivers CONCRETE value
   - Lists and bullet points for scannability
   - Bolded key phrases for emphasis
   - Internal linking opportunities identified
   - CTA: Clear next step for reader

6. **HTML STRUCTURE (Clean & Semantic)**
   ```html
   <h2>Section Title with Primary or Secondary Keyword</h2>
   <p>Opening paragraph with transition and keyword variant.</p>
   <h3>Subsection Title</h3>
   <p>Content paragraph with <strong>important phrases</strong> emphasized.</p>
   <ul>
     <li>Bullet point with specific detail</li>
     <li>Another concrete point with example</li>
   </ul>
   ```
   - Use <h2> for main sections ONLY
   - Use <h3> for subsections ONLY
   - Use <strong> for key phrases (not entire sentences)
   - Use <ul>/<ol> for lists
   - Use <p> for paragraphs (no orphaned text)

7. **TITLE & META (Critical for SEO Score)**
   - Title format: "Primary Keyword: Compelling Benefit [Year]"
   - Title must be 55-65 characters
   - Meta description must include:
     * Primary keyword (first 80 characters)
     * Benefit statement
     * Urgency or CTA
     * 150-160 characters total

**OUTPUT FORMAT (STRICT JSON):**
{{
  "title": "SEO-optimized title 55-65 chars with primary keyword",
  "meta_description": "150-160 chars with primary keyword, benefit, and CTA",
  "content": "FULL HTML CONTENT WITH PROPER STRUCTURE",
  "word_count": 1500,
  "keywords_used": {{
    "primary": ["keyword1 (used X times)", "keyword2 (used Y times)"],
    "secondary": ["keyword3 (used A times)", "keyword4 (used B times)"]
  }},
  "keyword_density": {{
    "primary_keyword_1": "1.8%",
    "primary_keyword_2": "1.5%",
    "secondary_keyword_1": "1.0%"
  }},
  "readability_metrics": {{
    "avg_sentence_length": 18,
    "longest_sentence": 28,
    "paragraph_count": 25,
    "avg_paragraph_length": "4 sentences"
  }},
  "internal_link_suggestions": [
    "Anchor: 'related topic 1' → URL: /related-topic-1",
    "Anchor: 'learn more about 2' → URL: /topic-2"
  ]},
  "content_structure": {{
    "introduction": "Hook + problem + benefit (150-200 words)",
    "main_sections": [
      "H2: Section 1 Title (250 words with 2 H3s)",
      "H2: Section 2 Title (250 words with 2 H3s)",
      "H2: Section 3 Title (250 words with 2 H3s)",
      "H2: Section 4 Title (250 words with 2 H3s)",
      "H2: Section 5 Title (250 words with 2 H3s)"
    ],
    "conclusion": "Summary + CTA (150-200 words)"
  }},
  "quality_self_check": {{
    "estimated_seo_score": 85,
    "estimated_readability": 68,
    "estimated_overall_score": 87,
    "confidence": "HIGH - meets all publication standards"
  }}
}}

**SELF-CHECK BEFORE OUTPUTTING:**
- [ ] Word count {min_words}-{max_words}? ✓
- [ ] Primary keyword in title, first 100 words, 3+ H2s? ✓
- [ ] Keyword density 1.5-2% for primary? ✓
- [ ] No sentences over 30 words? ✓
- [ ] Paragraphs 3-5 sentences? ✓
- [ ] 5-7 H2 sections? ✓
- [ ] 2-3 H3s per H2? ✓
- [ ] Specific examples and data? ✓
- [ ] Actionable takeaways? ✓
- [ ] Strong hook and CTA? ✓

**IF ANY CHECK FAILS, REVISE BEFORE OUTPUTTING.**

Output ONLY valid JSON - no markdown code blocks, no commentary.
""".replace("{min_words}", str(PublicationWorkflowConfig.MIN_WORD_COUNT))
   .replace("{max_words}", str(PublicationWorkflowConfig.MAX_WORD_COUNT)))

    @message_handler
    async def handle_research(self, message: Any, ctx: MessageContext) -> None:
        """Generate publication-ready content from research"""
        print(f"\n{'='*80}\n✍️ PUBLICATION-READY WRITER - Generating Content\n{'='*80}")
        
        research_content = message.content if hasattr(message, 'content') else str(message)
        
        prompt = f"Research Data:\n{research_content}\n\nGenerate PUBLICATION-READY content in JSON format that will score SEO ≥ 80, Overall ≥ 85."
        
        try:
            llm_result = await self._model_client.create(
                messages=[self._system_message, UserMessage(content=prompt, source="default")],
                cancellation_token=ctx.cancellation_token,
            )
            
            response = llm_result.content
            print(f"\n📝 Content Generated ({len(response)} chars)\n")
            
            # Forward to SEO agent
            await self.publish_message(
                response,
                topic_id=TopicId(PublicationWorkflowConfig.TOPIC_SEO, source="default")
            )
            
        except Exception as e:
            error_msg = f"Writer agent error: {str(e)}"
            print(f"❌ {error_msg}")


# Note: SEO Agent and Scorer Agent would follow similar enhancement patterns
# with stricter validation and clearer publication-ready criteria

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  PUBLICATION-READY CONTENT WORKFLOW                          ║
    ║  ------------------------------------------------------------ ║
    ║  Enhanced with:                                               ║
    ║  • SERP API Integration for real-world research              ║
    ║  • Stricter Quality Thresholds (SEO ≥80, Overall ≥85)       ║
    ║  • Publication-Ready Prompts                                  ║
    ║  • Comprehensive Self-Checks                                  ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    To use:
    1. Set OPENAI_API_KEY environment variable
    2. Set SERP_API_KEY environment variable (optional but recommended)
    3. Replace agents in your existing workflow
    4. Enjoy publication-ready content!
    """)
=======
"""
Production-Ready Content Workflow with SERP API Integration
============================================================
Enhanced prompts that enforce publication quality standards
Integrated web search for accurate, current information
"""

import os
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from autogen_core import (
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    message_handler,
    type_subscription,
)
from autogen_core.models import SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

class PublicationWorkflowConfig:
    """Enhanced configuration for publication-ready content"""
    OPENAI_MODEL = "gpt-4o-mini"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERP_API_KEY = os.getenv("SERP_API_KEY")  # Get from serpapi.com
    
    # Stricter thresholds for publication quality
    SEO_PASS_THRESHOLD = 80  # Increased from 75
    OVERALL_PASS_THRESHOLD = 85  # Increased from 80
    MIN_WORD_COUNT = 1000
    MAX_WORD_COUNT = 2000
    TARGET_READABILITY = 65  # Flesch Reading Ease
    
    # Topic identifiers
    TOPIC_RESEARCH = "ResearchAgent"
    TOPIC_WRITER = "ContentWriterAgent"
    TOPIC_SEO = "SEOAgent"
    TOPIC_SCORER = "ScorerAgent"
    TOPIC_OUTPUT = "OutputAgent"


# ============================================================================
# SERP API INTEGRATION
# ============================================================================

class SerpAPIResearcher:
    """Integrate real-world web search for accurate research"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
    
    def search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Perform web search using SERP API"""
        if not self.api_key:
            return {"error": "SERP API key not configured"}
        
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "engine": "google"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            results = {
                "organic_results": [],
                "related_searches": [],
                "people_also_ask": []
            }
            
            # Organic search results
            for result in data.get("organic_results", [])[:10]:
                results["organic_results"].append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0)
                })
            
            # Related searches
            for related in data.get("related_searches", [])[:5]:
                results["related_searches"].append(related.get("query", ""))
            
            # People also ask
            for paa in data.get("related_questions", [])[:5]:
                results["people_also_ask"].append({
                    "question": paa.get("question", ""),
                    "snippet": paa.get("snippet", "")
                })
            
            return results
            
        except Exception as e:
            return {"error": f"SERP API error: {str(e)}"}


# ============================================================================
# ENHANCED RESEARCH AGENT
# ============================================================================

@type_subscription(topic_type=PublicationWorkflowConfig.TOPIC_RESEARCH)
class EnhancedResearchAgent(RoutedAgent):
    """Research agent with SERP API integration for real-world data"""
    
    def __init__(self, model_client, serp_api_key: Optional[str] = None):
        super().__init__("research_agent")
        self._model_client = model_client
        self._serp_researcher = SerpAPIResearcher(serp_api_key) if serp_api_key else None
        
        self._system_message = SystemMessage(content="""
You are an EXPERT Content Research Analyst with 10+ years of experience in SEO, content strategy, and audience analysis.

**CRITICAL MISSION:** Provide research that will result in PUBLICATION-READY content scoring:
- SEO Score ≥ 80/100 (NOT 75, NOT 78 - MINIMUM 80)
- Overall Quality Score ≥ 85/100
- Flesch Reading Ease ≥ 65
- Publication Status: READY FOR PUBLICATION

**YOUR RESEARCH MUST ENSURE:**

1. **HIGH-VOLUME, LOW-COMPETITION KEYWORDS**
   - Primary keywords: 1000+ monthly searches, competition < 60
   - Include EXACT search volume data if available
   - Mix of short-tail (1-2 words) and long-tail (3-5 words) keywords
   - Include question-based keywords (who, what, where, why, how)

2. **TRENDING & CURRENT INFORMATION**
   - Focus on 2024-2025 trends and data
   - Include recent statistics, studies, case studies
   - Reference current industry leaders and examples
   - Note seasonal or timely aspects

3. **COMPREHENSIVE AUDIENCE RESEARCH**
   - Specific demographics (age, location, income, profession)
   - Detailed pain points (at least 5)
   - Search intent (informational, transactional, navigational)
   - Common questions and concerns
   - Preferred content formats

4. **COMPETITIVE GAPS & UNIQUE ANGLES**
   - What's missing from top-ranking content
   - Underserved subtopics or perspectives
   - Opportunities for original insights
   - Ways to stand out from competitors

5. **CONTENT STRUCTURE GUIDANCE**
   - Recommended word count: {min_words}-{max_words} words
   - Optimal heading structure (number of H2s, H3s)
   - Content depth requirements
   - Internal linking opportunities

**OUTPUT FORMAT (STRICT JSON):**
{{
  "topic": "Specific, SEO-optimized topic title",
  "niche": "Precise niche category",
  "keywords": {{
    "primary": ["keyword1 (5000/mo)", "keyword2 (3000/mo)"],
    "secondary": ["keyword3 (1000/mo)", "keyword4 (800/mo)"],
    "long_tail": ["specific phrase 1", "specific phrase 2"],
    "questions": ["how to X?", "what is Y?", "why Z?"]
  }},
  "trending_aspects": [
    "2024 trend 1 with specific data",
    "Industry shift 2 with examples",
    "Emerging topic 3 with statistics"
  ],
  "target_audience": {{
    "primary": "Specific demographic with age/location/profession",
    "demographics": {{
      "age_range": "25-45",
      "locations": ["US", "UK", "Canada"],
      "professions": ["specific job 1", "specific job 2"],
      "income_level": "range",
      "tech_savviness": "level"
    }},
    "pain_points": [
      "Specific problem 1 with emotional impact",
      "Detailed challenge 2 with consequences",
      "Clear frustration 3 with context",
      "Pain point 4 with urgency",
      "Issue 5 with financial/time cost"
    ],
    "intent": "Specific search intent with context",
    "questions": [
      "What audience wants to know 1",
      "How audience wants to solve 2",
      "Why audience cares about 3"
    ]
  }},
  "unique_angles": [
    "Angle 1: Specific approach not covered by competitors",
    "Angle 2: Unique perspective with justification",
    "Angle 3: Original framework or methodology"
  ],
  "content_gaps": [
    "Gap 1: What competitors miss with opportunity",
    "Gap 2: Underserved subtopic with demand",
    "Gap 3: Unanswered questions with search volume"
  ],
  "content_strategy": {{
    "recommended_word_count": 1500,
    "structure": {{
      "introduction_length": "150-200 words with hook",
      "main_sections": 5,
      "h2_headings": ["Heading 1", "Heading 2", "Heading 3", "Heading 4", "Heading 5"],
      "h3_subsections": 2-3 per H2,
      "conclusion_length": "150-200 words with CTA"
    }},
    "content_depth": "Comprehensive with examples, data, and actionable steps",
    "visual_elements": ["Recommended visual 1", "Chart/graph 2", "Infographic 3"],
    "internal_linking": ["Related topic 1", "Related topic 2", "Related topic 3"]
  }},
  "seo_requirements": {{
    "title_format": "Primary keyword | Benefit/Number | Brand",
    "meta_description_template": "Hook + benefit + primary keyword + CTA",
    "target_readability": 65,
    "keyword_density": {{
      "primary": "1.5-2%",
      "secondary": "0.8-1.2%"
    }},
    "heading_keywords": "Primary keyword in H1, variants in H2s"
  }},
  "quality_benchmarks": {{
    "seo_score_target": 80,
    "overall_score_target": 85,
    "expected_outcomes": [
      "Rank in top 10 for primary keywords",
      "Minimum 3-minute average read time",
      "Publication-ready without revisions"
    ]
  }},
  "web_research_insights": {{
    "top_ranking_analysis": "What makes current top 10 successful",
    "competitor_weaknesses": "Gaps we can exploit",
    "trending_topics": "Related trending searches",
    "current_statistics": "Latest relevant data points"
  }},
  "tone_suggestion": "Specific tone with examples"
}}

**REQUIREMENTS:**
- ALL fields must be filled with SPECIFIC, ACTIONABLE data
- NO generic statements - use concrete examples and numbers
- If web search data is provided, incorporate it extensively
- Ensure research directly supports SEO score ≥ 80
- Think: "Will this research lead to publication-ready content?"
- Output ONLY valid JSON - no markdown, no commentary

**WEB SEARCH CONTEXT (if provided):**
{{web_search_context}}
""".replace("{min_words}", str(PublicationWorkflowConfig.MIN_WORD_COUNT))
   .replace("{max_words}", str(PublicationWorkflowConfig.MAX_WORD_COUNT)))

    @message_handler
    async def handle_user_request(self, message: Any, ctx: MessageContext) -> None:
        """Process research request with optional web search"""
        print(f"\n{'='*80}\n🔍 ENHANCED RESEARCH AGENT - Processing Request\n{'='*80}")
        
        user_request = message.content if hasattr(message, 'content') else str(message)
        
        # Perform web search if SERP API is available
        web_search_context = ""
        if self._serp_researcher:
            print("🌐 Performing web search for real-time data...")
            
            # Extract main topic for search
            search_results = self._serp_researcher.search(user_request)
            
            if "error" not in search_results:
                web_search_context = f"""
**REAL-TIME WEB SEARCH RESULTS:**

**Top Ranking Content:**
{json.dumps(search_results.get('organic_results', [])[:5], indent=2)}

**Related Searches:**
{json.dumps(search_results.get('related_searches', []), indent=2)}

**People Also Ask:**
{json.dumps(search_results.get('people_also_ask', []), indent=2)}

**INSTRUCTION:** Use this data to identify:
- High-performing keywords from top-ranking titles
- Content gaps from related searches
- Common questions to address
- Trending angles from current rankings
"""
                print(f"✅ Retrieved {len(search_results.get('organic_results', []))} search results")
            else:
                print(f"⚠️ Web search failed: {search_results.get('error')}")
        
        # Create enhanced prompt with web search context
        enhanced_prompt = self._system_message.content.replace(
            "{web_search_context}",
            web_search_context
        )
        
        prompt = f"{enhanced_prompt}\n\n**USER REQUEST:**\n{user_request}\n\n**YOUR RESEARCH (JSON ONLY):**"
        
        try:
            llm_result = await self._model_client.create(
                messages=[
                    SystemMessage(content=enhanced_prompt),
                    UserMessage(content=f"User Request: {user_request}\n\nProvide comprehensive research in JSON format.", source="default")
                ],
                cancellation_token=ctx.cancellation_token,
            )
            
            response = llm_result.content
            print(f"\n📊 Research Output Generated ({len(response)} chars)\n")
            
            # Store and forward
            await self.publish_message(
                response,
                topic_id=TopicId(PublicationWorkflowConfig.TOPIC_WRITER, source="default")
            )
            
        except Exception as e:
            error_msg = f"Research agent error: {str(e)}"
            print(f"❌ {error_msg}")


# ============================================================================
# ENHANCED CONTENT WRITER AGENT
# ============================================================================

@type_subscription(topic_type=PublicationWorkflowConfig.TOPIC_WRITER)
class PublicationReadyWriterAgent(RoutedAgent):
    """Content writer with strict publication-ready standards"""
    
    def __init__(self, model_client):
        super().__init__("content_writer")
        self._model_client = model_client
        
        self._system_message = SystemMessage(content="""
You are a MASTER Content Writer with 15+ years of experience creating TOP-RANKING, PUBLICATION-READY content for major publications.

**NON-NEGOTIABLE MISSION:** Create content that achieves:
- ✅ SEO Score ≥ 80/100 (MINIMUM, aim for 85+)
- ✅ Overall Quality Score ≥ 85/100
- ✅ Flesch Reading Ease ≥ 65
- ✅ Status: APPROVED and READY FOR PUBLICATION

**IF YOUR CONTENT SCORES BELOW THESE THRESHOLDS, IT IS A FAILURE.**

**MANDATORY QUALITY STANDARDS:**

1. **WORD COUNT & STRUCTURE (Critical)**
   - {min_words}-{max_words} words (STRICT - will be checked)
   - Introduction: 150-200 words with compelling hook
   - 5-7 main sections with H2 headings
   - 2-3 H3 subsections per H2
   - Conclusion: 150-200 words with strong CTA
   - Each section: 200-300 words minimum

2. **SEO OPTIMIZATION (Score ≥ 80 Required)**
   - Primary keyword: IN TITLE, first 100 words, at least 3 H2s
   - Primary keyword density: 1.5-2% EXACTLY
   - Secondary keywords: 0.8-1.2% density
   - Keyword placement: Natural, not stuffed
   - Title: 55-65 characters with primary keyword at start
   - Meta description: 150-160 characters with primary keyword and CTA
   - Alt text mentality: Descriptive, keyword-rich

3. **READABILITY (Flesch Score ≥ 65 Required)**
   - Average sentence length: 15-20 words
   - NO sentences over 30 words
   - Paragraphs: 3-5 sentences maximum
   - Use transition words: however, therefore, additionally, etc.
   - Active voice: 80%+ of sentences
   - Simple vocabulary: 8th-grade reading level
   - Short words preferred: use "help" not "facilitate"

4. **CONTENT DEPTH & QUALITY**
   - ORIGINAL insights (no generic advice)
   - SPECIFIC examples with numbers/data
   - ACTIONABLE steps readers can implement
   - EXPERT quotes or research citations
   - CASE STUDIES or real-world applications
   - VISUAL descriptions (what images/charts would show)
   - ANTICIPATED QUESTIONS answered proactively

5. **ENGAGEMENT & VALUE**
   - Hook: Problem/question/statistic that grabs attention
   - Benefits clearly stated in first paragraph
   - Each section delivers CONCRETE value
   - Lists and bullet points for scannability
   - Bolded key phrases for emphasis
   - Internal linking opportunities identified
   - CTA: Clear next step for reader

6. **HTML STRUCTURE (Clean & Semantic)**
   ```html
   <h2>Section Title with Primary or Secondary Keyword</h2>
   <p>Opening paragraph with transition and keyword variant.</p>
   <h3>Subsection Title</h3>
   <p>Content paragraph with <strong>important phrases</strong> emphasized.</p>
   <ul>
     <li>Bullet point with specific detail</li>
     <li>Another concrete point with example</li>
   </ul>
   ```
   - Use <h2> for main sections ONLY
   - Use <h3> for subsections ONLY
   - Use <strong> for key phrases (not entire sentences)
   - Use <ul>/<ol> for lists
   - Use <p> for paragraphs (no orphaned text)

7. **TITLE & META (Critical for SEO Score)**
   - Title format: "Primary Keyword: Compelling Benefit [Year]"
   - Title must be 55-65 characters
   - Meta description must include:
     * Primary keyword (first 80 characters)
     * Benefit statement
     * Urgency or CTA
     * 150-160 characters total

**OUTPUT FORMAT (STRICT JSON):**
{{
  "title": "SEO-optimized title 55-65 chars with primary keyword",
  "meta_description": "150-160 chars with primary keyword, benefit, and CTA",
  "content": "FULL HTML CONTENT WITH PROPER STRUCTURE",
  "word_count": 1500,
  "keywords_used": {{
    "primary": ["keyword1 (used X times)", "keyword2 (used Y times)"],
    "secondary": ["keyword3 (used A times)", "keyword4 (used B times)"]
  }},
  "keyword_density": {{
    "primary_keyword_1": "1.8%",
    "primary_keyword_2": "1.5%",
    "secondary_keyword_1": "1.0%"
  }},
  "readability_metrics": {{
    "avg_sentence_length": 18,
    "longest_sentence": 28,
    "paragraph_count": 25,
    "avg_paragraph_length": "4 sentences"
  }},
  "internal_link_suggestions": [
    "Anchor: 'related topic 1' → URL: /related-topic-1",
    "Anchor: 'learn more about 2' → URL: /topic-2"
  ]},
  "content_structure": {{
    "introduction": "Hook + problem + benefit (150-200 words)",
    "main_sections": [
      "H2: Section 1 Title (250 words with 2 H3s)",
      "H2: Section 2 Title (250 words with 2 H3s)",
      "H2: Section 3 Title (250 words with 2 H3s)",
      "H2: Section 4 Title (250 words with 2 H3s)",
      "H2: Section 5 Title (250 words with 2 H3s)"
    ],
    "conclusion": "Summary + CTA (150-200 words)"
  }},
  "quality_self_check": {{
    "estimated_seo_score": 85,
    "estimated_readability": 68,
    "estimated_overall_score": 87,
    "confidence": "HIGH - meets all publication standards"
  }}
}}

**SELF-CHECK BEFORE OUTPUTTING:**
- [ ] Word count {min_words}-{max_words}? ✓
- [ ] Primary keyword in title, first 100 words, 3+ H2s? ✓
- [ ] Keyword density 1.5-2% for primary? ✓
- [ ] No sentences over 30 words? ✓
- [ ] Paragraphs 3-5 sentences? ✓
- [ ] 5-7 H2 sections? ✓
- [ ] 2-3 H3s per H2? ✓
- [ ] Specific examples and data? ✓
- [ ] Actionable takeaways? ✓
- [ ] Strong hook and CTA? ✓

**IF ANY CHECK FAILS, REVISE BEFORE OUTPUTTING.**

Output ONLY valid JSON - no markdown code blocks, no commentary.
""".replace("{min_words}", str(PublicationWorkflowConfig.MIN_WORD_COUNT))
   .replace("{max_words}", str(PublicationWorkflowConfig.MAX_WORD_COUNT)))

    @message_handler
    async def handle_research(self, message: Any, ctx: MessageContext) -> None:
        """Generate publication-ready content from research"""
        print(f"\n{'='*80}\n✍️ PUBLICATION-READY WRITER - Generating Content\n{'='*80}")
        
        research_content = message.content if hasattr(message, 'content') else str(message)
        
        prompt = f"Research Data:\n{research_content}\n\nGenerate PUBLICATION-READY content in JSON format that will score SEO ≥ 80, Overall ≥ 85."
        
        try:
            llm_result = await self._model_client.create(
                messages=[self._system_message, UserMessage(content=prompt, source="default")],
                cancellation_token=ctx.cancellation_token,
            )
            
            response = llm_result.content
            print(f"\n📝 Content Generated ({len(response)} chars)\n")
            
            # Forward to SEO agent
            await self.publish_message(
                response,
                topic_id=TopicId(PublicationWorkflowConfig.TOPIC_SEO, source="default")
            )
            
        except Exception as e:
            error_msg = f"Writer agent error: {str(e)}"
            print(f"❌ {error_msg}")


# Note: SEO Agent and Scorer Agent would follow similar enhancement patterns
# with stricter validation and clearer publication-ready criteria

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  PUBLICATION-READY CONTENT WORKFLOW                          ║
    ║  ------------------------------------------------------------ ║
    ║  Enhanced with:                                               ║
    ║  • SERP API Integration for real-world research              ║
    ║  • Stricter Quality Thresholds (SEO ≥80, Overall ≥85)       ║
    ║  • Publication-Ready Prompts                                  ║
    ║  • Comprehensive Self-Checks                                  ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    To use:
    1. Set OPENAI_API_KEY environment variable
    2. Set SERP_API_KEY environment variable (optional but recommended)
    3. Replace agents in your existing workflow
    4. Enjoy publication-ready content!
    """)
>>>>>>> c48496b (Automated update)
