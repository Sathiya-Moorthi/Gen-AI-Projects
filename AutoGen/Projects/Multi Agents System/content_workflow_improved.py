<<<<<<< HEAD
"""
RTCFR Multi-Agent Content Generation System - PUBLICATION READY VERSION
========================================================================
Sequential workflow with Research → Writer → SEO → Scorer agents
Enhanced with SERP API integration and stricter publication standards

Key Improvements:
- SERP API integration for real-world research
- SEO threshold increased to 80 (from 75)
- Overall threshold increased to 85 (from 80)
- Publication-ready prompts with self-validation
- Stricter word count and readability requirements
"""

import os
import json
import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from autogen_core import (
    MessageContext,
    MessageHandlerContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    message_handler,
    type_subscription,
)
from autogen_core.models import SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient


# ============================================================================
# Configuration
# ============================================================================

class WorkflowConfig:
    """Central configuration for the workflow"""
    OPENAI_MODEL = "gpt-4o-mini"
    
    @staticmethod
    def get_openai_api_key():
        return os.getenv("OPENAI_API_KEY")
    
    @staticmethod
    def get_serp_api_key():
        return os.getenv("SERP_API_KEY")  # Optional but recommended
    
    # Topic identifiers
    TOPIC_RESEARCH = "research_agent"
    TOPIC_WRITER = "content_writer"
    TOPIC_SEO = "seo_agent"
    TOPIC_SCORER = "scorer_agent"
    TOPIC_OUTPUT = "output_agent"
    
    # Thresholds - INCREASED FOR PUBLICATION QUALITY
    SEO_PASS_THRESHOLD = 80  # Increased from 75
    OVERALL_PASS_THRESHOLD = 85  # Increased from 80
    MIN_WORD_COUNT = 1000  # Minimum words for SEO
    MAX_WORD_COUNT = 2000  # Maximum words for readability
    TARGET_READABILITY = 65  # Flesch Reading Ease target
    
    # Timeouts (seconds)
    LLM_TIMEOUT = 120
    WORKFLOW_TIMEOUT = 600


# ============================================================================
# Message Protocol
# ============================================================================

@dataclass
class ContentMessage:
    """Standardized message format for inter-agent communication"""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    stage: str = ""


@dataclass
class WorkflowResult:
    """Complete workflow result for API responses"""
    success: bool
    research: Optional[Dict[str, Any]] = None
    content: Optional[Dict[str, Any]] = None
    seo_analysis: Optional[Dict[str, Any]] = None
    final_score: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0


# ============================================================================
# Result Collector (Global State Management)
# ============================================================================

class ResultCollector:
    """Thread-safe result collection for workflow outputs"""
    
    def __init__(self):
        self._results: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
    
    async def store(self, key: str, value: Any):
        async with self._lock:
            self._results[key] = value
    
    async def get(self, key: str, default=None):
        async with self._lock:
            return self._results.get(key, default)
    
    async def get_all(self) -> Dict[str, Any]:
        async with self._lock:
            return self._results.copy()
    
    async def clear(self):
        async with self._lock:
            self._results.clear()

# Global result collector instance
result_collector = ResultCollector()


# ============================================================================
# SERP API Integration
# ============================================================================

class SerpAPIResearcher:
    """Integrate real-world web search for accurate research"""
    
    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
    
    def search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Perform web search using SERP API"""
        if not self.api_key:
            return {"error": "SERP API key not configured"}
        
        try:
            import requests
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
# Agent 1: Enhanced Research Agent with SERP API
# ============================================================================

@type_subscription(topic_type=WorkflowConfig.TOPIC_RESEARCH)
class ResearchAgent(RoutedAgent):
    """Expert Content Research Analyst with web search integration"""
    
    def __init__(self, model_client, serp_api_key: Optional[str] = None):
        super().__init__("research_agent")
        self._model_client = model_client
        self._serp_researcher = SerpAPIResearcher(serp_api_key) if serp_api_key else None
        
        self._system_message = SystemMessage(content="""
**ROLE:**
You are an EXPERT Content Research Analyst with 10+ years of experience in SEO, content strategy, and audience analysis.

**CRITICAL MISSION:** Provide research that will result in PUBLICATION-READY content scoring:
- SEO Score ≥ 80/100 (NOT 75, NOT 78 - MINIMUM 80)
- Overall Quality Score ≥ 85/100
- Flesch Reading Ease ≥ 65
- Publication Status: READY FOR PUBLICATION

**YOUR RESEARCH MUST ENSURE:**

1. **HIGH-VOLUME, LOW-COMPETITION KEYWORDS**
   - Primary keywords: 1000+ monthly searches
   - Include search volume data if available
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
   - Recommended word count: 1000-2000 words
   - Optimal heading structure (number of H2s, H3s)
   - Content depth requirements
   - Internal linking opportunities

**OUTPUT FORMAT (STRICT JSON):**
{
  "topic": "Specific, SEO-optimized topic title",
  "niche": "Precise niche category",
  "keywords": {
    "primary": ["keyword1", "keyword2"],
    "secondary": ["keyword3", "keyword4"],
    "long_tail": ["specific phrase 1", "specific phrase 2"],
    "questions": ["how to X?", "what is Y?", "why Z?"]
  },
  "trending_aspects": [
    "2024 trend 1 with specific data",
    "Industry shift 2 with examples",
    "Emerging topic 3 with statistics"
  ],
  "target_audience": {
    "primary": "Specific demographic with age/location/profession",
    "demographics": {
      "age_range": "25-45",
      "locations": ["US", "UK", "Canada"],
      "professions": ["specific job 1", "specific job 2"],
      "income_level": "range",
      "tech_savviness": "level"
    },
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
  },
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
  "content_strategy": {
    "recommended_word_count": 1500,
    "structure": {
      "introduction_length": "150-200 words with hook",
      "main_sections": 5,
      "h2_headings": ["Heading 1", "Heading 2", "Heading 3", "Heading 4", "Heading 5"],
      "h3_subsections": "2-3 per H2",
      "conclusion_length": "150-200 words with CTA"
    },
    "content_depth": "Comprehensive with examples, data, and actionable steps",
    "visual_elements": ["Recommended visual 1", "Chart/graph 2", "Infographic 3"],
    "internal_linking": ["Related topic 1", "Related topic 2", "Related topic 3"]
  },
  "seo_requirements": {
    "title_format": "Primary keyword | Benefit/Number | Brand",
    "meta_description_template": "Hook + benefit + primary keyword + CTA",
    "target_readability": 65,
    "keyword_density": {
      "primary": "1.5-2%",
      "secondary": "0.8-1.2%"
    },
    "heading_keywords": "Primary keyword in H1, variants in H2s"
  },
  "quality_benchmarks": {
    "seo_score_target": 80,
    "overall_score_target": 85,
    "expected_outcomes": [
      "Rank in top 10 for primary keywords",
      "Minimum 3-minute average read time",
      "Publication-ready without revisions"
    ]
  },
  "tone_suggestion": "Specific tone with examples"
}

**REQUIREMENTS:**
- ALL fields must be filled with SPECIFIC, ACTIONABLE data
- NO generic statements - use concrete examples and numbers
- If web search data is provided, incorporate it extensively
- Ensure research directly supports SEO score ≥ 80
- Think: "Will this research lead to publication-ready content?"
- Output ONLY valid JSON - no markdown, no commentary

**WEB SEARCH CONTEXT (if provided):**
{web_search_context}
""")

    @message_handler
    async def handle_user_request(self, message: ContentMessage, ctx: MessageContext) -> None:
        """Process research request with optional web search"""
        print(f"\n{'='*80}\n🔍 ENHANCED RESEARCH AGENT - Processing Request\n{'='*80}")
        
        user_request = message.content
        
        # Perform web search if SERP API is available
        web_search_context = ""
        if self._serp_researcher:
            print("🌐 Performing web search for real-time data...")
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
                print(f"⚠️ Web search unavailable: {search_results.get('error')}")
        
        try:
            # Update system message with web search context
            enhanced_prompt = self._system_message.content.replace("{web_search_context}", web_search_context)
            updated_system = SystemMessage(content=enhanced_prompt)
            
            prompt = f"User Request: {user_request}\n\nProvide comprehensive research in JSON format that will lead to SEO score ≥ 80 and Overall score ≥ 85."
            
            agent_id = MessageHandlerContext.agent_id()
            llm_result = await asyncio.wait_for(
                self._model_client.create(
                    messages=[updated_system, UserMessage(content=prompt, source="default")],
                    cancellation_token=ctx.cancellation_token,
                ),
                timeout=WorkflowConfig.LLM_TIMEOUT
            )
            
            response = llm_result.content
            print(f"📊 Research Output Generated ({len(response)} chars)\n")
            
            # Store research result
            await result_collector.store("research", self._parse_json_safe(response))
            
            # Forward to writer agent
            await self.publish_message(
                ContentMessage(
                    content=response,
                    metadata={"stage": "research", "original_request": user_request},
                    stage="research"
                ),
                topic_id=TopicId(WorkflowConfig.TOPIC_WRITER, source="default")
            )
            
        except asyncio.TimeoutError:
            error_msg = "Research agent timeout"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
        except Exception as e:
            error_msg = f"Research agent error: {str(e)}"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
    
    @staticmethod
    def _parse_json_safe(text: str) -> Dict[str, Any]:
        """Safely parse JSON, handling markdown code blocks"""
        try:
            # Remove markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            return {"error": f"Failed to parse JSON: {str(e)}", "raw_text": text[:500]}


# ============================================================================
# Agent 2: Publication-Ready Content Writer Agent
# ============================================================================

@type_subscription(topic_type=WorkflowConfig.TOPIC_WRITER)
class ContentWriterAgent(RoutedAgent):
    """Master content writer focused on publication-ready quality"""
    
    def __init__(self, model_client):
        super().__init__("content_writer")
        self._model_client = model_client
        
        self._system_message = SystemMessage(content="""
