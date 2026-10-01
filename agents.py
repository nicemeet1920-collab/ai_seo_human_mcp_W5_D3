import os
import sys
import asyncio

from dotenv import load_dotenv

from autogen_agentchat.agents import (
    AssistantAgent,
    UserProxyAgent,
)

from autogen_agentchat.conditions import TextMentionTermination

from autogen_agentchat.teams import RoundRobinGroupChat

from autogen_agentchat.ui import Console

from autogen_ext.models.openai import (
    OpenAIChatCompletionClient
)

from autogen_ext.tools.mcp import (
    StdioServerParams,
    mcp_server_tools,
)


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# Main
# ============================================================

async def main():

    # ========================================================
    # 1. OpenAI API Key
    # ========================================================

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("ERROR: OPENAI_API_KEY not found.")
        return

    print("OpenAI API key found.")


    # ========================================================
    # 2. OpenAI Model
    # ========================================================

    print("\nCreating OpenAI model client...")

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=api_key,
    )

    print("OpenAI model client created.")


    # ========================================================
    # 3. MCP Server
    # ========================================================

    print("\nConnecting to MCP server...")

    server = StdioServerParams(
        command=sys.executable,
        args=["mcp_server.py"],
        read_timeout_seconds=30,
    )


    # ========================================================
    # 4. Load MCP Tools
    # ========================================================

    tools = await mcp_server_tools(server)

    print("\nMCP tools connected:")

    for tool in tools:
        print(f"- {tool.name}")


    # ========================================================
    # 5. Research Agent
    # ========================================================

    research_agent = AssistantAgent(
        name="Research_Agent",

        model_client=model_client,

        system_message="""
You are an SEO Research Agent.

Research the topic given by the user.

Create a research brief containing:

1. Search intent
2. Primary keyword
3. Secondary keywords
4. Long-tail keywords
5. Target audience pain points
6. Three content angles
7. Important points the writer should cover

Do not write the final article.

Only provide the research brief.
""",
    )


    # ========================================================
    # 6. Content Writer
    # ========================================================

    writer_agent = AssistantAgent(
        name="Content_Writer",

        model_client=model_client,

        system_message="""
You are a professional SEO Content Writer.

Use the Research Agent's research brief.

Write a complete SEO-friendly blog post.

Include:

1. SEO title
2. Introduction
3. Proper headings
4. Useful explanations
5. Examples
6. Practical advice
7. Conclusion

Use simple language.

Do not keyword stuff.

Return the complete article draft.
""",
    )


    # ========================================================
    # 7. SEO Optimizer + MCP
    # ========================================================

    seo_agent = AssistantAgent(
        name="SEO_Optimizer",

        model_client=model_client,

        tools=tools,

        reflect_on_tool_use=True,

        system_message="""
You are an SEO Optimization Agent.

You have access to MCP SEO tools.

Available tools:

1. check_keyword
2. count_words
3. seo_score

Use the MCP tools to analyze the article.

Check:

- Primary keyword
- Keyword usage
- Word count
- SEO score

Then improve:

- SEO title
- Meta title
- Meta description
- URL slug
- Headings
- FAQ
- Keyword placement
- Readability

Do not keyword stuff.

At the end provide the improved SEO content.

Do NOT finish the project.
The human reviewer must approve the content first.
""",
    )


    # ========================================================
    # 8. Human Reviewer
    # ========================================================

    human_reviewer = UserProxyAgent(
        name="Human_Reviewer"
    )


    # ========================================================
    # 9. Reviewer Agent
    # ========================================================

    reviewer_agent = AssistantAgent(
        name="Content_Reviewer",

        model_client=model_client,

        system_message="""
You are the final SEO Content Reviewer.

Review the SEO content after human approval.

Check:

1. Grammar
2. Clarity
3. Structure
4. SEO
5. Search intent
6. Usefulness
7. Readability
8. Keyword stuffing

Make final improvements if necessary.

Return:

FINAL CONTENT

Then:

REVIEW SUMMARY

Finally write exactly:

END OF PROJECT
""",
    )


    # ========================================================
    # 10. Termination
    # ========================================================

    termination = TextMentionTermination(
        "END OF PROJECT"
    )


    # ========================================================
    # 11. Team
    # ========================================================

    team = RoundRobinGroupChat(
        participants=[
            research_agent,
            writer_agent,
            seo_agent,
            human_reviewer,
            reviewer_agent,
        ],

        termination_condition=termination,

        max_turns=10,
    )


    # ========================================================
    # 12. Task
    # ========================================================

    task = """
Create SEO-optimized content.

Topic:
AI tools for small businesses

Target Audience:
Small business owners

Content Type:
Blog post

Workflow:

1. Research Agent creates the research brief.

2. Content Writer creates the article.

3. SEO Optimizer uses MCP tools and improves the article.

4. Human Reviewer must review the SEO output.

5. Human Reviewer should type:

APPROVE

if the content is acceptable.

If changes are needed, type:

REJECT: followed by the requested changes.

6. After human approval, Content Reviewer creates the final version.

7. Content Reviewer must finish with:

END OF PROJECT
"""


    # ========================================================
    # 13. Start
    # ========================================================

    print("\n")
    print("=" * 70)
    print("AI SEO HUMAN-IN-THE-LOOP PROJECT")
    print("=" * 70)

    print("\nStarting agents...")

    await Console(
        team.run_stream(
            task=task
        )
    )


    # ========================================================
    # 14. Completed
    # ========================================================

    print("\n")
    print("=" * 70)
    print("PROJECT COMPLETED")
    print("=" * 70)


    # ========================================================
    # 15. Close Model
    # ========================================================

    await model_client.close()


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())