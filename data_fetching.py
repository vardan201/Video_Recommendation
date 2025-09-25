import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models import User, Post  # your SQLAlchemy models

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
FLIC_TOKEN = os.getenv("FLIC_TOKEN")

headers = {"Flic-Token": FLIC_TOKEN}


def fetch_data(endpoint, page_size=1000):
    """
    Fetch paginated data from an endpoint.
    Returns combined list of all items.
    """
    all_items = []
    page = 1
    while True:
        url = f"{API_BASE_URL}{endpoint}&page={page}&page_size={page_size}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching {endpoint}: {response.status_code}")
            break
        data = response.json()
        items = data.get("post", [])
        if not items:
            break
        all_items.extend(items)
        if len(items) < page_size:  # Last page
            break
        page += 1
    return all_items


def save_user_posts(db: Session, user_data):
    """
    Persist fetched posts and their owners in the database.
    """
    for post in user_data["all_posts"]:
        owner_data = post["owner"]

        # Check if user exists
        db_user = db.query(User).filter(User.username == owner_data["username"]).first()
        if not db_user:
            db_user = User(
                username=owner_data["username"],
                first_name=owner_data.get("first_name", ""),
                last_name=owner_data.get("last_name", "")
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        # Check if post exists
        if not db.query(Post).filter(Post.id == post["id"]).first():
            db_post = Post(
                id=post["id"],
                title=post.get("title", ""),
                owner_id=db_user.id
            )
            db.add(db_post)
    db.commit()


def fetch_all_user_data(username, db: Session = None):
    """
    Fetch all relevant data for a given username.
    Optionally saves data to the database if a Session is provided.
    """
    user_data = {}

    # All posts
    user_data["all_posts"] = fetch_data("/posts/summary/get?")

    # User interactions
    user_data["viewed_posts"] = fetch_data(f"/posts/view?username={username}&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if&")
    user_data["liked_posts"] = fetch_data(f"/posts/like?username={username}&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if&")
    user_data["inspired_posts"] = fetch_data(f"/posts/inspire?username={username}&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if&")
    user_data["rated_posts"] = fetch_data(f"/posts/rating?username={username}&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if&")

    # Save to DB if session provided
    if db:
        save_user_posts(db, user_data)

    return user_data


# Example usage
if __name__ == "__main__":
    from database import SessionLocal  # import your DB session
    username = "doeyy"  # replace with real username
    db = SessionLocal()
    data = fetch_all_user_data(username, db=db)
    print(f"Total posts fetched: {len(data['all_posts'])}")
    print(f"Posts viewed by {username}: {len(data['viewed_posts'])}")
    print(f"Posts liked by {username}: {len(data['liked_posts'])}")
    print(f"Posts inspired by {username}: {len(data['inspired_posts'])}")
    print(f"Posts rated by {username}: {len(data['rated_posts'])}")
    db.close()
