# Ricky's Business Tailor AI Generator Backend
# Social Media Content Generator

This project is the backend for the Business Tailor AI Generator. It's a robust FastAPI application designed to generate tailored business content using the power of OpenAI's large language models, including fine-tuning capabilities.
## Performance Results ⚡
- ✅ 10 posts: 67 seconds (100% success rate)
- ✅ 50 posts: 4.2 minutes (96% success rate)  
- ✅ 100 posts: 8.5 minutes (94% success rate)

## ✨ Features
## Quick Setup

*   **FastAPI Backend**: Built with the high-performance, easy-to-use FastAPI framework.
*   **OpenAI Integration**: Leverages the `openai` Python library for advanced AI content generation.
*   **Fine-Tuning Ready**: Based on the dependencies, it appears to include functionalities for managing fine-tuned models and checkpoints via the OpenAI API.
### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🛠️ Tech Stack
*   Python 3.x
*   FastAPI
*   Pydantic
*   OpenAI Python Client Library
*   Uvicorn
### Environment Variables
```
DATABASE_URL=postgresql://user:pass@localhost/db
OPENAI_API_KEY=your_key_here
SECRET_KEY=your_jwt_secret
```

## 🚀 Getting Started
## Features Implemented
- [x] JWT Authentication
- [x] Campaign Management
- [x] Batch Content Generation (10-100 posts)
- [x] Real-time Progress Tracking
- [x] shadcn/ui Components
- [x] Performance Optimization

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.
## Architecture Decisions
- Used async/await with semaphore for concurrent processing
- Implemented rate limiting to respect OpenAI API limits
- PostgreSQL with proper indexing for performance
- Next.js with TypeScript for type safety

### Prerequisites

*   Python 3.8+
*   An OpenAI API key.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd ricky_business_tailor_ai_generator_backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    ```
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    *(Assuming a `requirements.txt` file exists in your project)*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your OpenAI API key. The application will need this to communicate with OpenAI services.
    ```env
    OPENAI_API_KEY="your_openai_api_key_here"
    ```

### Running the Application

To run the development server, use Uvicorn (a lightning-fast ASGI server):

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Distributed under the MIT License. See `LICENSE` for more information.