import os
import sys
import asyncio

import streamlit as st
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from autogen_ext.tools.mcp import (
    StdioServerParams,
    mcp_server_tools,
)

from web_search import web_search


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI SEO Multi-Agent System",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# TITLE
# ============================================================

st.title("🤖 AI SEO Multi-Agent Content System")

st.write(
    "AI Interview → Web Research → Writer → SEO + MCP → "
    "Human Approval → Final Reviewer"
)


# ============================================================
# SESSION STATE
# ============================================================

if "step" not in st.session_state:
    st.session_state.step = 1

if "topic" not in st.session_state:
    st.session_state.topic = ""

if "audience" not in st.session_state:
    st.session_state.audience = ""

if "content_type" not in st.session_state:
    st.session_state.content_type = "Blog"

if "primary_keyword" not in st.session_state:
    st.session_state.primary_keyword = ""

if "web_results" not in st.session_state:
    st.session_state.web_results = ""

if "research" not in st.session_state:
    st.session_state.research = ""

if "draft" not in st.session_state:
    st.session_state.draft = ""

if "seo_content" not in st.session_state:
    st.session_state.seo_content = ""

if "final_content" not in st.session_state:
    st.session_state.final_content = ""

if "feedback" not in st.session_state:
    st.session_state.feedback = ""


# ============================================================
# SEO METRICS HELPER
# ============================================================

def calculate_seo_metrics(keyword, content):

    if not keyword.strip():
        return 0, len(content.split()), 50

    keyword_count = content.lower().count(
        keyword.lower()
    )

    word_count = len(
        content.split()
    )

    score = 50

    if keyword_count >= 1:
        score += 15

    if keyword_count >= 3:
        score += 10

    if word_count >= 300:
        score += 10

    if word_count >= 600:
        score += 10

    if word_count > 1500:
        score -= 10

    score = max(
        0,
        min(score, 100)
    )

    return (
        keyword_count,
        word_count,
        score
    )


# ============================================================
# AI PIPELINE
# ============================================================

