# LinkLian Inference

Worker-based inference service for:
- document/image summarization
- vector embedding storage in Qdrant
- quiz generation from summaries
- q&a chat response queue

## Requirements
- Python 3.11+
- Redis (for BullMQ)
- Qdrant (for vector storage)
- Azure Blob Storage (for summary and quiz outputs)

## Setup (Local)

### 1) Create virtual environment (recommended)

```bash
python -m venv venv
```

### 2) Activate

**Windows**

```bash
venv\Scripts\activate
```

**Mac / Linux**

```bash
source venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Required for all workers:
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_PASSWORD`
- `OPENROUTER_API_KEY`
- `AZURE_STORAGE_CONNECTION_STRING`

Required for Qdrant worker:
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION`

## Run Workers (Local)

Use the worker runner:

```bash
python worker.py --queue ai_summary_queue
python worker.py --queue qdrant_vector_store
python worker.py --queue quiz_generation_queue
python worker.py --queue qa_chat_queue
```

## Run with Docker Compose

```bash
docker compose up -d
```

## Queues and Payloads

### ai_summary_queue
Summarize files and upload results to Blob. This worker can enqueue Qdrant jobs.

### qdrant_vector_store
Input:
```json
{
	"post_content_id": 1,
	"file_name": "intro.pdf",
	"page": {
		"page_1": ["key1", "key2"],
		"page_2": ["key1", "key2", "key3"]
	}
}
```

### quiz_generation_queue
Input:
```json
{
	"post_content_id": "315",
	"summary_text": "...",
	"difficulty": "medium",
	"num_questions": 5,
	"file_name": "CSS336Lecture05CultureatGoogle.pdf"
}
```

### qa_chat_queue
Current behavior (temporary):
- Returns fixed message: `"มีอะไรให้ช่วยไหม"`

Input:
```json
{
	"session_id": "session-001",
	"question": "สรุปโพสต์นี้ให้หน่อย"
}
```

## Notes
- Summaries and quizzes are uploaded to Azure Blob Storage under `summary-post-announcement/`.
- Long-running jobs use extended BullMQ lock durations to avoid reprocessing.
