# 🎓 SRM Chatbot - RAG-based Campus Assistant

Production-ready chatbot with authentication, chat logging, and session management.

---

## 🚀 Features

- ✅ **RAG-based QA** - FAISS + Ollama LLM
- ✅ **SMS OTP Authentication** - Email + Phone verification
- ✅ **Session Management** - Auto-logout on window close
- ✅ **Chat Logging** - All conversations stored in Supabase
- ✅ **User Tracking** - User data persisted in database
- ✅ **Clean UI** - Single-page chat interface

---

## 📦 Tech Stack

**Backend:**
- FastAPI (Python 3.12)
- FAISS (Vector search)
- Sentence Transformers (Embeddings)
- Ollama Gemma 3:1b (LLM)
- Supabase (Database)

**Frontend:**
- HTML/CSS/JavaScript
- sessionStorage (Auto-logout)

---

## 🗄️ Database Schema

### Users Table
```sql
users (
    id UUID PRIMARY KEY,
    email TEXT,
    phone TEXT UNIQUE,
    created_at TIMESTAMP
)
```

### Chat Logs Table
```sql
chat_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    query TEXT,
    answer TEXT,
    created_at TIMESTAMP
)
```

---

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone 
cd srm-chatbot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` file:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 3. Setup Supabase

Run SQL from STEP 1 in Supabase SQL Editor to create tables.

### 4. Build Vector Store

```bash
python scripts/build_vectorstore.py
```

### 5. Run Backend

```bash
python -m uvicorn backend.main:app --reload --port 8001
```

### 6. Run Frontend

```bash
cd frontend
python -m http.server 5501
```

Open: http://127.0.0.1:5501/kivy_chatbot.html

---

## 🔐 Authentication Flow

1. User enters **email**
2. User enters **phone number** (10 digits)
3. OTP sent to phone (printed in console for demo)
4. User enters **OTP**
5. Verified → User stored in Supabase → Session created
6. Chat logged to `chat_logs` table

**Session Behavior:**
- ✅ Refresh page → User stays logged in
- ✅ Close window → User logged out (sessionStorage cleared)
- ✅ Reopen → Login required

---

## 📊 Database Queries

### View all users
```sql
SELECT * FROM users ORDER BY created_at DESC;
```

### View chat logs for a user
```sql
SELECT cl.*, u.email, u.phone 
FROM chat_logs cl
JOIN users u ON cl.user_id = u.id
WHERE u.phone = '1234567890'
ORDER BY cl.created_at DESC;
```

### Chat activity stats
```sql
SELECT 
    u.email,
    COUNT(cl.id) as total_chats,
    MAX(cl.created_at) as last_chat
FROM users u
LEFT JOIN chat_logs cl ON u.id = cl.user_id
GROUP BY u.email
ORDER BY total_chats DESC;
```

---

## 🧪 Testing

**Test Authentication:**
```bash
curl -X POST http://127.0.0.1:8001/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@srm.edu", "phone": "9876543210"}'

curl -X POST http://127.0.0.1:8001/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone": "9876543210", "otp": "123456"}'
```

**Test Chat (with user_id):**
```bash
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Where is library?", "user_id": "uuid-here"}'
```

---

## 📁 Project Structure
srm-chatbot/
├── backend/
│   ├── api/
│   │   ├── auth.py          # OTP authentication + Supabase
│   │   └── routes.py        # Chat endpoint + logging
│   ├── core/
│   │   ├── rag_engine.py    # RAG pipeline
│   │   ├── prompts.py       # ChatGPT-style prompts
│   │   ├── vector_store.py  # FAISS operations
│   │   └── embeddings.py    # Sentence Transformers
│   └── main.py              # FastAPI app
├── frontend/
│   └── kivy_chatbot.html    # Single-page chat UI
├── data/
│   ├── processed/
│   │   └── merged_chunks.json
│   └── vectorstore/
│       └── faiss.index
├── scripts/
│   ├── build_vectorstore.py
│   └── integrate_new_dataset.py
├── .env
├── requirements.txt
└── README.md

---

## 🚨 Troubleshooting

**Backend not starting:**
```bash
# Check if port 8001 is free
lsof -ti:8001 | xargs kill -9
```

**Supabase connection failed:**
```bash
# Verify .env variables
cat .env
# Check Supabase project is active
```

**OTP not received:**
```bash
# Check terminal output for printed OTP (demo mode)
# In production, integrate Twilio for real SMS
```

**Auto-logout not working:**
```bash
# Clear browser cache and sessionStorage
sessionStorage.clear()
```

---

## 📈 Production Deployment

1. **Enable real SMS:**
   - Integrate Twilio in `auth.py`
   - Remove OTP printing

2. **Security:**
   - Add rate limiting
   - Enable CORS properly
   - Use HTTPS
   - Secure Supabase RLS policies

3. **Monitoring:**
   - Add logging (winston/loguru)
   - Setup error tracking (Sentry)
   - Monitor DB queries

---

## 📄 License

MIT License

---

## 👥 Contributors

Your Team Name

---

## 🙏 Acknowledgments

- SRM Institute of Science and Technology
- Anthropic Claude for development assistance

---

**Built with ❤️ for SRM Students**