async def run_ai_pipeline(
    topic,
    audience,
    content_type,
    feedback=""
):

    # ========================================================
    # OPENAI API KEY
    # ========================================================

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:

        return {
            "error":
            "OPENAI_API_KEY not found in .env file."
        }


    # ========================================================
    # OPENAI MODEL
    # ========================================================

    model_client = OpenAIChatCompletionClient(

        model="gpt-4o-mini",

        api_key=api_key,
    )


    try:

        # ====================================================
        # MCP SERVER
        # ====================================================

        server = StdioServerParams(

            command=sys.executable,

            args=[
                "mcp_server.py"
            ],

            read_timeout_seconds=30,
        )


        tools = await mcp_server_tools(
            server
        )


        # ====================================================
        # WEB SEARCH
        # ====================================================

        search_query = (
            f"{topic} latest trends 2026"
        )


        web_results = web_search(

            search_query,

            num_results=5,
        )


        # ====================================================
        # RESEARCH AGENT
        # ====================================================

        research_agent = AssistantAgent(

            name="Research_Agent",

            model_client=model_client,

            system_message="""
You are an SEO Research Agent.

You receive real web search results.

Use those results to create a research brief.

Include:

1. Search intent
2. Primary keyword
3. Secondary keywords
4. Long-tail keywords
5. Target audience pain points
6. Current trends
7. Important facts
8. Content angles

Important rules:

- Use the provided web results as research input.
- Do not invent facts.
- Do not write the final article.
- Clearly separate useful information from unsupported claims.
- Do not treat search snippets as verified facts.
"""
        )


        research_result = await research_agent.run(

            task=f"""
Topic:
{topic}

Target Audience:
{audience}

Content Type:
{content_type}


REAL WEB SEARCH RESULTS:

{web_results}


Based on the web search results,
create a detailed SEO research brief.
"""
        )


        research = (
            research_result
            .messages[-1]
            .content
        )


        # ====================================================
        # CONTENT WRITER
        # ====================================================

        writer_agent = AssistantAgent(

            name="Content_Writer",

            model_client=model_client,

            system_message="""
You are a professional SEO Content Writer.

Use the SEO research brief and web research.

Create the requested content.

Important rules:

- Use current information from the research.
- Do not use outdated years unless supported by the research.
- Do not invent statistics.
- Do not invent sources.
- Use natural keyword placement.
- Write for humans first.
- Use clear headings.
- Include practical examples.
- Keep the content useful and readable.
- Do not copy search snippets.
- Do not mention that you are an AI.

Return the complete article.
"""
        )


        writer_result = await writer_agent.run(

            task=f"""
Topic:
{topic}

Target Audience:
{audience}

Content Type:
{content_type}


SEO RESEARCH:

{research}


REAL WEB SEARCH RESULTS:

{web_results}


Create the complete content.

Use the research information
and current web findings.
"""
        )


        draft = (
            writer_result
            .messages[-1]
            .content
        )


        # ====================================================
        # SEO OPTIMIZER + MCP
        # ====================================================

        seo_agent = AssistantAgent(

            name="SEO_Optimizer",

            model_client=model_client,

            tools=tools,

            reflect_on_tool_use=True,

            system_message="""
You are an SEO Optimization Agent.

You have access to these MCP tools:

1. check_keyword
2. count_words
3. seo_score

Use the MCP tools before finalizing.

Analyze the content.

Then improve:

- SEO title
- Meta title
- Meta description
- URL slug
- Headings
- FAQ
- Keyword usage
- Readability
- Search intent

Important rules:

- Use MCP tools.
- Do not keyword stuff.
- Keep the content natural.
- Do not invent statistics.
- Do not invent search results.
- Do not use outdated information when current research is available.
- Return the complete optimized content.
"""
        )


        # ====================================================
        # FIRST SEO OPTIMIZATION
        # ====================================================

        if not feedback:

            seo_task = f"""
Topic:
{topic}

Target Audience:
{audience}

Content Type:
{content_type}


RESEARCH:

{research}


DRAFT:

{draft}


Optimize this content using the MCP tools.

Check:

- Keyword usage
- Word count
- SEO score

Then return the complete optimized content.
"""


        # ====================================================
        # HUMAN REJECTION / REVISION
        # ====================================================

        else:

            seo_task = f"""
CURRENT SEO CONTENT:

{st.session_state.seo_content}


HUMAN REVIEWER FEEDBACK:

{feedback}


Revise the content according to the
human reviewer's feedback.

Use the MCP tools again.

Check:

- Keyword usage
- Word count
- SEO score
- Readability
- Search intent

Return the complete revised content.
"""


        seo_result = await seo_agent.run(
            task=seo_task
        )


        seo_content = (
            seo_result
            .messages[-1]
            .content
        )


        return {

            "web_results":
                web_results,

            "research":
                research,

            "draft":
                draft,

            "seo_content":
                seo_content,
        }


    except Exception as e:

        return {
            "error": str(e)
        }


    finally:

        try:

            await model_client.close()

        except Exception:

            pass


# ============================================================
# STEP 1
# CONTENT INTERVIEW
# ============================================================

if st.session_state.step == 1:

    st.header(
        "Step 1: AI Content Interview"
    )


    st.info(
        "Tell the system what type of SEO content you want."
    )


    # --------------------------------------------------------
    # TOPIC
    # --------------------------------------------------------

    st.session_state.topic = st.text_input(

        "1️⃣ What topic or business should "
        "the content be about?",

        value=st.session_state.topic,

        placeholder=(
            "Example: Latest AI Trends in 2026"
        ),
    )


    # --------------------------------------------------------
    # TARGET AUDIENCE
    # --------------------------------------------------------

    st.session_state.audience = st.text_input(

        "2️⃣ Who is the target audience?",

        value=st.session_state.audience,

        placeholder=(
            "Example: Small business owners"
        ),
    )


    # --------------------------------------------------------
    # CONTENT TYPE
    # --------------------------------------------------------

    content_types = [

        "Blog",

        "Website Article",

        "LinkedIn Post",

        "Social Media Post",

        "Product Description",
    ]


    current_content_type = (
        st.session_state.content_type
    )


    if current_content_type not in content_types:

        current_content_type = "Blog"


    st.session_state.content_type = (
        st.selectbox(

            "3️⃣ What type of content do you want?",

            content_types,

            index=content_types.index(
                current_content_type
            ),
        )
    )


    st.divider()


    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    if st.button(

        "🚀 Start Content Generation",

        use_container_width=True,
    ):

        if not st.session_state.topic.strip():

            st.error(
                "Please enter a topic."
            )

        elif not st.session_state.audience.strip():

            st.error(
                "Please enter the target audience."
            )

        else:

            st.session_state.primary_keyword = (
                st.session_state.topic
            )

            st.session_state.step = 2

            st.rerun()


