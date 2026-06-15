# Bupa Care Navigator AI Agent Backend

An asynchronous Socket.IO backend service powered by the Gemini 2.5 Flash model. It serves as **NAVI**, a conversational care assistant designed for the **Care Navigator (CN)** platform. The assistant facilitates healthcare management tasks for care navigators by leveraging over 50 built-in tool integrations (function calls) to query and update member profiles, schedule calls, log metrics, assign pathways, manage tasks, and raise support tickets.

---

## 🚀 Key Features

* **Real-time Communication:** Built on Socket.IO (ASGI) for bidirectional, low-latency, and event-driven communication.
* **Intelligent Agent (NAVI):** Driven by `gemini-2.5-flash` using the Google GenAI SDK. Orchestrates multi-turn conversations and multi-step tool/function invocation.
* **Rich Tool Integration:** Supports 55+ function-calling tools ranging from program assignment and metric entry to calendar breaks and task transfers.
* **Encrypted API Integration:** Secure, AES-CBC encrypted communications with the backend provider endpoints via a custom encryption layer.
* **Container Ready:** Includes a production-ready `Dockerfile` with SSL/TLS support for secure WebSocket communication (`WSS`).

---

## 📁 Repository Structure

```
├── main.py                  # Entrypoint: Starts Socket.IO ASGI server using Uvicorn
├── llm_client.py            # Gemini client wrappers, Chat Session manager, retry logic
├── system_prompt.py         # Dynamic system prompt configuration for NAVI's persona
├── tool_config.py           # Declarations/schemas of all tools for the Gemini API
├── tool_funcs.py            # Implementations of the tool handlers
├── constants.py             # Caching of static lookups and dynamic member contexts
├── enc_dec.py               # AES-CBC encryption/decryption utilities for API requests
├── requirements.txt         # Python package dependencies
├── Dockerfile               # Docker build instructions with SSL settings
├── .dockerignore            # Docker ignore file
├── .env                     # Local environment variables configuration (ignored by git)
├── certificate.pem          # SSL certificate for secure server runs
└── private-key.pem          # SSL private key for secure server runs
```

---

## 🛠️ Technology Stack

* **Language:** Python 3.9+
* **LLM Engine:** Google GenAI SDK (`google-genai`) & `gemini-2.5-flash`
* **Server Framework:** `python-socketio` (ASGI mode) & `uvicorn`
* **Security & Crypto:** `pycryptodome` (for AES-CBC encryption/decryption)
* **Date Utilities:** `python-dateutil`
* **HTTP Client:** `requests`

---

## ⚙️ Environment Configuration

Create a `.env` file in the root of the project with the following keys:

```env
# Gemini API Settings
GEMINI_API_KEY=your_gemini_api_key_here

# Backend API Settings
BASE_URL=https://your-api-endpoint.com/carenavigator
AES_ENCRYPTION_KEY=your_32_byte_hex_aes_key
AES_ENCRYPTION_IV=your_16_byte_hex_aes_iv
```

*Note: `AES_ENCRYPTION_KEY` and `AES_ENCRYPTION_IV` should be hex-encoded strings.*

---

## 🔌 Socket.IO Event API

The server listens on host `0.0.0.0` and port `5000` (local) or `443` (production SSL).

### 1. Connection Events
* **`connect`**: Automatically triggered when a client establishes a connection. Returns a default welcome message from NAVI.
* **`disconnect`**: Cleans up the in-memory chat session and leaves any rooms associated with the Socket ID.

### 2. Client-Emitted Events

#### `join_session`
Registers the client into a specific session room, facilitating multiple clients/panels subscribing to the same chat room updates.
```json
{
  "sessionId": "session-uuid-or-id"
}
```

