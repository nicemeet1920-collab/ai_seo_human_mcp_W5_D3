# 🤖 AI SEO Multi-Agent Content System

An AI-powered SEO content generation system built using **AutoGen, Streamlit, MCP, OpenAI, and Serper Web Search**.

The system uses multiple AI agents to research a topic, create SEO content, optimize it using MCP tools, get human approval, revise rejected content, and perform a final review.

---

## 🚀 Project Overview

This project demonstrates how **Human-in-the-Loop, AI Interviewing, Multi-Agent Collaboration, Web Search, and MCP tools** can work together in a practical SEO content generation workflow.

### Workflow

```text
User
  ↓
Streamlit UI
  ↓
AI Content Interview
  ↓
Serper Web Search
  ↓
Research Agent
  ↓
Content Writer
  ↓
SEO Optimizer + MCP
  ↓
Human Approval
  ↓
 ┌───────────────┐
 │               │
 APPROVE       REJECT
 │               │
 ↓               ↓
Final Reviewer  Human Feedback
 │               ↓
 ↓          SEO Revision + MCP
 ↓               │
 └───────←───────┘
  ↓
Final Content
```

---

## ✨ Features

- 🤖 Multi-Agent AI workflow
- 👤 Human-in-the-Loop
- 🎤 AI content interview
- 🔍 Real-time web research using Serper
- 🧠 AI Research Agent
- ✍️ AI Content Writer
- 📊 SEO Optimization Agent
- 🔧 MCP integration
- 🔑 Keyword analysis
- 📝 Word count analysis
- 📈 SEO score calculation
- ✅ Human approval
- ❌ Human rejection with feedback
- 🔄 Automatic content revision
- 👨‍💼 Final content reviewer
- 🌐 Streamlit web interface
- 📥 Download final content as Markdown/Text

---

## 🧩 Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| AutoGen | Multi-agent framework |
| OpenAI | LLM |
| Streamlit | Web UI |
| MCP | External tool integration |
| FastMCP | MCP server |
| Serper API | Web search |
| python-dotenv | Environment variables |

---

## 🤖 Agents

### 1. Research Agent

The Research Agent receives web search results and creates an SEO research brief.

It identifies:

- Search intent
- Primary keyword
- Secondary keywords
- Long-tail keywords
- Target audience pain points
- Current trends
- Important facts
- Content angles

---

### 2. Content Writer

The Content Writer uses the research output to generate the requested content.

It focuses on:

- Clear structure
- SEO-friendly headings
- Readability
- Natural keyword usage
- Practical examples
- Human-friendly content

---

### 3. SEO Optimizer

The SEO Optimizer improves the generated content.

It checks:

- Keyword usage
- Word count
- SEO score
- SEO title
- Meta title
- Meta description
- URL slug
- Headings
- FAQ
- Search intent
- Readability

The SEO Agent uses MCP tools during optimization.

---

### 4. Final Reviewer

The Final Reviewer checks the approved content for:

- Grammar
- Clarity
- Structure
- SEO
- Search intent
- Usefulness
- Readability
- Keyword stuffing

It then produces the final polished content.

---

# 🔧 MCP Integration

This project uses **Model Context Protocol (MCP)** to provide external SEO tools to the AI agent.

### MCP Server

The project contains:

```text
mcp_server.py
```

The MCP server exposes three tools:

### `check_keyword`

Checks how many times a keyword appears in the content.

### `count