# ============================================================
# STEP 2
# WEB RESEARCH + AGENTS
# ============================================================

elif st.session_state.step == 2:

    st.header(
        "Step 2: AI Multi-Agent Processing"
    )


    st.info(
        "🔍 Web Search → Research Agent → "
        "✍️ Writer → 📊 SEO + MCP"
    )


    st.write(
        f"**Topic:** "
        f"{st.session_state.topic}"
    )


    st.write(
        f"**Audience:** "
        f"{st.session_state.audience}"
    )


    st.write(
        f"**Content Type:** "
        f"{st.session_state.content_type}"
    )


    with st.spinner(
        "AI agents are working..."
    ):

        result = asyncio.run(

            run_ai_pipeline(

                st.session_state.topic,

                st.session_state.audience,

                st.session_state.content_type,
            )
        )


    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    if "error" in result:

        st.error(
            result["error"]
        )


        if st.button(
            "⬅️ Back"
        ):

            st.session_state.step = 1

            st.rerun()


        st.stop()


    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    st.session_state.web_results = (
        result["web_results"]
    )


    st.session_state.research = (
        result["research"]
    )


    st.session_state.draft = (
        result["draft"]
    )


    st.session_state.seo_content = (
        result["seo_content"]
    )


    st.session_state.step = 3

    st.rerun()


# ============================================================
# STEP 3
# HUMAN APPROVAL + SEO DASHBOARD
# ============================================================