**ROLE:**
You are a MASTER Content Writer with 15+ years of experience creating TOP-RANKING, PUBLICATION-READY content for major publications.

**NON-NEGOTIABLE MISSION:** Create content that achieves:
- ✅ SEO Score ≥ 80/100 (MINIMUM, aim for 85+)
- ✅ Overall Quality Score ≥ 85/100
- ✅ Flesch Reading Ease ≥ 65
- ✅ Status: APPROVED and READY FOR PUBLICATION

**IF YOUR CONTENT SCORES BELOW THESE THRESHOLDS, IT IS A FAILURE.**

**MANDATORY QUALITY STANDARDS:**

1. **WORD COUNT & STRUCTURE (Critical)**
   - 1000-2000 words (STRICT - will be checked)
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
   - Use <h2> for main sections ONLY
   - Use <h3> for subsections ONLY
   - Use <strong> for key phrases (not entire sentences)
   - Use <ul>/<ol> for lists
   - Use <p> for paragraphs (no orphaned text)
   - Example structure:
     <h2>Section Title with Primary or Secondary Keyword</h2>
     <p>Opening paragraph with transition and keyword variant.</p>
     <h3>Subsection Title</h3>
     <p>Content paragraph with <strong>important phrases</strong> emphasized.</p>
     <ul>
       <li>Bullet point with specific detail</li>
       <li>Another concrete point with example</li>
     </ul>

7. **TITLE & META (Critical for SEO Score)**
   - Title format: "Primary Keyword: Compelling Benefit [Year]"
   - Title must be 55-65 characters
   - Meta description must include:
     * Primary keyword (first 80 characters)
     * Benefit statement
     * Urgency or CTA
     * 150-160 characters total

**OUTPUT FORMAT (STRICT JSON):**
{
  "title": "SEO-optimized title 55-65 chars with primary keyword",
  "meta_description": "150-160 chars with primary keyword, benefit, and CTA",
  "content": "FULL HTML CONTENT WITH PROPER STRUCTURE",
  "word_count": 1500,
  "keywords_used": {
    "primary": ["keyword1 (used X times)", "keyword2 (used Y times)"],
    "secondary": ["keyword3 (used A times)", "keyword4 (used B times)"]
  },
  "keyword_density": {
    "primary_keyword_1": "1.8%",
    "primary_keyword_2": "1.5%",
    "secondary_keyword_1": "1.0%"
  },
  "readability_metrics": {
    "avg_sentence_length": 18,
    "longest_sentence": 28,
    "paragraph_count": 25,
    "avg_paragraph_length": "4 sentences"
  },
  "internal_link_suggestions": [
    "Anchor: 'related topic 1' → URL: /related-topic-1",
    "Anchor: 'learn more about 2' → URL: /topic-2"
  ],
  "content_structure": {
    "introduction": "Hook + problem + benefit (150-200 words)",
    "main_sections": [
      "H2: Section 1 Title (250 words with 2 H3s)",
      "H2: Section 2 Title (250 words with 2 H3s)",
      "H2: Section 3 Title (250 words with 2 H3s)",
      "H2: Section 4 Title (250 words with 2 H3s)",
      "H2: Section 5 Title (250 words with 2 H3s)"
    ],
    "conclusion": "Summary + CTA (150-200 words)"
  },
  "quality_self_check": {
    "estimated_seo_score": 85,
    "estimated_readability": 68,
    "estimated_overall_score": 87,
    "confidence": "HIGH - meets all publication standards"
  }
}

**SELF-CHECK BEFORE OUTPUTTING:**
- [ ] Word count 1000-2000? ✓
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
""")

    @message_handler
    async def handle_research(self, message: ContentMessage, ctx: MessageContext) -> None:
        """Generate publication-ready content from research"""
        print(f"\n{'='*80}\n✍️ PUBLICATION-READY WRITER - Generating Content\n{'='*80}")
        
        research_content = message.content
        
        prompt = f"""Research Data:
{research_content}

Generate PUBLICATION-READY content in JSON format.

CRITICAL: Content MUST achieve:
- SEO Score ≥ 80 (not 75, not 78)
- Overall Score ≥ 85 (not 80)
- Word count: 1000-2000 words (STRICT)
- Keyword density: 1.5-2% for primary keywords
- Readability: Flesch ≥ 65

Output ONLY JSON."""
        
        try:
            agent_id = MessageHandlerContext.agent_id()
            llm_result = await asyncio.wait_for(
                self._model_client.create(
                    messages=[self._system_message, UserMessage(content=prompt, source="default")],
                    cancellation_token=ctx.cancellation_token,
                ),
                timeout=WorkflowConfig.LLM_TIMEOUT
            )
            
            response = llm_result.content
            print(f"📝 Content Generated ({len(response)} chars)\n")
            
            # Store content result
            await result_collector.store("content", self._parse_json_safe(response))
            
            # Forward to SEO agent
            await self.publish_message(
                ContentMessage(
                    content=response,
                    metadata={"stage": "content_writing"},
                    stage="content_writing"
                ),
                topic_id=TopicId(WorkflowConfig.TOPIC_SEO, source="default")
            )
            
        except asyncio.TimeoutError:
            error_msg = "Content writer timeout"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
        except Exception as e:
            error_msg = f"Content writer error: {str(e)}"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
    
    @staticmethod
    def _parse_json_safe(text: str) -> Dict[str, Any]:
        """Safely parse JSON, handling markdown code blocks"""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            return {"error": f"Failed to parse JSON: {str(e)}", "raw_text": text[:500]}


# ============================================================================
# Agent 3: SEO Validation Agent (Enhanced Thresholds)
# ============================================================================

@type_subscription(topic_type=WorkflowConfig.TOPIC_SEO)
class SEOAgent(RoutedAgent):
    """SEO Expert with stricter validation standards"""
    
    def __init__(self, model_client):
        super().__init__("seo_agent")
        self._model_client = model_client
        
        self._system_message = SystemMessage(content=f"""
**ROLE:**
You are an SEO Technical Expert and Content Quality Auditor with 10+ years of experience optimizing content for top search engine rankings. You specialize in keyword optimization, readability analysis, and technical SEO validation.

**TASK:**
Validate the generated content against strict SEO best practices and publication standards. Perform comprehensive technical analysis and provide actionable recommendations.

**CONTEXT:**
You are analyzing content that MUST meet these publication thresholds:
- SEO Score: ≥ 80/100 (STRICT - not 75)
- Keyword Density: Primary 1.5-2%, Secondary 0.8-1.2%
- Readability: Flesch Reading Ease ≥ 65
- Word Count: 1000-2000 words

**VALIDATION CRITERIA:**

1. **Keyword Optimization (30 points)**
   - Primary keyword in title (5 pts)
   - Primary keyword in first 100 words (5 pts)
   - Primary keyword in at least 3 H2 headings (5 pts)
   - Primary keyword density 1.5-2% (10 pts)
   - Secondary keyword integration (5 pts)

2. **Content Structure (25 points)**
   - Single H1 tag present (5 pts)
   - 5-7 H2 sections (10 pts)
   - 2-3 H3 per H2 (5 pts)
   - Proper HTML hierarchy (5 pts)

3. **Readability (25 points)**
   - Flesch Reading Ease ≥ 65 (10 pts)
   - Average sentence length 15-20 words (8 pts)
   - No sentences > 30 words (7 pts)

4. **Meta Elements (10 points)**
   - Title 55-65 characters (5 pts)
   - Meta description 150-160 characters (5 pts)

5. **Technical SEO (10 points)**
   - Internal link suggestions (5 pts)
   - Paragraph length 3-5 sentences (5 pts)

**SUCCESS CRITERIA:**
- Overall SEO score ≥ {WorkflowConfig.SEO_PASS_THRESHOLD}/100 to PASS validation
- If score < {WorkflowConfig.SEO_PASS_THRESHOLD}, status = FAIL, requires_revision = true

