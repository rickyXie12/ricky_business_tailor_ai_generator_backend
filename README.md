# Social Media Content Generator

## Performance Results using `py test_performance.py`⚡
- ✅ 10 posts: 39.81 seconds (100% success rate)
- ✅ 50 posts: 3.00 minutes (100% success rate)  
- ✅ 100 posts: 6.28 minutes (100% success rate)

## Batch Generation Results (testing using frontend)

The system successfully meets and exceeds all performance targets.

| Posts | Time          | Success Rate | Rate (posts/min) | Notes                   |
|-------|---------------|--------------|------------------|-------------------------|
| 10    | 40 seconds    | 100%         | ~15              | ✅ Meets < 90s target   |
| 50    | 3.10 minutes  | 100%         | ~16.1            | ✅ Meets < 5m target    |
| 100   | 6.30 minutes  | 100%         | ~15.9            | ✅ Meets < 10m target   |

## Quick Setup

### 1. Environment Variables
Create a `.env` file in the `backend` directory. You can copy `.env.example` to get started.
```
DATABASE_URL="postgresql://user:password@localhost/social_media_db"
OPENAI_API_KEY="your_openai_api_key_here"
SECRET_KEY="your_super_secret_jwt_key_here"
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
3. **Database setup:**
    ```bash
    psql -U myuser -d social_media_db -a -f schema.sql
    ```
4.  **Install dependencies:**
    *(Assuming a `requirements.txt` file exists in your project)*
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set up environment variables:**
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