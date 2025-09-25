Video Recommendation Engine

A FastAPI-based video recommendation system that provides personalized and category-based recommendations for users, leveraging embeddings, user interactions, and engagement-based scoring.

Features

Personalized Recommendations:
Combines user interactions (likes, views, ratings, inspirations) and embedding similarity to generate recommendations.

Category/Project-based Feed:
Supports filtering recommendations by project code.

Cold Start Handling:
If a user has no interaction history, the system falls back on engagement/popularity-based scoring.

Structured Response:
Returns data in a schema-compliant JSON format, including post details, owner, topic, category, video links, and tags.

System Components
1. data_fetching.py

Fetches all posts and user interactions from an external API.

Returns a dictionary containing:

all_posts: All available posts

viewed_posts, liked_posts, inspired_posts, rated_posts: User-specific interactions

2. recommender.py

Generates embeddings for posts using sentence-transformers.

Builds a user embedding by averaging embeddings of interacted posts.

Calculates similarity between user embedding and posts.

Combines embedding similarity with interaction-based scores to produce top-k recommendations.

3. app2.py (FastAPI)

Provides a REST API for fetching recommendations:

GET / → basic health check.

GET /feed?username={username}&project_code={optional}&top_k={optional} → returns personalized or category-based recommendations.

Uses Pydantic models to ensure response schema compliance.





Example API Response
{
  "status": "success",
  "post": [
    {
      "id": 3104,
      "owner": {
        "first_name": "Sachin",
        "last_name": "Kinha",
        "name": "Sachin Kinha",
        "username": "sachin",
        "picture_url": "https://assets.socialverseapp.com/profile/19.png",
        "user_type": null,
        "has_evm_wallet": false,
        "has_solana_wallet": false
      },
      "category": { ... },
      "topic": { ... },
      "title": "testing-topic",
      "video_link": "https://video-cdn.socialverseapp.com/sachin_d323e3b5-0012-4e55-85cc-b15dbe47a470.mp4",
      "tags": ["testing", "editing", "social-media"]
    }
  ]
}


How It Works

Data Fetching:
Fetch all posts and user-specific interactions from the API.

User Embedding:
Compute an embedding for the user based on interacted posts.

Post Scoring:
Compute similarity scores between user embedding and posts.
Blend with interaction-based and engagement-based scores.

Recommendation:
Return top-k posts in a structured JSON format, optionally filtered by project code. 



Installation & Setup

Clone the repository:

git clone <repo_url>
cd video-recommendation-assignment


Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows


Install dependencies:

pip install -r requirements.txt


Set up environment variables in .env:

API_BASE_URL=<your_api_base_url>
FLIC_TOKEN=<your_flic_token>


(Optional) Database setup & migrations

Configure alembic.ini with your DB URL.

Run migrations:

alembic upgrade head


Run the FastAPI server:

uvicorn app2:app --reload


Open API docs:

Swagger UI → http://127.0.0.1:8000/docs

Redoc → http://127.0.0.1:8000/redoc    