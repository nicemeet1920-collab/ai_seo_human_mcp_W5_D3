from mcp.server.fastmcp import FastMCP


# Create MCP server
mcp = FastMCP("SEO Tools")


@mcp.tool()
def check_keyword(keyword: str, content: str) -> str:
    """
    Check how many times a keyword appears in the content.
    """

    keyword_count = content.lower().count(keyword.lower())

    if 1 <= keyword_count <= 8:
        recommendation = "Good keyword usage"
    elif keyword_count == 0:
        recommendation = "Keyword not found"
    else:
        recommendation = "Review keyword usage. It may be too frequent."

    return (
        f"Keyword: {keyword}\n"
        f"Occurrences: {keyword_count}\n"
        f"Recommendation: {recommendation}"
    )


@mcp.tool()
def count_words(content: str) -> str:
    """
    Count the number of words in the content.
    """

    word_count = len(content.split())

    return f"Word count: {word_count}"


@mcp.tool()
def seo_score(keyword: str, content: str) -> str:
    """
    Calculate a simple demo SEO score.
    """

    score = 50

    keyword_count = content.lower().count(keyword.lower())
    word_count = len(content.split())

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

    score = max(0, min(score, 100))

    return (
        f"SEO Score: {score}/100\n"
        f"Keyword occurrences: {keyword_count}\n"
        f"Word count: {word_count}"
    )


if __name__ == "__main__":
    mcp.run()