elif st.session_state.step == 3:

    st.header(
        "Step 3: Human Approval"
    )


    # ========================================================
    # SEO DASHBOARD
    # ========================================================

    st.subheader(
        "📊 SEO Dashboard"
    )


    keyword = (
        st.session_state.primary_keyword
    )


    keyword_count, word_count, seo_score = (
        calculate_seo_metrics(

            keyword,

            st.session_state.seo_content,
        )
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(

            "🔑 Keyword Occurrences",

            keyword_count,
        )


    with col2:

        st.metric(

            "📝 Word Count",

            word_count,
        )


    with col3:

        st.metric(

            "📈 SEO Score",

            f"{seo_score}/100",
        )


    st.divider()


    # ========================================================
    # PRIMARY KEYWORD
    # ========================================================

    st.write(
        f"**Primary Keyword:** "
        f"`{keyword}`"
    )


    # ========================================================
    # SEO CONTENT
    # ========================================================

    st.subheader(
        "📄 SEO Optimized Content"
    )


    st.markdown(
        st.session_state.seo_content
    )


    st.divider()


    # ========================================================
    # DETAILS
    # ========================================================

    with st.expander(
        "🔍 View Web Research"
    ):

        st.text(
            st.session_state.web_results
        )


    with st.expander(
        "🧠 View Research Agent Output"
    ):

        st.markdown(
            st.session_state.research
        )


    with st.expander(
        "✍️ View Original Draft"
    ):

        st.markdown(
            st.session_state.draft
        )


    st.divider()


    # ========================================================
    # HUMAN APPROVAL
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        if st.button(

            "✅ APPROVE",

            use_container_width=True,
        ):

            st.session_state.step = 5

            st.rerun()


    with col2:

        if st.button(

            "❌ REJECT",

            use_container_width=True,
        ):

            st.session_state.step = 4

            st.rerun()


# ============================================================
# STEP 4
# HUMAN FEEDBACK + REVISION
# ============================================================

elif st.session_state.step == 4:

    st.header(
        "Step 4: Human Feedback"
    )


    st.warning(
        "Tell the SEO Agent what should be changed."
    )


    # ========================================================
    # CURRENT CONTENT
    # ========================================================

    st.subheader(
        "Current Content"
    )


    st.markdown(
        st.session_state.seo_content
    )


    st.divider()


    # ========================================================
    # FEEDBACK
    # ========================================================

    feedback = st.text_area(

        "Human Reviewer Feedback",

        value=st.session_state.feedback,

        placeholder=(
            "Example: Make the introduction shorter "
            "and add three practical examples."
        ),

        height=180,
    )


    # ========================================================
    # REVISE
    # ========================================================

    if st.button(

        "🔄 Revise Content",

        use_container_width=True,
    ):

        if not feedback.strip():

            st.error(
                "Please enter feedback."
            )

        else:

            st.session_state.feedback = (
                feedback
            )


            with st.spinner(
                "SEO Agent is revising the content..."
            ):

                result = asyncio.run(

                    run_ai_pipeline(

                        st.session_state.topic,

                        st.session_state.audience,

                        st.session_state.content_type,

                        feedback,
                    )
                )


            if "error" in result:

                st.error(
                    result["error"]
                )

                st.stop()


            st.session_state.seo_content = (
                result["seo_content"]
            )


            st.session_state.step = 3

            st.rerun()


# ============================================================
# STEP 5
# FINAL REVIEW
# ============================================================

elif st.session_state.step == 5:

    st.header(
        "Step 5: Final Content Review"
    )


    with st.spinner(
        "Final Reviewer is checking the content..."
    ):


        async def final_review():

            api_key = os.getenv(
                "OPENAI_API_KEY"
            )


            model_client = (
                OpenAIChatCompletionClient(

                    model="gpt-4o-mini",

                    api_key=api_key,
                )
            )


            reviewer = AssistantAgent(

                name="Content_Reviewer",

                model_client=model_client,

                system_message="""
You are the final SEO Content Reviewer.

Review the approved content.

Check:

1. Grammar
2. Clarity
3. Structure
4. SEO
5. Search intent
6. Usefulness
7. Readability
8. Keyword stuffing

Important:

- Preserve the main meaning.
- Do not invent facts.
- Do not add unsupported statistics.
- Keep current information accurate.

Return the final polished content only.
"""
            )


            result = await reviewer.run(

                task=f"""
Topic:
{st.session_state.topic}

Target Audience:
{st.session_state.audience}

Content Type:
{st.session_state.content_type}


APPROVED CONTENT:

{st.session_state.seo_content}


Create the final polished content.
"""
            )


            output = (
                result
                .messages[-1]
                .content
            )


            await model_client.close()


            return output


        final_content = asyncio.run(
            final_review()
        )


        st.session_state.final_content = (
            final_content
        )


    st.session_state.step = 6

    st.rerun()


# ============================================================
# STEP 6
# FINAL OUTPUT
# ============================================================

elif st.session_state.step == 6:

    st.header(
        "🎉 Final Content"
    )


    st.success(
        "Content generation completed successfully."
    )


    # ========================================================
    # FINAL CONTENT
    # ========================================================

    st.markdown(
        st.session_state.final_content
    )


    st.divider()


    # ========================================================
    # PROJECT SUMMARY
    # ========================================================

    st.subheader(
        "📋 Project Summary"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.write(
            "**Topic**"
        )

        st.write(
            st.session_state.topic
        )


    with col2:

        st.write(
            "**Target Audience**"
        )

        st.write(
            st.session_state.audience
        )


    with col3:

        st.write(
            "**Content Type**"
        )

        st.write(
            st.session_state.content_type
        )


    st.divider()


    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.subheader(
        "📥 Download"
    )


    st.download_button(

        label="📄 Download Markdown",

        data=st.session_state.final_content,

        file_name="final_seo_content.md",

        mime="text/markdown",

        use_container_width=True,
    )


    st.download_button(

        label="📝 Download Text",

        data=st.session_state.final_content,

        file_name="final_seo_content.txt",

        mime="text/plain",

        use_container_width=True,
    )


    st.divider()


    # ========================================================
    # NEW CONTENT
    # ========================================================

    if st.button(

        "🔄 Create New Content",

        use_container_width=True,
    ):

        st.session_state.clear()

        st.rerun()