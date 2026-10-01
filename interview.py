import os
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


load_dotenv()


async def main():

    # ==========================================
    # OpenAI API Key
    # ==========================================

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("OPENAI_API_KEY not found.")
        return


    # ==========================================
    # Model
    # ==========================================

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=api_key,
    )


    # ==========================================
    # AI Interviewer
    # ==========================================

    interviewer = AssistantAgent(

        name="AI_Interviewer",

        model_client=model_client,

        system_message="""
You are an AI SEO Content Interviewer.

Your job is to understand what content the user wants.

Ask exactly 3 questions.

Ask ONE question at a time.

Question 1:
What topic or business should the content be about?

Question 2:
Who is the target audience?

Question 3:
What type of content do you want?
For example:
- Blog
- Website article
- Product description
- LinkedIn post
- Social media content

Important rules:

- Ask only one question at a time.
- Wait for the user's answer.
- Do not ask all questions together.
- After receiving the third answer, summarize the requirements.
- Finally write exactly:

END OF INTERVIEW
"""
    )


    # ==========================================
    # Human User
    # ==========================================

    user = UserProxyAgent(
        name="Human_User"
    )


    # ==========================================
    # Termination
    # ==========================================

    termination = TextMentionTermination(
        "END OF INTERVIEW"
    )


    # ==========================================
    # Interview Team
    # ==========================================

    interview_team = RoundRobinGroupChat(

        participants=[
            interviewer,
            user,
        ],

        termination_condition=termination,

        max_turns=7,
    )


    # ==========================================
    # Start Interview
    # ==========================================

    print()
    print("=" * 70)
    print("AI SEO CONTENT INTERVIEWER")
    print("=" * 70)
    print()

    await Console(
        interview_team.run_stream(
            task="""
Start the SEO content interview.

Ask the user the first question.

Remember:
Ask only ONE question at a time.
"""
        )
    )


    # ==========================================
    # Close Model
    # ==========================================

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())