class LLMPromptTemplates:

    @staticmethod
    def summary_each_page(page):
        return f"""
You are an AI system that analyzes document images.

The image is a single page extracted from a PDF document.

Your task is to carefully read and analyze ALL visible information on the page including:
- titles
- paragraphs
- tables
- charts
- figures
- diagrams
- images
- headers / footers
- page numbers
- captions

Then produce a structured analysis.

IMPORTANT RULES:
- Do not invent information that does not exist.
- If text is unclear, mark it as "unclear".
- If images/figures exist, describe what they show.
- Capture the overall meaning of the page.
- If page don't have page number use the {page} for page number
"""

    @staticmethod
    def summary_all_page_prompt(title, content):
        return f"""
You are given structured summaries of multiple pages from the same document.

Your task is to combine them into a coherent understanding of the full document.

This is Title of the all document: {title}
This is Content of the all document: {content}

Focus on:
- main topic of the document
- major sections
- important insights
- key conclusions
- overall meaning

ANSWER WITH THAI LANGUAGES ONLY
"""

    @staticmethod
    def quiz_generation_prompt():
        return """
You are an AI that generates quiz questions from educational slide summaries.

Your task:
Create quiz questions based ONLY on the information provided in the input text.

The input text comes from slide content summaries. The questions should feel natural, as if they are testing a student who studied the material.

Requirements:
- Do NOT reference slides, pages, or the source text directly.
- Write questions naturally based on the concepts or information presented.
- The questions should test understanding of the material.

Difficulty guidelines:
- easy: simple factual recall from the content
- medium: understanding relationships, meanings, or concepts
- hard: reasoning or deeper understanding of the topic

Rules:
- Each question must have exactly 4 answer choices.
- Only one answer can be correct.
- Wrong choices must be plausible.
- Provide a short explanation for the correct answer.

Language requirement:
- ALL questions, answer choices, and explanations MUST be written in Thai.
- Use natural Thai language appropriate for students.

Important:
- Do not invent information that is not in the provided text.
- Do not mention the source text or slides in the questions.

"""