**OUTPUT FORMAT (JSON):**
{{
  "seo_score": 85,
  "validation_status": "PASS",
  "pass_threshold": {WorkflowConfig.SEO_PASS_THRESHOLD},
  "requires_revision": false,
  "analysis": {{
    "keyword_optimization": {{
      "score": 28,
      "primary_keyword_in_title": true,
      "primary_keyword_in_first_100": true,
      "primary_keyword_in_headings": 5,
      "primary_keyword_density": "1.8%",
      "secondary_keyword_density": "1.0%",
      "issues": []
    }},
    "content_structure": {{
      "score": 24,
      "h1_count": 1,
      "h2_count": 6,
      "h3_count": 15,
      "heading_hierarchy_valid": true,
      "issues": []
    }},
    "readability": {{
      "score": 24,
      "flesch_reading_ease": 68,
      "avg_sentence_length": 18,
      "longest_sentence": 28,
      "sentences_over_30_words": 0,
      "issues": []
    }},
    "meta_elements": {{
      "score": 10,
      "title_length": 62,
      "meta_description_length": 158,
      "title_has_keyword": true,
      "meta_has_keyword": true,
      "issues": []
    }},
    "technical_seo": {{
      "score": 9,
      "internal_links_present": true,
      "paragraph_structure_valid": true,
      "issues": ["Consider adding 1-2 more internal links"]
    }}
  }},
  "recommendations": [
    "Excellent keyword optimization - maintain 1.8% density",
    "Add one more internal link for better site structure",
    "Content meets all publication standards"
  ]
}}

**REQUIREMENTS:**
1. Perform ACTUAL analysis - don't just approve without checking
2. Calculate REAL keyword density and readability scores
3. If SEO score < {WorkflowConfig.SEO_PASS_THRESHOLD}, status MUST be "FAIL"
4. Provide SPECIFIC recommendations for any issues found
5. Be STRICT - publication quality requires high standards
6. Output ONLY valid JSON

Analyze the content thoroughly and provide detailed validation.
""")

    @message_handler
    async def handle_content(self, message: ContentMessage, ctx: MessageContext) -> None:
        """Validate content for SEO compliance with strict standards"""
        print(f"\n{'='*80}\n📊 SEO AGENT - Validating Content (Threshold: {WorkflowConfig.SEO_PASS_THRESHOLD})\n{'='*80}")
        
        content_data = message.content
        
        prompt = f"""Content to validate:
{content_data}

Perform STRICT SEO validation.
Threshold for PASS: ≥ {WorkflowConfig.SEO_PASS_THRESHOLD}/100
Output ONLY JSON."""
        
        try:
            agent_id = MessageHandlerContext.agent_id()
            llm_result = await asyncio.wait_for(
                self._model_client.create(
                    messages=[self._system_message, UserMessage(content=prompt, source="default")],
                    cancellation_token=ctx.cancellation_token,
                ),
                timeout=WorkflowConfig.LLM_TIMEOUT
            )
            
            response = llm_result.content
            print(f"🔍 SEO Analysis Complete\n")
            
            # Store SEO result
            await result_collector.store("seo_analysis", self._parse_json_safe(response))
            
            # Forward to scorer
            await self.publish_message(
                ContentMessage(
                    content=response,
                    metadata={"stage": "seo_validation"},
                    stage="seo_validation"
                ),
                topic_id=TopicId(WorkflowConfig.TOPIC_SCORER, source="default")
            )
            
        except asyncio.TimeoutError:
            error_msg = "SEO agent timeout"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
        except Exception as e:
            error_msg = f"SEO agent error: {str(e)}"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
    
    @staticmethod
    def _parse_json_safe(text: str) -> Dict[str, Any]:
        """Safely parse JSON"""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            return {"error": f"Failed to parse JSON: {str(e)}", "raw_text": text[:500]}


# ============================================================================
# Agent 4: Quality Scorer Agent (Enhanced Thresholds)
# ============================================================================

@type_subscription(topic_type=WorkflowConfig.TOPIC_SCORER)
class ScorerAgent(RoutedAgent):
    """Quality scorer with strict publication standards"""
    
    def __init__(self, model_client):
        super().__init__("scorer_agent")
        self._model_client = model_client
        
        self._system_message = SystemMessage(content=f"""
**ROLE:**
You are a Senior Content Quality Auditor and Editorial Director with 15+ years evaluating content for top-tier publications. You make final APPROVE/REJECT decisions based on comprehensive quality analysis.

**TASK:**
Evaluate the complete content generation output and provide a final quality score and publication decision.

**PUBLICATION STANDARDS (STRICT):**
1. SEO Performance: Must be ≥ {WorkflowConfig.SEO_PASS_THRESHOLD}/100
2. Overall Quality: Must be ≥ {WorkflowConfig.OVERALL_PASS_THRESHOLD}/100
3. Content must be publication-ready without revisions

**SCORING COMPONENTS:**

1. **SEO Performance (30% weight)**
   - Based on SEO agent's validation
   - Must score ≥ {WorkflowConfig.SEO_PASS_THRESHOLD} to pass

2. **Content Quality (30% weight)**
   - Originality and depth (0-100)
   - Specific examples and data
   - Actionable insights
   - Research backing

3. **Engagement Potential (20% weight)**
   - Hook effectiveness (0-100)
   - Scannability (headings, lists, formatting)
   - Value delivery per section
   - CTA clarity

4. **Audience Alignment (20% weight)**
   - Addresses pain points (0-100)
   - Appropriate tone
   - Reading level match
   - Intent fulfillment

**DECISION LOGIC:**
1. Calculate overall_score = (SEO×0.3) + (Quality×0.3) + (Engagement×0.2) + (Audience×0.2)
2. Approve (APPROVED) only if: overall_score ≥ {WorkflowConfig.OVERALL_PASS_THRESHOLD} AND seo_performance ≥ {WorkflowConfig.SEO_PASS_THRESHOLD}
3. Reject (REJECTED) if: overall_score < {WorkflowConfig.OVERALL_PASS_THRESHOLD} OR seo_performance < {WorkflowConfig.SEO_PASS_THRESHOLD}

**OUTPUT FORMAT (JSON):**
{{
  "overall_score": 87.5,
  "final_decision": "APPROVED",
  "publication_readiness": "Ready for publication",
  "score_breakdown": {{
    "seo_performance": {{
      "score": 85,
      "weight": 30,
      "weighted_score": 25.5,
      "justification": "Strong keyword optimization and readability"
    }},
    "content_quality": {{
      "score": 88,
      "weight": 30,
      "weighted_score": 26.4,
      "justification": "Original insights with specific examples"
    }},
    "engagement_potential": {{
      "score": 90,
      "weight": 20,
      "weighted_score": 18.0,
      "justification": "Compelling hook, scannable structure, clear CTA"
    }},
    "audience_alignment": {{
      "score": 87,
      "weight": 20,
      "weighted_score": 17.4,
      "justification": "Addresses pain points, appropriate tone"
    }}
  }},
  "strengths": [
    "Excellent SEO optimization with 1.8% keyword density",
    "Comprehensive coverage with actionable steps",
    "Strong engagement with compelling examples",
    "Clear structure with proper heading hierarchy"
  ],
  "weaknesses": [
    "Could include one additional case study",
    "Consider adding more statistical data"
  ],
  "suggested_improvements": [
    "Add 1-2 more internal linking opportunities",
    "Include a data visualization description"
  ],
  "approval_criteria_met": {{
    "seo_score_above_{WorkflowConfig.SEO_PASS_THRESHOLD}": true,
    "overall_score_above_{WorkflowConfig.OVERALL_PASS_THRESHOLD}": true,
    "readability_adequate": true,
    "word_count_in_range": true,
    "publication_ready": true
  }}
}}

**REQUIREMENTS:**
1. Be STRICT - only APPROVE if ALL criteria met
2. If SEO score < {WorkflowConfig.SEO_PASS_THRESHOLD}, MUST reject
3. If overall < {WorkflowConfig.OVERALL_PASS_THRESHOLD}, MUST reject
4. Provide SPECIFIC strengths and weaknesses
5. Justify ALL scores with concrete examples
6. Output ONLY valid JSON

Evaluate thoroughly and make your decision.
""")

    @message_handler
    async def handle_seo_analysis(self, message: ContentMessage, ctx: MessageContext) -> None:
        """Generate final quality score and publication decision"""
        print(f"\n{'='*80}\n🎯 SCORER AGENT - Final Evaluation (Threshold: {WorkflowConfig.OVERALL_PASS_THRESHOLD})\n{'='*80}")
        
        # Get all previous results
        research = await result_collector.get("research", {})
        content = await result_collector.get("content", {})
        seo_analysis = await result_collector.get("seo_analysis", {})
        
        prompt = f"""Complete workflow results:

RESEARCH:
{json.dumps(research, indent=2)[:1000]}...

CONTENT:
{json.dumps(content, indent=2)[:1000]}...

SEO ANALYSIS:
{json.dumps(seo_analysis, indent=2)}

Evaluate and provide final score.

CRITICAL THRESHOLDS:
- SEO must be ≥ {WorkflowConfig.SEO_PASS_THRESHOLD} (not {WorkflowConfig.SEO_PASS_THRESHOLD - 5})
- Overall must be ≥ {WorkflowConfig.OVERALL_PASS_THRESHOLD} (not {WorkflowConfig.OVERALL_PASS_THRESHOLD - 5})

