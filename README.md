# DocPilot-AI

DocPilot-AI is a document question-answering application. Users upload readable PDFs, the backend extracts and chunks the text, creates local embeddings, searches the relevant document context with FAISS, and uses Gemini to generate grounded answers with source citations.

## Features

- JWT authentication with bcrypt password hashing
- User-owned PDF upload and document management
- PDF page-aware text extraction and chunk embeddings
- User/document-scoped FAISS retrieval
- Gemini answers grounded in retrieved document context
- Source snippets with page numbers
- Suggested questions in the chat UI
- Persistent chat sessions and messages
- Delete chat and document actions
- Upload validation for size, page count, PDF type, encrypted files, and unreadable PDFs

## Project Structure

```text
backend/
  app/
    core/          Configuration and security
    database/      SQLAlchemy setup
    models/        User, document, and chat models
    routers/       Auth, document, and chat APIs
    services/      PDF, embedding, vector search, and Gemini services
  requirements.txt
frontend/
  src/
    components/   Protected route, sidebar, history, citations, suggestions
    pages/        Login, signup, dashboard, and chat pages
    services/     Axios API client
```

## Requirements

- Python 3.11+ recommended
- Node.js 18+
- A Gemini API key
- A local SQLite database by default, or another SQLAlchemy-compatible database URL

## Backend Setup

From the repository root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` using `backend/.env.example`:

```env
DATABASE_URL=sqlite:///./docpilot.db
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=your-gemini-api-key
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Swagger documentation is available at `http://127.0.0.1:8000/docs`.

## Frontend Setup

Open a second terminal from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

The Vite development server normally runs at `http://localhost:5173`.

The frontend currently uses `http://127.0.0.1:8000` as its API URL in `src/services/api.js`. For deployment, replace this with an environment variable such as `VITE_API_URL` and update backend CORS to allow the deployed frontend origin.

## How To Use

1. Start the backend and frontend.
2. Create an account or log in.
3. Upload a text-readable PDF from the dashboard.
4. Open the chat page and select the uploaded document.
5. Ask a question or choose a suggested question.
6. Review the answer and source snippets below it.
7. Use the sidebar to create, switch, or delete persistent conversations.

Scanned or image-only PDFs currently require OCR and will be rejected with a readable-text error.

## API Overview

| Method | Endpoint                   | Purpose                                  |
| ------ | -------------------------- | ---------------------------------------- |
| POST   | `/signup`                  | Create an account                        |
| POST   | `/login`                   | Get a JWT access token                   |
| GET    | `/me`                      | Get the current user                     |
| GET    | `/documents/`              | List the current user's documents        |
| POST   | `/documents/upload`        | Upload and index a PDF                   |
| DELETE | `/documents/{document_id}` | Delete an owned document and its vectors |
| GET    | `/chat/sessions`           | List persistent chats                    |
| POST   | `/chat/sessions`           | Create a chat session                    |
| DELETE | `/chat/sessions/{chat_id}` | Delete an owned chat                     |
| POST   | `/chat/ask`                | Retrieve context and generate an answer  |

Protected endpoints require:

```text
Authorization: Bearer <access-token>
```

## GitHub Safety Checklist

Before pushing:

- Never commit `.env`, API keys, passwords, JWT secrets, `venv`, `uploads`, or `vector_store`.
- Keep `.env.example` limited to placeholder values.
- Generate a new `SECRET_KEY` for every deployment.
- Review `git diff` and `git status` before committing.
- Rotate a Gemini key immediately if it was ever committed or shared publicly.

Example Git workflow:

```powershell
git status
git diff
git add README.md .gitignore backend frontend
git commit -m "Document DocPilot AI setup and features"
git push origin master
```

## Deployment Notes

The current FAISS index, uploaded PDFs, and local SQLite database are stored on the server filesystem. Many free hosting services use ephemeral disks, so these files can disappear after a restart or redeploy. For production deployment, use persistent object storage for PDFs, a persistent database, and a hosted or persistent vector store.

Do not enable broad CORS in production. Set `allow_origins` to the exact frontend URL. Keep Gemini and database credentials in the hosting provider's environment-variable settings.

## Security Status

Implemented protections include JWT authentication, bcrypt password hashing, ownership checks for documents and chats, upload size/page/type validation, encrypted PDF rejection, and rate limiting on `/chat/ask`. This is suitable for local development and a controlled demo; production deployment still needs persistent storage, HTTPS, stronger operational logging, and a migration strategy for schema changes.