#### `ai_chat_success`
Sends a message to NAVI. This is the primary messaging endpoint.
```json
{
  "message": "Assign diabetes program to the member.",
  "userId": "authenticated-member-user-id",
  "accessToken": "bearer-token-for-authorized-requests",
  "sessionId": "session-uuid-or-id",
  "cnId": "care-navigator-id",
  "timestamp": "ISO-8601-timestamp"
}
```

#### `typing`
Broadcasting helper indicating that the user is currently typing.
```json
{
  "sessionId": "session-uuid-or-id",
  "username": "CareNavigatorName"
}
```

### 3. Server-Emitted Events

#### `welcome_message`
Sent on initial client connection.
```json
"Hello, I am your assistant. How can I help you?"
```

#### `ai_chat_response`
Sent when the AI assistant returns its response (including after executing any necessary tools).
```json
{
  "data": "I have successfully assigned the Diabetes Management program with the Insulin pathway to John Doe.",
  "sessionId": "session-uuid-or-id",
  "userId": "authenticated-member-user-id",
  "cnId": "care-navigator-id",
  "message": "Assign diabetes program to the member.",
  "timestamp": "ISO-8601-timestamp"
}
```

---

## 🧰 Agent Tools & Capabilities

The assistant parses requests and dynamically selects from over 50 tools categorized by scope:

### Scope 1: Member-Specific Tools
Used to interact with data belonging to the *currently active/logged-in member*:
* **Notes:** `add_note`, `member_notes_history`
* **Vitals & Metrics:** `add_health_metric`, `add_bmi`, `user_health_metric_data`
* **Programs & Pathways:** `assign_program`, `user_assigned_programs`, `stop_condition`, `restart_condition`, `remove_condition`, `change_pathway`
* **Support Tickets:** `raise_new_ticket`, `add_comment_on_ticket`, `available_tickets`
* **Member Journey:** `member_journey`, `member_call_history`
* **Scheduled Services:** `add_new_service`, `get_member_services`, `fetch_monthly_service_suggestions`
* **Health Locker Documents:** `add_member_record`, `health_locker_files`, `view_specific_record`, `remove_specific_record`
* **Home/Lab Requests:** `lab_request`, `home_care_request`, `homebase_vaccine_request`

### Scope 2: Care Navigator workload & Scheduling
Used by the Care Navigator to coordinate calls, tasks, and manage their calendar:
* **Work Schedule & Breaks:** `get_working_plans_and_breaks`, `add_break`, `delete_break`
* **Task Management:** `get_task_list`, `get_todays_tasks`, `dismiss_task`, `complete_task`, `transfer_task`
* **Calls Coordination:** `scheduled_calls_under_cn`, `get_all_care_navigator_scheduled_calls`, `get_calender_calls`, `member_upcoming_scheduled_call`, `cancel_or_reschedule_call`, `schedule_call_with_cn`
* **Member Management:** `userinfo_by_name_query`, `search_view_member_under_cn`
* **Analytics/Summaries:** `get_weekly_summary`, `get_all_members_stratification`, `get_all_members_pathway_breakup`, `get_new_report_members`, `get_requested_services`

---

## 🏃 Setup & Execution

### Local Development Setup

1. **Clone the repository and enter directory:**
   ```bash
   cd Bupa-agent-backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify environment config:**
   Ensure your `.env` contains the required keys.

5. **Run the server locally:**
   ```bash
   python main.py
   ```
   *The server runs locally by default at `http://localhost:5000`.*

---

## 🐳 Docker Deployment

The application is containerized to deploy securely over HTTPS/WSS (Port 443).

### Prerequisite Certificates
Ensure `certificate.pem` and `private-key.pem` are placed in the root directory. They are copied into the container to enable SSL in Uvicorn.

### Build and Run with Docker

1. **Build the image:**
   ```bash
   docker build -t bupa-agent-backend:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     -p 443:443 \
     --env-file .env \
     --name bupa-agent-backend-container \
     bupa-agent-backend:latest
   ```

3. **Check logs:**
   ```bash
   docker logs -f bupa-agent-backend-container
   ```