Output ONLY JSON."""
        
        try:
            agent_id = MessageHandlerContext.agent_id()
            llm_result = await asyncio.wait_for(
                self._model_client.create(
                    messages=[self._system_message, UserMessage(content=prompt, source="default")],
                    cancellation_token=ctx.cancellation_token,
                ),
                timeout=WorkflowConfig.LLM_TIMEOUT
            )
            
            response = llm_result.content
            final_score = self._parse_json_safe(response)
            
            print(f"📈 Final Score: {final_score.get('overall_score', 0)}/100")
            print(f"🎯 Decision: {final_score.get('final_decision', 'N/A')}\n")
            
            # Store final score
            await result_collector.store("final_score", final_score)
            
            # Forward to output agent
            await self.publish_message(
                ContentMessage(
                    content=response,
                    metadata={"stage": "scoring", "final_decision": final_score.get("final_decision")},
                    stage="scoring"
                ),
                topic_id=TopicId(WorkflowConfig.TOPIC_OUTPUT, source="default")
            )
            
        except asyncio.TimeoutError:
            error_msg = "Scorer agent timeout"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
        except Exception as e:
            error_msg = f"Scorer agent error: {str(e)}"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
    
    @staticmethod
    def _parse_json_safe(text: str) -> Dict[str, Any]:
        """Safely parse JSON"""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            return {"error": f"Failed to parse JSON: {str(e)}", "raw_text": text[:500]}


# ============================================================================
# Agent 5: Output Agent (Unchanged)
# ============================================================================

@type_subscription(topic_type=WorkflowConfig.TOPIC_OUTPUT)
class OutputAgent(RoutedAgent):
    """Final output agent - terminates workflow"""
    
    def __init__(self):
        super().__init__("Output Agent")
    
    @message_handler
    async def handle_final_score(self, message: ContentMessage, ctx: MessageContext) -> None:
        """Receive final results and end workflow"""
        print(f"\n{'='*80}\n✅ OUTPUT AGENT - Workflow Complete\n{'='*80}")
        
        final_score = await result_collector.get("final_score", {})
        
        print(f"📊 Overall Score: {final_score.get('overall_score', 0)}/100")
        print(f"🎯 Decision: {final_score.get('final_decision', 'N/A')}")
        print(f"📄 Publication Status: {final_score.get('publication_readiness', 'N/A')}")
        print(f"{'='*80}\n")


# ============================================================================
# Main Workflow Execution
# ============================================================================

async def run_content_workflow(user_request: str) -> WorkflowResult:
    """
    Execute the complete content generation workflow with publication-ready standards
    
    Args:
        user_request: User's content generation request
    
    Returns:
        WorkflowResult with all agent outputs and final scores
    """
    start_time = asyncio.get_event_loop().time()
    
    # Clear previous results
    await result_collector.clear()
    
    print(f"\n{'='*80}")
    print(f"🚀 PUBLICATION-READY CONTENT WORKFLOW")
    print(f"{'='*80}")
    print(f"Request: {user_request[:100]}...")
    print(f"Thresholds: SEO ≥ {WorkflowConfig.SEO_PASS_THRESHOLD}, Overall ≥ {WorkflowConfig.OVERALL_PASS_THRESHOLD}")
    print(f"{'='*80}\n")
    
    # Validate API key
    if not WorkflowConfig.get_openai_api_key():
        error_msg = "OPENAI_API_KEY not found in environment variables"
        print(f"❌ {error_msg}")
        return WorkflowResult(success=False, error=error_msg)
    
    # Initialize model client
    model_client = OpenAIChatCompletionClient(
        model=WorkflowConfig.OPENAI_MODEL,
        api_key=WorkflowConfig.get_openai_api_key(),
    )
    
    # Create runtime
    runtime = SingleThreadedAgentRuntime()
    
    try:
        # Register all agents with enhanced configuration
        research_topic = WorkflowConfig.TOPIC_RESEARCH
        await ResearchAgent.register(
            runtime,
            type=research_topic,
            factory=lambda: ResearchAgent(
                model_client,
                serp_api_key=WorkflowConfig.get_serp_api_key()
            )
        )
        
        writer_topic = WorkflowConfig.TOPIC_WRITER
        await ContentWriterAgent.register(
            runtime,
            type=writer_topic,
            factory=lambda: ContentWriterAgent(model_client)
        )
        
        seo_topic = WorkflowConfig.TOPIC_SEO
        await SEOAgent.register(
            runtime,
            type=seo_topic,
            factory=lambda: SEOAgent(model_client)
        )
        
        scorer_topic = WorkflowConfig.TOPIC_SCORER
        await ScorerAgent.register(
            runtime,
            type=scorer_topic,
            factory=lambda: ScorerAgent(model_client)
        )
        
        output_topic = WorkflowConfig.TOPIC_OUTPUT
        await OutputAgent.register(
            runtime,
            type=output_topic,
            factory=lambda: OutputAgent()
        )
        
        # Start runtime
        runtime.start()
        
        # Trigger workflow
        await runtime.send_message(
            ContentMessage(content=user_request),
            TopicId(research_topic, source="user")
        )
        
        # Wait for workflow completion with timeout
        await asyncio.wait_for(
            runtime.stop_when_idle(),
            timeout=WorkflowConfig.WORKFLOW_TIMEOUT
        )
        
        # Collect results
        results = await result_collector.get_all()
        execution_time = asyncio.get_event_loop().time() - start_time
        
        # Check for errors
        if "error" in results:
            return WorkflowResult(
                success=False,
                error=results.get("error"),
                execution_time=execution_time
            )
        
        # Return successful result
        return WorkflowResult(
            success=True,
            research=results.get("research"),
            content=results.get("content"),
            seo_analysis=results.get("seo_analysis"),
            final_score=results.get("final_score"),
            execution_time=execution_time
        )
        
    except asyncio.TimeoutError:
        error_msg = f"Workflow timeout after {WorkflowConfig.WORKFLOW_TIMEOUT}s"
        print(f"❌ {error_msg}")
        return WorkflowResult(
            success=False,
            error=error_msg,
            execution_time=asyncio.get_event_loop().time() - start_time
        )
    except Exception as e:
        error_msg = f"Workflow error: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return WorkflowResult(
            success=False,
            error=error_msg,
            execution_time=asyncio.get_event_loop().time() - start_time
        )
    finally:
        try:
            await runtime.stop()
        except RuntimeError:
            # Runtime might already be stopped
            pass


# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """Interactive CLI for testing the workflow"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  PUBLICATION-READY CONTENT GENERATION SYSTEM                 ║
    ║  ------------------------------------------------------------ ║
    ║  Enhanced with:                                               ║
    ║  • SERP API Integration (optional)                           ║
    ║  • SEO Threshold: 80/100 (was 75)                           ║
    ║  • Overall Threshold: 85/100 (was 80)                        ║
    ║  • Publication-Ready Prompts                                  ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    if not WorkflowConfig.get_openai_api_key():
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    if not WorkflowConfig.get_serp_api_key():
        print("⚠️  Warning: SERP_API_KEY not set (optional)")
        print("For better results, get free key at: https://serpapi.com")
        print("Set with: export SERP_API_KEY='your-key-here'\n")
    
    # Example request
    example_request = """Generate a 1500-word SEO-optimized blog post about "AI Marketing Automation Tools for Small Businesses in 2024"

REQUIREMENTS:
- Target Audience: Small business owners, 30-50 years old, 5-20 employees
- Primary Keywords: AI marketing automation, small business marketing tools
- Word Count: 1500 words (STRICT)
- Tone: Professional yet approachable
- Structure: 5 main H2 sections, each with 2-3 H3 subsections
- Include: Specific tool examples, pricing, ROI data, implementation steps
- SEO Target: Score ≥ 80
- Overall Target: Score ≥ 85"""
    
    print(f"Example request:\n{example_request}\n")
    print("=" * 80)
    
    user_input = input("\nEnter your request (or press Enter to use example): ").strip()
    request = user_input if user_input else example_request
    
    print("\n🚀 Starting workflow...\n")
    
    result = await run_content_workflow(request)
    
    print("\n" + "=" * 80)
    print("📊 WORKFLOW RESULTS")
    print("=" * 80)
    print(f"Success: {result.success}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    
    if result.success:
        print(f"\n✅ Content Generation Successful!")
        
        if result.final_score:
            print(f"\n🎯 Final Scores:")
            print(f"   Overall: {result.final_score.get('overall_score', 0)}/100")
            print(f"   Decision: {result.final_score.get('final_decision', 'N/A')}")
            print(f"   Status: {result.final_score.get('publication_readiness', 'N/A')}")
        
        if result.seo_analysis:
            print(f"\n📊 SEO Analysis:")
            print(f"   SEO Score: {result.seo_analysis.get('seo_score', 0)}/100")
            print(f"   Status: {result.seo_analysis.get('validation_status', 'N/A')}")
        
        if result.content:
            print(f"\n📝 Content:")
            print(f"   Title: {result.content.get('title', 'N/A')}")
            print(f"   Word Count: {result.content.get('word_count', 0)}")
    else:
        print(f"\n❌ Workflow Failed: {result.error}")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
=======
"""
RTCFR Multi-Agent Content Generation System - PUBLICATION READY VERSION
========================================================================
Sequential workflow with Research → Writer → SEO → Scorer agents
Enhanced with SERP API integration and stricter publication standards

Key Improvements:
- SERP API integration for real-world research
- SEO threshold increased to 80 (from 75)
- Overall threshold increased to 85 (from 80)
- Publication-ready prompts with self-validation
- Stricter word count and readability requirements
"""

import os
import json
import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from autogen_core import (
    MessageContext,
    MessageHandlerContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    message_handler,
    type_subscription,
)
from autogen_core.models import SystemMessage, UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient


# ============================================================================
# Configuration
# ============================================================================

class WorkflowConfig:
    """Central configuration for the workflow"""
    OPENAI_MODEL = "gpt-4o-mini"
    
    @staticmethod
    def get_openai_api_key():
        return os.getenv("OPENAI_API_KEY")
    
    @staticmethod
    def get_serp_api_key():
        return os.getenv("SERP_API_KEY")  # Optional but recommended
    
    # Topic identifiers
    TOPIC_RESEARCH = "research_agent"
    TOPIC_WRITER = "content_writer"
    TOPIC_SEO = "seo_agent"
    TOPIC_SCORER = "scorer_agent"
    TOPIC_OUTPUT = "output_agent"
    
    # Thresholds - INCREASED FOR PUBLICATION QUALITY
    SEO_PASS_THRESHOLD = 80  # Increased from 75
    OVERALL_PASS_THRESHOLD = 85  # Increased from 80
    MIN_WORD_COUNT = 1000  # Minimum words for SEO
    MAX_WORD_COUNT = 2000  # Maximum words for readability
    TARGET_READABILITY = 65  # Flesch Reading Ease target
    
    # Timeouts (seconds)
    LLM_TIMEOUT = 120
    WORKFLOW_TIMEOUT = 600


# ============================================================================
# Message Protocol
# ============================================================================

@dataclass
class ContentMessage:
    """Standardized message format for inter-agent communication"""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    stage: str = ""


@dataclass
class WorkflowResult:
    """Complete workflow result for API responses"""
    success: bool
    research: Optional[Dict[str, Any]] = None
    content: Optional[Dict[str, Any]] = None
    seo_analysis: Optional[Dict[str, Any]] = None
    final_score: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0


# ============================================================================
# Result Collector (Global State Management)
# ============================================================================

class ResultCollector:
    """Thread-safe result collection for workflow outputs"""
    
    def __init__(self):
        self._results: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
    
    async def store(self, key: str, value: Any):
        async with self._lock:
            self._results[key] = value
    
    async def get(self, key: str, default=None):
        async with self._lock:
            return self._results.get(key, default)
    
    async def get_all(self) -> Dict[str, Any]:
        async with self._lock:
            return self._results.copy()
    
    async def clear(self):
        async with self._lock:
            self._results.clear()

# Global result collector instance
result_collector = ResultCollector()


# ============================================================================
# SERP API Integration
# ============================================================================

class SerpAPIResearcher:
    """Integrate real-world web search for accurate research"""
    
    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
    
    def search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Perform web search using SERP API"""
        if not self.api_key:
            return {"error": "SERP API key not configured"}
        
        try:
            import requests
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
# Agent 1: Enhanced Research Agent with SERP API
# ============================================================================

@type_subscription(topic_type=WorkflowConfig.TOPIC_RESEARCH)
class ResearchAgent(RoutedAgent):
    """Expert Content Research Analyst with web search integration"""
    
    def __init__(self, model_client, serp_api_key: Optional[str] = None):
        super().__init__("research_agent")
        self._model_client = model_client
        self._serp_researcher = SerpAPIResearcher(serp_api_key) if serp_api_key else None
        
        self._system_message = SystemMessage(content="""
**ROLE:**
You are an EXPERT Content Research Analyst with 10+ years of experience in SEO, content strategy, and audience analysis.

**CRITICAL MISSION:** Provide research that will result in PUBLICATION-READY content scoring:
- SEO Score ≥ 80/100 (NOT 75, NOT 78 - MINIMUM 80)
- Overall Quality Score ≥ 85/100
- Flesch Reading Ease ≥ 65
- Publication Status: READY FOR PUBLICATION

**YOUR RESEARCH MUST ENSURE:**

1. **HIGH-VOLUME, LOW-COMPETITION KEYWORDS**
   - Primary keywords: 1000+ monthly searches
   - Include search volume data if available
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
   - Recommended word count: 1000-2000 words
   - Optimal heading structure (number of H2s, H3s)
   - Content depth requirements
   - Internal linking opportunities

**OUTPUT FORMAT (STRICT JSON):**
{
  "topic": "Specific, SEO-optimized topic title",
  "niche": "Precise niche category",
  "keywords": {
    "primary": ["keyword1", "keyword2"],
    "secondary": ["keyword3", "keyword4"],
    "long_tail": ["specific phrase 1", "specific phrase 2"],
    "questions": ["how to X?", "what is Y?", "why Z?"]
  },
  "trending_aspects": [
    "2024 trend 1 with specific data",
    "Industry shift 2 with examples",
    "Emerging topic 3 with statistics"
  ],
  "target_audience": {
    "primary": "Specific demographic with age/location/profession",
    "demographics": {
      "age_range": "25-45",
      "locations": ["US", "UK", "Canada"],
      "professions": ["specific job 1", "specific job 2"],
      "income_level": "range",
      "tech_savviness": "level"
    },
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
  },
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
  "content_strategy": {
    "recommended_word_count": 1500,
    "structure": {
      "introduction_length": "150-200 words with hook",
      "main_sections": 5,
      "h2_headings": ["Heading 1", "Heading 2", "Heading 3", "Heading 4", "Heading 5"],
      "h3_subsections": "2-3 per H2",
      "conclusion_length": "150-200 words with CTA"
    },
    "content_depth": "Comprehensive with examples, data, and actionable steps",
    "visual_elements": ["Recommended visual 1", "Chart/graph 2", "Infographic 3"],
    "internal_linking": ["Related topic 1", "Related topic 2", "Related topic 3"]
  },
  "seo_requirements": {
    "title_format": "Primary keyword | Benefit/Number | Brand",
    "meta_description_template": "Hook + benefit + primary keyword + CTA",
    "target_readability": 65,
    "keyword_density": {
      "primary": "1.5-2%",
      "secondary": "0.8-1.2%"
    },
    "heading_keywords": "Primary keyword in H1, variants in H2s"
  },
  "quality_benchmarks": {
    "seo_score_target": 80,
    "overall_score_target": 85,
    "expected_outcomes": [
      "Rank in top 10 for primary keywords",
      "Minimum 3-minute average read time",
      "Publication-ready without revisions"
    ]
  },
  "tone_suggestion": "Specific tone with examples"
}

**REQUIREMENTS:**
- ALL fields must be filled with SPECIFIC, ACTIONABLE data
- NO generic statements - use concrete examples and numbers
- If web search data is provided, incorporate it extensively
- Ensure research directly supports SEO score ≥ 80
- Think: "Will this research lead to publication-ready content?"
- Output ONLY valid JSON - no markdown, no commentary

**WEB SEARCH CONTEXT (if provided):**
{web_search_context}
""")

    @message_handler
    async def handle_user_request(self, message: ContentMessage, ctx: MessageContext) -> None:
        """Process research request with optional web search"""
        print(f"\n{'='*80}\n🔍 ENHANCED RESEARCH AGENT - Processing Request\n{'='*80}")
        
        user_request = message.content
        
        # Perform web search if SERP API is available
        web_search_context = ""
        if self._serp_researcher:
            print("🌐 Performing web search for real-time data...")
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
                print(f"⚠️ Web search unavailable: {search_results.get('error')}")
        
        try:
            # Update system message with web search context
            enhanced_prompt = self._system_message.content.replace("{web_search_context}", web_search_context)
            updated_system = SystemMessage(content=enhanced_prompt)
            
            prompt = f"User Request: {user_request}\n\nProvide comprehensive research in JSON format that will lead to SEO score ≥ 80 and Overall score ≥ 85."
            
            agent_id = MessageHandlerContext.agent_id()
            llm_result = await asyncio.wait_for(
                self._model_client.create(
                    messages=[updated_system, UserMessage(content=prompt, source="default")],
                    cancellation_token=ctx.cancellation_token,
                ),
                timeout=WorkflowConfig.LLM_TIMEOUT
            )
            
            response = llm_result.content
            print(f"📊 Research Output Generated ({len(response)} chars)\n")
            
            # Store research result
            await result_collector.store("research", self._parse_json_safe(response))
            
            # Forward to writer agent
            await self.publish_message(
                ContentMessage(
                    content=response,
                    metadata={"stage": "research", "original_request": user_request},
                    stage="research"
                ),
                topic_id=TopicId(WorkflowConfig.TOPIC_WRITER, source="default")
            )
            
        except asyncio.TimeoutError:
            error_msg = "Research agent timeout"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
        except Exception as e:
            error_msg = f"Research agent error: {str(e)}"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
    
    @staticmethod
    def _parse_json_safe(text: str) -> Dict[str, Any]:
        """Safely parse JSON, handling markdown code blocks"""
        try:
            # Remove markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            return {"error": f"Failed to parse JSON: {str(e)}", "raw_text": text[:500]}


# ============================================================================
# Agent 2: Publication-Ready Content Writer Agent
# ============================================================================

@type_subscription(topic_type=WorkflowConfig.TOPIC_WRITER)
class ContentWriterAgent(RoutedAgent):
    """Master content writer focused on publication-ready quality"""
    
    def __init__(self, model_client):
        super().__init__("content_writer")
        self._model_client = model_client
        
        self._system_message = SystemMessage(content="""
**ROLE:**
You are a MASTER Content Writer with 15+ years of experience creating TOP-RANKING, PUBLICATION-READY content for major publications.

**NON-NEGOTIABLE MISSION:** Create content that achieves:
- ✅ SEO Score ≥ 80/100 (MINIMUM, aim for 85+)
- ✅ Overall Quality Score ≥ 85/100
- ✅ Flesch Reading Ease ≥ 65
- ✅ Status: APPROVED and READY FOR PUBLICATION

**IF YOUR CONTENT SCORES BELOW THESE THRESHOLDS, IT IS A FAILURE.**

**MANDATORY QUALITY STANDARDS:**

1. **WORD COUNT & STRUCTURE (Critical)**
   - 1000-2000 words (STRICT - will be checked)
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
   - Use <h2> for main sections ONLY
   - Use <h3> for subsections ONLY
   - Use <strong> for key phrases (not entire sentences)
   - Use <ul>/<ol> for lists
   - Use <p> for paragraphs (no orphaned text)
   - Example structure:
     <h2>Section Title with Primary or Secondary Keyword</h2>
     <p>Opening paragraph with transition and keyword variant.</p>
     <h3>Subsection Title</h3>
     <p>Content paragraph with <strong>important phrases</strong> emphasized.</p>
     <ul>
       <li>Bullet point with specific detail</li>
       <li>Another concrete point with example</li>
     </ul>

7. **TITLE & META (Critical for SEO Score)**
   - Title format: "Primary Keyword: Compelling Benefit [Year]"
   - Title must be 55-65 characters
   - Meta description must include:
     * Primary keyword (first 80 characters)
     * Benefit statement
     * Urgency or CTA
     * 150-160 characters total

**OUTPUT FORMAT (STRICT JSON):**
{
  "title": "SEO-optimized title 55-65 chars with primary keyword",
  "meta_description": "150-160 chars with primary keyword, benefit, and CTA",
  "content": "FULL HTML CONTENT WITH PROPER STRUCTURE",
  "word_count": 1500,
  "keywords_used": {
    "primary": ["keyword1 (used X times)", "keyword2 (used Y times)"],
    "secondary": ["keyword3 (used A times)", "keyword4 (used B times)"]
  },
  "keyword_density": {
    "primary_keyword_1": "1.8%",
    "primary_keyword_2": "1.5%",
    "secondary_keyword_1": "1.0%"
  },
  "readability_metrics": {
    "avg_sentence_length": 18,
    "longest_sentence": 28,
    "paragraph_count": 25,
    "avg_paragraph_length": "4 sentences"
  },
  "internal_link_suggestions": [
    "Anchor: 'related topic 1' → URL: /related-topic-1",
    "Anchor: 'learn more about 2' → URL: /topic-2"
  ],
  "content_structure": {
    "introduction": "Hook + problem + benefit (150-200 words)",
    "main_sections": [
      "H2: Section 1 Title (250 words with 2 H3s)",
      "H2: Section 2 Title (250 words with 2 H3s)",
      "H2: Section 3 Title (250 words with 2 H3s)",
      "H2: Section 4 Title (250 words with 2 H3s)",
      "H2: Section 5 Title (250 words with 2 H3s)"
    ],
    "conclusion": "Summary + CTA (150-200 words)"
  },
  "quality_self_check": {
    "estimated_seo_score": 85,
    "estimated_readability": 68,
    "estimated_overall_score": 87,
    "confidence": "HIGH - meets all publication standards"
  }
}

**SELF-CHECK BEFORE OUTPUTTING:**
- [ ] Word count 1000-2000? ✓
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
""")

    @message_handler
    async def handle_research(self, message: ContentMessage, ctx: MessageContext) -> None:
        """Generate publication-ready content from research"""
        print(f"\n{'='*80}\n✍️ PUBLICATION-READY WRITER - Generating Content\n{'='*80}")
        
        research_content = message.content
        
        prompt = f"""Research Data:
{research_content}

Generate PUBLICATION-READY content in JSON format.

CRITICAL: Content MUST achieve:
- SEO Score ≥ 80 (not 75, not 78)
- Overall Score ≥ 85 (not 80)
- Word count: 1000-2000 words (STRICT)
- Keyword density: 1.5-2% for primary keywords
- Readability: Flesch ≥ 65

Output ONLY JSON."""
        
        try:
            agent_id = MessageHandlerContext.agent_id()
            llm_result = await asyncio.wait_for(
                self._model_client.create(
                    messages=[self._system_message, UserMessage(content=prompt, source="default")],
                    cancellation_token=ctx.cancellation_token,
                ),
                timeout=WorkflowConfig.LLM_TIMEOUT
            )
            
            response = llm_result.content
            print(f"📝 Content Generated ({len(response)} chars)\n")
            
            # Store content result
            await result_collector.store("content", self._parse_json_safe(response))
            
            # Forward to SEO agent
            await self.publish_message(
                ContentMessage(
                    content=response,
                    metadata={"stage": "content_writing"},
                    stage="content_writing"
                ),
                topic_id=TopicId(WorkflowConfig.TOPIC_SEO, source="default")
            )
            
        except asyncio.TimeoutError:
            error_msg = "Content writer timeout"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
        except Exception as e:
            error_msg = f"Content writer error: {str(e)}"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
    
    @staticmethod
    def _parse_json_safe(text: str) -> Dict[str, Any]:
        """Safely parse JSON, handling markdown code blocks"""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            return {"error": f"Failed to parse JSON: {str(e)}", "raw_text": text[:500]}


# ============================================================================
# Agent 3: SEO Validation Agent (Enhanced Thresholds)
# ============================================================================

@type_subscription(topic_type=WorkflowConfig.TOPIC_SEO)
class SEOAgent(RoutedAgent):
    """SEO Expert with stricter validation standards"""
    
    def __init__(self, model_client):
        super().__init__("seo_agent")
        self._model_client = model_client
        
        self._system_message = SystemMessage(content=f"""
**ROLE:**
You are an SEO Technical Expert and Content Quality Auditor with 10+ years of experience optimizing content for top search engine rankings. You specialize in keyword optimization, readability analysis, and technical SEO validation.

**TASK:**
Validate the generated content against strict SEO best practices and publication standards. Perform comprehensive technical analysis and provide actionable recommendations.

**CONTEXT:**
You are analyzing content that MUST meet these publication thresholds:
- SEO Score: ≥ 80/100 (STRICT - not 75)
- Keyword Density: Primary 1.5-2%, Secondary 0.8-1.2%
- Readability: Flesch Reading Ease ≥ 65
- Word Count: 1000-2000 words

**VALIDATION CRITERIA:**

1. **Keyword Optimization (30 points)**
   - Primary keyword in title (5 pts)
   - Primary keyword in first 100 words (5 pts)
   - Primary keyword in at least 3 H2 headings (5 pts)
   - Primary keyword density 1.5-2% (10 pts)
   - Secondary keyword integration (5 pts)

2. **Content Structure (25 points)**
   - Single H1 tag present (5 pts)
   - 5-7 H2 sections (10 pts)
   - 2-3 H3 per H2 (5 pts)
   - Proper HTML hierarchy (5 pts)

3. **Readability (25 points)**
   - Flesch Reading Ease ≥ 65 (10 pts)
   - Average sentence length 15-20 words (8 pts)
   - No sentences > 30 words (7 pts)

4. **Meta Elements (10 points)**
   - Title 55-65 characters (5 pts)
   - Meta description 150-160 characters (5 pts)

5. **Technical SEO (10 points)**
   - Internal link suggestions (5 pts)
   - Paragraph length 3-5 sentences (5 pts)

**SUCCESS CRITERIA:**
- Overall SEO score ≥ {WorkflowConfig.SEO_PASS_THRESHOLD}/100 to PASS validation
- If score < {WorkflowConfig.SEO_PASS_THRESHOLD}, status = FAIL, requires_revision = true

**OUTPUT FORMAT (JSON):**
{{
  "seo_score": 85,
  "validation_status": "PASS",
  "pass_threshold": {WorkflowConfig.SEO_PASS_THRESHOLD},
  "requires_revision": false,
  "analysis": {{
    "keyword_optimization": {{
      "score": 28,
      "primary_keyword_in_title": true,
      "primary_keyword_in_first_100": true,
      "primary_keyword_in_headings": 5,
      "primary_keyword_density": "1.8%",
      "secondary_keyword_density": "1.0%",
      "issues": []
    }},
    "content_structure": {{
      "score": 24,
      "h1_count": 1,
      "h2_count": 6,
      "h3_count": 15,
      "heading_hierarchy_valid": true,
      "issues": []
    }},
    "readability": {{
      "score": 24,
      "flesch_reading_ease": 68,
      "avg_sentence_length": 18,
      "longest_sentence": 28,
      "sentences_over_30_words": 0,
      "issues": []
    }},
    "meta_elements": {{
      "score": 10,
      "title_length": 62,
      "meta_description_length": 158,
      "title_has_keyword": true,
      "meta_has_keyword": true,
      "issues": []
    }},
    "technical_seo": {{
      "score": 9,
      "internal_links_present": true,
      "paragraph_structure_valid": true,
      "issues": ["Consider adding 1-2 more internal links"]
    }}
  }},
  "recommendations": [
    "Excellent keyword optimization - maintain 1.8% density",
    "Add one more internal link for better site structure",
    "Content meets all publication standards"
  ]
}}

**REQUIREMENTS:**
1. Perform ACTUAL analysis - don't just approve without checking
2. Calculate REAL keyword density and readability scores
3. If SEO score < {WorkflowConfig.SEO_PASS_THRESHOLD}, status MUST be "FAIL"
4. Provide SPECIFIC recommendations for any issues found
5. Be STRICT - publication quality requires high standards
6. Output ONLY valid JSON

Analyze the content thoroughly and provide detailed validation.
""")

    @message_handler
    async def handle_content(self, message: ContentMessage, ctx: MessageContext) -> None:
        """Validate content for SEO compliance with strict standards"""
        print(f"\n{'='*80}\n📊 SEO AGENT - Validating Content (Threshold: {WorkflowConfig.SEO_PASS_THRESHOLD})\n{'='*80}")
        
        content_data = message.content
        
        prompt = f"""Content to validate:
{content_data}

Perform STRICT SEO validation.
Threshold for PASS: ≥ {WorkflowConfig.SEO_PASS_THRESHOLD}/100
Output ONLY JSON."""
        
        try:
            agent_id = MessageHandlerContext.agent_id()
            llm_result = await asyncio.wait_for(
                self._model_client.create(
                    messages=[self._system_message, UserMessage(content=prompt, source="default")],
                    cancellation_token=ctx.cancellation_token,
                ),
                timeout=WorkflowConfig.LLM_TIMEOUT
            )
            
            response = llm_result.content
            print(f"🔍 SEO Analysis Complete\n")
            
            # Store SEO result
            await result_collector.store("seo_analysis", self._parse_json_safe(response))
            
            # Forward to scorer
            await self.publish_message(
                ContentMessage(
                    content=response,
                    metadata={"stage": "seo_validation"},
                    stage="seo_validation"
                ),
                topic_id=TopicId(WorkflowConfig.TOPIC_SCORER, source="default")
            )
            
        except asyncio.TimeoutError:
            error_msg = "SEO agent timeout"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
        except Exception as e:
            error_msg = f"SEO agent error: {str(e)}"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
    
    @staticmethod
    def _parse_json_safe(text: str) -> Dict[str, Any]:
        """Safely parse JSON"""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            return {"error": f"Failed to parse JSON: {str(e)}", "raw_text": text[:500]}


# ============================================================================
# Agent 4: Quality Scorer Agent (Enhanced Thresholds)
# ============================================================================

@type_subscription(topic_type=WorkflowConfig.TOPIC_SCORER)
class ScorerAgent(RoutedAgent):
    """Quality scorer with strict publication standards"""
    
    def __init__(self, model_client):
        super().__init__("scorer_agent")
        self._model_client = model_client
        
        self._system_message = SystemMessage(content=f"""
**ROLE:**
You are a Senior Content Quality Auditor and Editorial Director with 15+ years evaluating content for top-tier publications. You make final APPROVE/REJECT decisions based on comprehensive quality analysis.

**TASK:**
Evaluate the complete content generation output and provide a final quality score and publication decision.

**PUBLICATION STANDARDS (STRICT):**
1. SEO Performance: Must be ≥ {WorkflowConfig.SEO_PASS_THRESHOLD}/100
2. Overall Quality: Must be ≥ {WorkflowConfig.OVERALL_PASS_THRESHOLD}/100
3. Content must be publication-ready without revisions

**SCORING COMPONENTS:**

1. **SEO Performance (30% weight)**
   - Based on SEO agent's validation
   - Must score ≥ {WorkflowConfig.SEO_PASS_THRESHOLD} to pass

2. **Content Quality (30% weight)**
   - Originality and depth (0-100)
   - Specific examples and data
   - Actionable insights
   - Research backing

3. **Engagement Potential (20% weight)**
   - Hook effectiveness (0-100)
   - Scannability (headings, lists, formatting)
   - Value delivery per section
   - CTA clarity

4. **Audience Alignment (20% weight)**
   - Addresses pain points (0-100)
   - Appropriate tone
   - Reading level match
   - Intent fulfillment

**DECISION LOGIC:**
1. Calculate overall_score = (SEO×0.3) + (Quality×0.3) + (Engagement×0.2) + (Audience×0.2)
2. Approve (APPROVED) only if: overall_score ≥ {WorkflowConfig.OVERALL_PASS_THRESHOLD} AND seo_performance ≥ {WorkflowConfig.SEO_PASS_THRESHOLD}
3. Reject (REJECTED) if: overall_score < {WorkflowConfig.OVERALL_PASS_THRESHOLD} OR seo_performance < {WorkflowConfig.SEO_PASS_THRESHOLD}

**OUTPUT FORMAT (JSON):**
{{
  "overall_score": 87.5,
  "final_decision": "APPROVED",
  "publication_readiness": "Ready for publication",
  "score_breakdown": {{
    "seo_performance": {{
      "score": 85,
      "weight": 30,
      "weighted_score": 25.5,
      "justification": "Strong keyword optimization and readability"
    }},
    "content_quality": {{
      "score": 88,
      "weight": 30,
      "weighted_score": 26.4,
      "justification": "Original insights with specific examples"
    }},
    "engagement_potential": {{
      "score": 90,
      "weight": 20,
      "weighted_score": 18.0,
      "justification": "Compelling hook, scannable structure, clear CTA"
    }},
    "audience_alignment": {{
      "score": 87,
      "weight": 20,
      "weighted_score": 17.4,
      "justification": "Addresses pain points, appropriate tone"
    }}
  }},
  "strengths": [
    "Excellent SEO optimization with 1.8% keyword density",
    "Comprehensive coverage with actionable steps",
    "Strong engagement with compelling examples",
    "Clear structure with proper heading hierarchy"
  ],
  "weaknesses": [
    "Could include one additional case study",
    "Consider adding more statistical data"
  ],
  "suggested_improvements": [
    "Add 1-2 more internal linking opportunities",
    "Include a data visualization description"
  ],
  "approval_criteria_met": {{
    "seo_score_above_{WorkflowConfig.SEO_PASS_THRESHOLD}": true,
    "overall_score_above_{WorkflowConfig.OVERALL_PASS_THRESHOLD}": true,
    "readability_adequate": true,
    "word_count_in_range": true,
    "publication_ready": true
  }}
}}

**REQUIREMENTS:**
1. Be STRICT - only APPROVE if ALL criteria met
2. If SEO score < {WorkflowConfig.SEO_PASS_THRESHOLD}, MUST reject
3. If overall < {WorkflowConfig.OVERALL_PASS_THRESHOLD}, MUST reject
4. Provide SPECIFIC strengths and weaknesses
5. Justify ALL scores with concrete examples
6. Output ONLY valid JSON

Evaluate thoroughly and make your decision.
""")

    @message_handler
    async def handle_seo_analysis(self, message: ContentMessage, ctx: MessageContext) -> None:
        """Generate final quality score and publication decision"""
        print(f"\n{'='*80}\n🎯 SCORER AGENT - Final Evaluation (Threshold: {WorkflowConfig.OVERALL_PASS_THRESHOLD})\n{'='*80}")
        
        # Get all previous results
        research = await result_collector.get("research", {})
        content = await result_collector.get("content", {})
        seo_analysis = await result_collector.get("seo_analysis", {})
        
        prompt = f"""Complete workflow results:

RESEARCH:
{json.dumps(research, indent=2)[:1000]}...

CONTENT:
{json.dumps(content, indent=2)[:1000]}...

SEO ANALYSIS:
{json.dumps(seo_analysis, indent=2)}

Evaluate and provide final score.

CRITICAL THRESHOLDS:
- SEO must be ≥ {WorkflowConfig.SEO_PASS_THRESHOLD} (not {WorkflowConfig.SEO_PASS_THRESHOLD - 5})
- Overall must be ≥ {WorkflowConfig.OVERALL_PASS_THRESHOLD} (not {WorkflowConfig.OVERALL_PASS_THRESHOLD - 5})

Output ONLY JSON."""
        
        try:
            agent_id = MessageHandlerContext.agent_id()
            llm_result = await asyncio.wait_for(
                self._model_client.create(
                    messages=[self._system_message, UserMessage(content=prompt, source="default")],
                    cancellation_token=ctx.cancellation_token,
                ),
                timeout=WorkflowConfig.LLM_TIMEOUT
            )
            
            response = llm_result.content
            final_score = self._parse_json_safe(response)
            
            print(f"📈 Final Score: {final_score.get('overall_score', 0)}/100")
            print(f"🎯 Decision: {final_score.get('final_decision', 'N/A')}\n")
            
            # Store final score
            await result_collector.store("final_score", final_score)
            
            # Forward to output agent
            await self.publish_message(
                ContentMessage(
                    content=response,
                    metadata={"stage": "scoring", "final_decision": final_score.get("final_decision")},
                    stage="scoring"
                ),
                topic_id=TopicId(WorkflowConfig.TOPIC_OUTPUT, source="default")
            )
            
        except asyncio.TimeoutError:
            error_msg = "Scorer agent timeout"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
        except Exception as e:
            error_msg = f"Scorer agent error: {str(e)}"
            print(f"❌ {error_msg}")
            await result_collector.store("error", error_msg)
    
    @staticmethod
    def _parse_json_safe(text: str) -> Dict[str, Any]:
        """Safely parse JSON"""
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            return {"error": f"Failed to parse JSON: {str(e)}", "raw_text": text[:500]}


# ============================================================================
# Agent 5: Output Agent (Unchanged)
# ============================================================================

@type_subscription(topic_type=WorkflowConfig.TOPIC_OUTPUT)
class OutputAgent(RoutedAgent):
    """Final output agent - terminates workflow"""
    
    def __init__(self):
        super().__init__("Output Agent")
    
    @message_handler
    async def handle_final_score(self, message: ContentMessage, ctx: MessageContext) -> None:
        """Receive final results and end workflow"""
        print(f"\n{'='*80}\n✅ OUTPUT AGENT - Workflow Complete\n{'='*80}")
        
        final_score = await result_collector.get("final_score", {})
        
        print(f"📊 Overall Score: {final_score.get('overall_score', 0)}/100")
        print(f"🎯 Decision: {final_score.get('final_decision', 'N/A')}")
        print(f"📄 Publication Status: {final_score.get('publication_readiness', 'N/A')}")
        print(f"{'='*80}\n")


# ============================================================================
# Main Workflow Execution
# ============================================================================

async def run_content_workflow(user_request: str) -> WorkflowResult:
    """
    Execute the complete content generation workflow with publication-ready standards
    
    Args:
        user_request: User's content generation request
    
    Returns:
        WorkflowResult with all agent outputs and final scores
    """
    start_time = asyncio.get_event_loop().time()
    
    # Clear previous results
    await result_collector.clear()
    
    print(f"\n{'='*80}")
    print(f"🚀 PUBLICATION-READY CONTENT WORKFLOW")
    print(f"{'='*80}")
    print(f"Request: {user_request[:100]}...")
    print(f"Thresholds: SEO ≥ {WorkflowConfig.SEO_PASS_THRESHOLD}, Overall ≥ {WorkflowConfig.OVERALL_PASS_THRESHOLD}")
    print(f"{'='*80}\n")
    
    # Validate API key
    if not WorkflowConfig.get_openai_api_key():
        error_msg = "OPENAI_API_KEY not found in environment variables"
        print(f"❌ {error_msg}")
        return WorkflowResult(success=False, error=error_msg)
    
    # Initialize model client
    model_client = OpenAIChatCompletionClient(
        model=WorkflowConfig.OPENAI_MODEL,
        api_key=WorkflowConfig.get_openai_api_key(),
    )
    
    # Create runtime
    runtime = SingleThreadedAgentRuntime()
    
    try:
        # Register all agents with enhanced configuration
        research_topic = WorkflowConfig.TOPIC_RESEARCH
        await ResearchAgent.register(
            runtime,
            type=research_topic,
            factory=lambda: ResearchAgent(
                model_client,
                serp_api_key=WorkflowConfig.get_serp_api_key()
            )
        )
        
        writer_topic = WorkflowConfig.TOPIC_WRITER
        await ContentWriterAgent.register(
            runtime,
            type=writer_topic,
            factory=lambda: ContentWriterAgent(model_client)
        )
        
        seo_topic = WorkflowConfig.TOPIC_SEO
        await SEOAgent.register(
            runtime,
            type=seo_topic,
            factory=lambda: SEOAgent(model_client)
        )
        
        scorer_topic = WorkflowConfig.TOPIC_SCORER
        await ScorerAgent.register(
            runtime,
            type=scorer_topic,
            factory=lambda: ScorerAgent(model_client)
        )
        
        output_topic = WorkflowConfig.TOPIC_OUTPUT
        await OutputAgent.register(
            runtime,
            type=output_topic,
            factory=lambda: OutputAgent()
        )
        
        # Start runtime
        runtime.start()
        
        # Trigger workflow
        await runtime.send_message(
            ContentMessage(content=user_request),
            TopicId(research_topic, source="user")
        )
        
        # Wait for workflow completion with timeout
        await asyncio.wait_for(
            runtime.stop_when_idle(),
            timeout=WorkflowConfig.WORKFLOW_TIMEOUT
        )
        
        # Collect results
        results = await result_collector.get_all()
        execution_time = asyncio.get_event_loop().time() - start_time
        
        # Check for errors
        if "error" in results:
            return WorkflowResult(
                success=False,
                error=results.get("error"),
                execution_time=execution_time
            )
        
        # Return successful result
        return WorkflowResult(
            success=True,
            research=results.get("research"),
            content=results.get("content"),
            seo_analysis=results.get("seo_analysis"),
            final_score=results.get("final_score"),
            execution_time=execution_time
        )
        
    except asyncio.TimeoutError:
        error_msg = f"Workflow timeout after {WorkflowConfig.WORKFLOW_TIMEOUT}s"
        print(f"❌ {error_msg}")
        return WorkflowResult(
            success=False,
            error=error_msg,
            execution_time=asyncio.get_event_loop().time() - start_time
        )
    except Exception as e:
        error_msg = f"Workflow error: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return WorkflowResult(
            success=False,
            error=error_msg,
            execution_time=asyncio.get_event_loop().time() - start_time
        )
    finally:
        try:
            await runtime.stop()
        except RuntimeError:
            # Runtime might already be stopped
            pass


# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """Interactive CLI for testing the workflow"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  PUBLICATION-READY CONTENT GENERATION SYSTEM                 ║
    ║  ------------------------------------------------------------ ║
    ║  Enhanced with:                                               ║
    ║  • SERP API Integration (optional)                           ║
    ║  • SEO Threshold: 80/100 (was 75)                           ║
    ║  • Overall Threshold: 85/100 (was 80)                        ║
    ║  • Publication-Ready Prompts                                  ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    if not WorkflowConfig.get_openai_api_key():
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    if not WorkflowConfig.get_serp_api_key():
        print("⚠️  Warning: SERP_API_KEY not set (optional)")
        print("For better results, get free key at: https://serpapi.com")
        print("Set with: export SERP_API_KEY='your-key-here'\n")
    
    # Example request
    example_request = """Generate a 1500-word SEO-optimized blog post about "AI Marketing Automation Tools for Small Businesses in 2024"

REQUIREMENTS:
- Target Audience: Small business owners, 30-50 years old, 5-20 employees
- Primary Keywords: AI marketing automation, small business marketing tools
- Word Count: 1500 words (STRICT)
- Tone: Professional yet approachable
- Structure: 5 main H2 sections, each with 2-3 H3 subsections
- Include: Specific tool examples, pricing, ROI data, implementation steps
- SEO Target: Score ≥ 80
- Overall Target: Score ≥ 85"""
    
    print(f"Example request:\n{example_request}\n")
    print("=" * 80)
    
    user_input = input("\nEnter your request (or press Enter to use example): ").strip()
    request = user_input if user_input else example_request
    
    print("\n🚀 Starting workflow...\n")
    
    result = await run_content_workflow(request)
    
    print("\n" + "=" * 80)
    print("📊 WORKFLOW RESULTS")
    print("=" * 80)
    print(f"Success: {result.success}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    
    if result.success:
        print(f"\n✅ Content Generation Successful!")
        
        if result.final_score:
            print(f"\n🎯 Final Scores:")
            print(f"   Overall: {result.final_score.get('overall_score', 0)}/100")
            print(f"   Decision: {result.final_score.get('final_decision', 'N/A')}")
            print(f"   Status: {result.final_score.get('publication_readiness', 'N/A')}")
        
        if result.seo_analysis:
            print(f"\n📊 SEO Analysis:")
            print(f"   SEO Score: {result.seo_analysis.get('seo_score', 0)}/100")
            print(f"   Status: {result.seo_analysis.get('validation_status', 'N/A')}")
        
        if result.content:
            print(f"\n📝 Content:")
            print(f"   Title: {result.content.get('title', 'N/A')}")
            print(f"   Word Count: {result.content.get('word_count', 0)}")
    else:
        print(f"\n❌ Workflow Failed: {result.error}")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
>>>>>>> c48496b (Automated update)
    asyncio.run(main())