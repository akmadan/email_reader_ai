![banner.png](assets/banner.png)

# Building an AI-Powered Email Reader: A Developer's Guide

Imagine having your inbox read to you in natural-sounding audio with concise AI summaries. In this tutorial, we'll build a Chrome extension that transforms Gmail into an audio experience - perfect for busy professionals, commuters, or anyone who wants to consume their emails hands-free.

![extension.gif](assets/extension.gif)

## Table of Contents

1. Introduction
2. [Technology Stack](#tech-stack)
3. Backend Setup
    - [Prerequisites](#prerequisites)
    - [Setting Up the Project Structure](#project-structure)
    - [Environment Configuration](#env-config)
    - [Dependency Management](#dependencies)
    - Core Application Components
        - [Data Models](#data-models)
        - [Configuration Management](#config-management)
        - [AI Services Layer](#ai-services)
        - [Business Logic Controller](#business-logic)
        - [API Routes](#api-routes)
        - [Main Application](#main-app)
4. [Docker Deployment](#docker)
5. [Testing the API](#testing)
6. Frontend Development
    - [Project Structure](#project-structure-fe)
    - [Manifest Configuration](#manifest)
    - [Background Script](#background)
    - [Content Scripts](#content-scripts)
    - [Popup Interface](#popup)

## Technology Stack

Here's a clear breakdown of the technology stack:

| **Component** | **Technologies** |
| --- | --- |
| Frontend | HTML
CSS
JavaScript (Vanilla)
Manifest 3 (Chrome Extension) |
| Backend | FastAPI (Python)
Langchain
GPT 4o / Gemini Flash 2.0
Murf AI (Text to Speech)
Docker |

## Backend Setup

This section guides you through building a FastAPI server that processes emails using AI for summarisation and text-to-speech conversion. We'll cover everything from setting up the project structure to deploying with Docker.

### **Prerequisites**

- Python 3.8+
- OpenAI / Gemini API key
- Murf AI API key
- Docker (optional, for containerised deployment)

### **Step 1: Setting Up the Project Structure**

```
mkdir email_reader_ai
cd email_reader_ai
mkdir -p server/app/{routers,utils,services,models,controllers,config}
mkdir -p server/tests
```

This structure follows **clean architecture principles**:

- **`app/`**: Core application code
    - **`routers/`**: API endpoint definitions
    - **`models/`**: Data models and validation
    - **`services/`**: Business logic and external integrations
    - **`controllers/`**: Mediates between routes and services
    - **`config/`**: Application configuration
    - **`utils/`**: Helper functions
- **`tests/`**: Unit and integration tests
- Root files: Dockerfile, requirements.txt, etc.

**Why this structure?** It promotes separation of concerns, making the code easier to maintain, test, and scale.

### **Step 2: Environment Configuration**

We use **`.env`** file to manage configuration:

```
# API Keys
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
MURF_API_KEY=your_murf_api_key

# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=False
```

**Best Practices:**

- Never commit **`.env`** to version control
- Use **`.env.example`** to document required variables
- Load environment variables at application startup

### **Step 3: Dependency Management**

Our **`requirements.txt`** specifies all Python dependencies:

```
# FastAPI and server
fastapi==0.109.2
uvicorn==0.27.1

# AI components
langchain==0.1.9
langchain-google-genai==0.0.11
langchain-openai==0.0.8

# Other utilities
python-dotenv==1.0.1
pydantic==2.6.1
```

**Key Dependencies:**

- **`fastapi`**: Modern, fast web framework
- **`uvicorn`**: ASGI server for running FastAPI
- **`langchain`**: Framework for working with LLMs
- **`pydantic`**: Data validation and settings management

### **Step 4: Core Application Components**

### **4.1 Data Models (`app/models/email.py`)**

```
from pydantic import BaseModel, Field, validator

class EmailData(BaseModel):
    subject: str = Field(..., min_length=1)
    sender: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)

    @validator('*')
    def remove_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @validator('body')
    def validate_body_length(cls, v):
        if len(v) < 10:
            raise ValueError('Email body too short')
        return v
```

**Why Pydantic?**

- Automatic data validation
- Type hints for better IDE support
- Clean error messages for API consumers
- Serialisation/deserialisation

### **4.2 Configuration Management (`app/config/settings.py`)**

```
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str
    murf_api_key: str
    port: int = 8000

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

**Key Features:**

- Type-safe settings from environment variables
- **`@lru_cache`** prevents repeated file reads
- Centralized configuration management

### **4.3 AI Services Layer**

### **LangChain Service (`app/services/langchain_service.py`)**

```
from langchain_google_genai import ChatGoogleGenerativeAI
from enum import Enum

class ModelProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"

class LangchainService:
    def __init__(self, provider: ModelProvider = ModelProvider.GEMINI):
        self.llm = self._init_llm(provider)

    def _init_llm(self, provider):
        if provider == ModelProvider.GEMINI:
            return ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0.3
            )
        # ... other providers

    def summarize_email(self, email_data):
        prompt = self._create_prompt(email_data)
        return self.llm.invoke(prompt)
```

**Design Decisions:**

- Support multiple LLM providers via strategy pattern
- Configurable parameters (temperature, model version)
- Clean separation between prompt engineering and execution

### **MurfAI Service (`app/services/murfai_service.py`)**

```
from murf import Murf

class MurfAIService:
    def __init__(self):
        self.client = Murf(api_key=os.getenv('MURF_API_KEY'))

    async def text_to_speech(self, text):
        return await self.client.generate(
            text=text,
            voice_id="en-US-natalie",
            format="MP3"
        )
```

**Audio Generation:**

- Async support for non-blocking operations
- Configurable voice parameters
- Error handling for API failures

### **4.4 Business Logic Controller (`app/controllers/email_summarizer_controller.py`)**

```
class EmailSummarizerController:
    def __init__(self):
        self.ai_service = LangchainService()
        self.tts_service = MurfAIService()

    async def process_email(self, email_data):
        summary = self.ai_service.summarize_email(email_data)
        audio = await self.tts_service.text_to_speech(summary)
        return {
            "summary": summary,
            "audio": audio
        }
```

**Controller Responsibilities:**

- Orchestrates service interactions
- Handles business logic flow
- Manages error cases
- Transforms data between layers

### **4.5 API Routes (`app/routers/email_router.py`)**

```
router = APIRouter()
controller = EmailSummarizerController()

@router.post("/summarize")
async def summarize_email(email: EmailData):
    return await controller.process_email(email)
```

**API Design Principles:**

- Clear route definitions
- Minimal logic in routes
- Proper response models
- Comprehensive error handling

### **4.6 Main Application (`app/main.py`)**

```
app = FastAPI(title="Email Reader AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"]
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

**Production-Ready Features:**

- CORS configuration
- API documentation (automatic with FastAPI)
- Health check endpoint
- Structured logging

### **Step 5: Docker Deployment**

```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**Docker Benefits:**

- Consistent runtime environment
- Easy deployment to cloud platforms
- Reproducible builds
- Scalability

### **Step 6: Testing the API**

Start the server:

```
uvicorn app.main:app --reload
```

Sample API request:

```
curl -X POST "http://localhost:8000/api/v1/summarize" \
     -H "Content-Type: application/json" \
     -d '{
           "subject": "Weekly Team Update",
           "sender": "manager@company.com",
           "body": "Hello team, great progress this week..."
         }'
```

Expected response:

```
{
  "summary": "The email provides a weekly update...",
  "audio": "https://murf.ai/audio/12345.mp3"
}
```

## Frontend Development: Chrome Extension for Gmail Integration

Now that we have our backend API ready, let's build the user-facing part of our application - a Chrome extension that seamlessly integrates with Gmail. This section will guide you through creating an intuitive and responsive interface for accessing our email summarisation features.

### Project Structure

First, let's create the project structure:

```bash
mkdir email-reader-extension
cd email-reader-extension
mkdir -p assets background content popup

```

The structure will look like this:

```
email-reader-extension/
├── assets/
│   ├── icon16.png
│   ├── icon48.png
│   ├── icon128.png
│   └── logo.png
├── background/
│   └── background.js
├── content/
│   ├── content.js
│   └── content.css
├── popup/
│   ├── popup.html
│   ├── popup.js
│   └── popup.css
└── manifest.json

```

### Manifest Configuration

Create `manifest.json`:

```json
{
  "manifest_version": 3,
  "name": "AudioMail by Murf AI",
  "version": "1.0.0",
  "description": "Generate audio summaries of your emails with AI",
  "permissions": [
    "activeTab",
    "storage",
    "scripting",
    "tabs"
  ],
  "host_permissions": [
    "<http://localhost:8000/*>",
    "<https://mail.google.com/*>"
  ],
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "assets/icon16.png",
      "48": "assets/icon48.png",
      "128": "assets/icon128.png"
    }
  },
  "background": {
    "service_worker": "background/background.js",
    "type": "module"
  },
  "content_scripts": [
    {
      "matches": ["<https://mail.google.com/*>"],
      "js": ["content/content.js"],
      "css": ["content/content.css"],
      "run_at": "document_end"
    }
  ],
  "icons": {
    "16": "assets/icon16.png",
    "48": "assets/icon48.png",
    "128": "assets/icon128.png"
  }
}

```

### Background Script

Create `background/background.js`:

```jsx
// Background script for Email Reader AI extension
chrome.runtime.onInstalled.addListener(() => {
    console.log('Email Reader AI extension installed');
});

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'checkServerStatus') {
        // Check if the server is running
        fetch('<http://localhost:8000/health>')
            .then(response => response.json())
            .then(data => {
                sendResponse({ status: 'ok', data });
            })
            .catch(error => {
                sendResponse({ status: 'error', message: 'Server not available' });
            });
        return true; // Required for async sendResponse
    }
});

```

### Content Scripts

**Content JavaScript (`content/content.js`)**

```jsx
// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getEmailContent') {
        try {
            const emailData = extractEmailContent();
            console.log('Extracted email data:', emailData);
            sendResponse(emailData);
        } catch (error) {
            console.error('Error extracting email:', error);
            sendResponse({ error: error.message });
        }
    }
    return true;
});

// Function to extract email content from Gmail
function extractEmailContent() {
    console.log('Starting email extraction...');

    // Get the email subject
    const subject = document.querySelector('h2.hP')?.textContent ||
                   document.querySelector('div[data-thread-title]')?.textContent ||
                   '';

    // Get the sender
    const sender = document.querySelector('span.gD')?.getAttribute('email') ||
                  document.querySelector('span[email]')?.getAttribute('email') ||
                  '';

    // Get the email body
    const bodyElement = document.querySelector('div.a3s.aiL') ||
                       document.querySelector('div[role="main"] div[dir="ltr"]') ||
                       document.querySelector('div[role="main"]');

    const body = bodyElement ? bodyElement.textContent.trim() : '';

    // If we're in the inbox view, try to get the preview
    if (!body && document.querySelector('.bog')) {
        const preview = document.querySelector('.bog').textContent.trim();
        return {
            subject: subject || 'No subject',
            sender: sender || 'Unknown sender',
            body: preview || 'No content available'
        };
    }

    // Validate that we have at least some content
    if (!subject && !body) {
        throw new Error('Could not find email content. Please make sure you are viewing an email.');
    }

    return {
        subject: subject || 'No subject',
        sender: sender || 'Unknown sender',
        body: body || 'No content available'
    };
}

// Set up observer for dynamic content
if (!window.emailReaderObserver) {
    window.emailReaderObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                console.log('Gmail content updated');
            }
        });
    });

    window.emailReaderObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
}

```

**Content CSS (`content/content.css`)**

```css
/* Custom styles for Gmail integration */
.email-reader-ai-button {
    background-color: #6B46C1;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: background-color 0.2s;
}

.email-reader-ai-button:hover {
    background-color: #553C9A;
}

.email-reader-ai-button:disabled {
    background-color: #9F7AEA;
    cursor: not-allowed;
}

```

### Popup Interface

**5.1 Popup HTML (`popup/popup.html`)**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Reader AI</title>
    <link rel="stylesheet" href="popup.css">
    <link href="<https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap>" rel="stylesheet">
    <link rel="stylesheet" href="<https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css>">
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="../assets/logo.png" alt="AudioMail by Murf AI" class="logo">
            <h1>AudioMail by Murf AI</h1>
        </div>

        <i class="fas fa-microphone mic-icon"></i>
        <h2>Summarize your emails</h2>
        <p class="subtitle">Get quick audio summaries of your inbox.</p>

        <div class="status-container">
            <span class="status-text">Ready</span>
        </div>

        <button id="summarizeBtn" class="summarize-button">Summarize Email</button>

        <div class="summary-container hidden">
            <h3>Summary</h3>
            <p id="summaryText"></p>
            <audio id="audioPlayer" controls></audio>
        </div>

        <div class="footer">
            <p>Powered by Murf AI</p>
        </div>
    </div>
    <script src="popup.js"></script>
</body>
</html>

```

**5.2 Popup JavaScript (`popup/popup.js`)**

```jsx
document.addEventListener('DOMContentLoaded', function() {
    const summarizeBtn = document.getElementById('summarizeBtn');
    const statusContainer = document.querySelector('.status-container');
    const statusText = document.querySelector('.status-text');
    const summaryContainer = document.querySelector('.summary-container');
    const summaryText = document.getElementById('summaryText');
    const audioPlayer = document.getElementById('audioPlayer');

    // Function to update status
    function updateStatus(text, isError = false) {
        statusText.textContent = text;
        statusContainer.classList.toggle('error', isError);
    }

    // Function to show loading state
    function setLoading(isLoading) {
        statusContainer.classList.toggle('loading', isLoading);
        summarizeBtn.disabled = isLoading;
    }

    // Function to show summary
    function showSummary(summary, audioUrl) {
        summaryText.textContent = summary;
        audioPlayer.src = audioUrl;
        summaryContainer.classList.remove('hidden');
    }

    // Function to check if server is running
    async function checkServerStatus() {
        try {
            const response = await fetch('<http://localhost:8000/health>');
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    // Function to get current email content
    async function getCurrentEmail() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab.url.includes('mail.google.com')) {
            throw new Error('Please open Gmail to use this extension');
        }

        try {
            const response = await chrome.tabs.sendMessage(tab.id, { action: 'getEmailContent' });

            if (response.error) {
                throw new Error(response.error);
            }

            return response;
        } catch (error) {
            console.error('Error getting email content:', error);
            if (error.message.includes('Receiving end does not exist')) {
                throw new Error('Please refresh the Gmail page and try again');
            }
            throw error;
        }
    }

    // Function to summarize email
    async function summarizeEmail(emailData) {
        try {
            const isServerRunning = await checkServerStatus();
            if (!isServerRunning) {
                throw new Error('Server is not running. Please start the FastAPI server.');
            }

            const response = await fetch('<http://localhost:8000/api/v1/summarize>', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(emailData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Failed to summarize email');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error summarizing email:', error);
            if (error.message.includes('Failed to fetch')) {
                throw new Error('Could not connect to server. Please make sure the FastAPI server is running.');
            }
            throw error;
        }
    }

    // Event listener for summarize button
    summarizeBtn.addEventListener('click', async () => {
        try {
            setLoading(true);
            updateStatus('Getting email content...');

            const emailData = await getCurrentEmail();
            updateStatus('Generating summary...');

            const result = await summarizeEmail(emailData);
            showSummary(result.summary, result.summary_audio_link);

            updateStatus('Ready');
        } catch (error) {
            updateStatus(error.message, true);
        } finally {
            setLoading(false);
        }
    });
});

```

**5.3 Popup CSS (`popup/popup.css`)**

```css
:root {
    --primary-color: #6B46C1;
    --primary-dark: #553C9A;
    --primary-light: #9F7AEA;
    --background-color: #1A1A2E;
    --text-color: #E2E8F0;
    --success-color: #48BB78;
    --error-color: #F56565;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'DM Sans', sans-serif;
    margin: 0;
    padding: 20px;
    background-color: var(--background-color);
    color: var(--text-color);
    width: 300px;
}

.container {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.logo {
    width: 30px;
    height: 30px;
    margin-right: 10px;
}

.mic-icon {
    font-size: 60px;
    color: var(--primary-light);
    margin-bottom: 20px;
}

h1 {
    font-size: 1.2em;
    color: var(--text-color);
}

h2 {
    font-size: 1.5em;
    margin-bottom: 5px;
    color: var(--text-color);
}

.subtitle {
    font-size: 0.9em;
    color: #a0a0a0;
    margin-bottom: 20px;
}

.status-container {
    margin-bottom: 20px;
    padding: 10px;
    border-radius: 5px;
}

.status-text {
    font-weight: bold;
}

.status-container.loading .status-text::before {
    content: '';
    display: inline-block;
    width: 10px;
    height: 10px;
    border: 2px solid var(--text-color);
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 5px;
}

.status-container.error .status-text {
    color: var(--error-color);
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.summarize-button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    padding: 12px 24px;
    font-size: 1em;
    border-radius: 25px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.summarize-button:hover {
    background-color: var(--primary-dark);
}

.summarize-button:disabled {
    background-color: var(--primary-light);
    cursor: not-allowed;
}

.summary-container {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #333;
    text-align: left;
    width: 100%;
}

.summary-container.hidden {
    display: none;
}

.summary-container h3 {
    font-size: 1.2em;
    margin-bottom: 10px;
    color: var(--text-color);
}

.summary-container p {
    font-size: 0.9em;
    line-height: 1.5;
    color: #b0bec5;
}

audio {
    width: 100%;
    margin-top: 15px;
}

.footer {
    margin-top: 20px;
    font-size: 0.8em;
    color: #a0a0a0;
}

.hidden {
    display: none;
}

```

### Loading the Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select your extension directory

### Testing the Extension

1. Open Gmail in Chrome
2. Click the extension icon in the toolbar
3. Click "Summarize Email" on any open email
4. Wait for the summary and audio to be generated

### Best Practices and Tips

1. **Error Handling**:
    - Always check for server availability
    - Handle network errors gracefully
    - Provide clear error messages to users
2. **Performance**:
    - Use efficient DOM selectors
    - Implement proper cleanup in observers
    - Cache DOM queries when possible
3. **Security**:
    - Validate all user input
    - Use HTTPS for API calls
    - Implement proper CORS policies
4. **User Experience**:
    - Show loading states
    - Provide clear feedback
    - Handle edge cases gracefully


This tutorial provides a solid foundation for building a Chrome extension that integrates with Gmail and provides AI-powered email summarization. The code is modular, well-structured, and follows best practices for Chrome extension development.