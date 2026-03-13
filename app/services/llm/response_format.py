

class LLMResponseFormatConfig:

    SUMMARY_EACH_PAGE = {
        "type": "json_schema",
        "json_schema": {
            "name": "document_page_analysis",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "page_number": {
                        "type": ["integer", "null"],
                        "description": "Page number of the document if visible, otherwise null"
                    },
                    "title": {
                        "type": "string",
                        "description": "Main title or heading of the page if any"
                    },
                    "text_content_summary": {
                        "type": "string",
                        "description": "Detailed summary of all written text content on the page"
                    },
                    "visual_elements": {
                        "type": "array",
                        "description": "List of visual elements found on the page such as images, charts, tables, or diagrams",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["image", "chart", "diagram", "table", "figure"],
                                    "description": "Type of visual element"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Explanation of what the visual element shows"
                                }
                            },
                            "required": ["type", "description"],
                            "additionalProperties": False
                        }
                    },
                    "key_points": {
                        "type": "array",
                        "description": "Important facts or insights extracted from the page",
                        "items": {
                            "type": "string"
                        }
                    },
                },
                "required": [
                    "page_number",
                    "title",
                    "text_content_summary",
                    "visual_elements",
                    "key_points",
                ],
                "additionalProperties": False
            }
        }
    }

    SUMMARY_ALL_PAGE = {
        "type": "json_schema",
        "json_schema": {
            "name": "document_combined_summary",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "document_title": {
                        "type": "string",
                        "description": "The inferred title of the entire document"
                    },
                    "document_overview": {
                        "type": "string",
                        "description": "High-level overview explaining what the document is about"
                    },
                    "main_topics": {
                        "type": "array",
                        "description": "Main topics or sections covered in the document",
                        "items": {
                            "type": "string"
                        }
                    },
                    "key_insights": {
                        "type": "array",
                        "description": "Important insights or findings extracted from across all pages",
                        "items": {
                            "type": "string"
                        }
                    },
                    "visual_elements_summary": {
                        "type": "string",
                        "description": "Summary of important visual elements such as charts, tables, diagrams, or figures found across the document"
                    },
                    "final_summary": {
                        "type": "string",
                        "description": "Comprehensive summary of the entire document combining all page information"
                    }
                },
                "required": [
                    "document_title",
                    "document_overview",
                    "main_topics",
                    "key_insights",
                    "visual_elements_summary",
                    "final_summary"
                ],
                "additionalProperties": False
            }
        }
    }

    QUIZ_GENERATION = {
        "type": "json_schema",
        "json_schema": {
            "name": "quiz_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard"]
                    },
                    "total_questions": {
                        "type": "integer"
                    },
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"},
                                "choices": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "answer": {"type": "string"},
                                "explanation": {"type": "string"}
                            },
                            "required": [
                                "question",
                                "choices",
                                "answer",
                                "explanation"
                            ]
                        }
                    }
                },
                "required": [
                    "difficulty",
                    "total_questions",
                    "questions"
                ]
            }
        }
    }
