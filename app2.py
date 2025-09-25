from fastapi import FastAPI, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from data_fetching import fetch_all_user_data
from recommender import recommend_with_embeddings
from database import get_db  # your DB session dependency

# ---------------------- SCHEMA ---------------------- #
class User(BaseModel):
    first_name: str
    last_name: str
    name: str
    username: str
    picture_url: Optional[str] = ""
    user_type: Optional[str] = None
    has_evm_wallet: Optional[bool] = False
    has_solana_wallet: Optional[bool] = False

class TopicOwner(BaseModel):
    first_name: str
    last_name: str
    name: str
    username: str
    profile_url: Optional[str] = ""
    user_type: Optional[str] = None

class Topic(BaseModel):
    id: int
    name: str
    description: str
    image_url: str
    slug: str
    is_public: bool
    project_code: str
    posts_count: int
    language: Optional[str] = None
    created_at: str
    owner: TopicOwner

class Category(BaseModel):
    id: int
    name: str
    count: int
    description: str
    image_url: str

class BaseToken(BaseModel):
    address: str = ""
    name: str = ""
    symbol: str = ""
    image_url: str = ""

class Post(BaseModel):
    id: int
    owner: User
    category: Category
    topic: Topic
    title: str
    is_available_in_public_feed: bool
    is_locked: bool
    slug: str
    upvoted: bool
    bookmarked: bool
    following: bool
    identifier: str
    comment_count: int
    upvote_count: int
    view_count: int
    exit_count: int
    rating_count: int
    average_rating: int
    share_count: int
    bookmark_count: int
    video_link: str
    thumbnail_url: str
    gif_thumbnail_url: str
    contract_address: str
    chain_id: str
    chart_url: str
    baseToken: BaseToken
    created_at: int
    tags: List[str]

class FeedResponse(BaseModel):
    status: str
    post: List[Post]


# ---------------------- APP ---------------------- #
app = FastAPI(
    title="Video Recommendation Engine",
    description="API to fetch personalized and category-based recommendations",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Video Recommendation Engine is running 🚀"}


@app.get("/feed", response_model=FeedResponse)
def get_feed(
    username: str = Query(..., description="Username to fetch recommendations for"),
    project_code: Optional[str] = Query(None, description="Optional filter by project code"),
    top_k: int = Query(10, description="Number of recommendations to return"),
    db: Session = Depends(get_db)
):
    """
    Get personalized or category-based feed for a user.
    - /feed?username={username} → personalized feed
    - /feed?username={username}&project_code={project_code} → category-based feed
    """
    try:
        # Step 1: Fetch user data from API and save to DB
        user_data = fetch_all_user_data(username, db=db)

        # Step 2: Generate recommendations
        raw_posts = recommend_with_embeddings(user_data, project_code, top_k)["post"]

        # Step 3: Map recommender output to schema
        formatted_posts = []
        for p in raw_posts:
            formatted_posts.append({
                "id": p["id"],
                "owner": {
                    "first_name": p["owner"]["first_name"],
                    "last_name": p["owner"]["last_name"],
                    "name": p["owner"]["name"],
                    "username": p["owner"]["username"],
                    "picture_url": p["owner"].get("picture_url", ""),
                    "user_type": p["owner"].get("user_type"),
                    "has_evm_wallet": p["owner"].get("has_evm_wallet", False),
                    "has_solana_wallet": p["owner"].get("has_solana_wallet", False)
                },
                "category": p["category"],
                "topic": p["topic"],
                "title": p["title"],
                "is_available_in_public_feed": p.get("is_available_in_public_feed", True),
                "is_locked": p.get("is_locked", False),
                "slug": p["slug"],
                "upvoted": p.get("upvoted", False),
                "bookmarked": p.get("bookmarked", False),
                "following": p.get("following", False),
                "identifier": p.get("identifier", ""),
                "comment_count": p.get("comment_count", 0),
                "upvote_count": p.get("upvote_count", 0),
                "view_count": p.get("view_count", 0),
                "exit_count": p.get("exit_count", 0),
                "rating_count": p.get("rating_count", 0),
                "average_rating": p.get("average_rating", 0),
                "share_count": p.get("share_count", 0),
                "bookmark_count": p.get("bookmark_count", 0),
                "video_link": p["video_link"],
                "thumbnail_url": p["thumbnail_url"],
                "gif_thumbnail_url": p["gif_thumbnail_url"],
                "contract_address": p.get("contract_address", ""),
                "chain_id": p.get("chain_id", ""),
                "chart_url": p.get("chart_url", ""),
                "baseToken": p.get("baseToken", {"address": "", "name": "", "symbol": "", "image_url": ""}),
                "created_at": p.get("created_at", 0),
                "tags": p.get("tags", [])
            })

        return {"status": "success", "post": formatted_posts}

    except Exception as e:
        return {"status": "error", "message": str(e), "post": []}
