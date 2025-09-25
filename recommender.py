import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load pretrained embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


# -------------------- Recommender Logic --------------------
def get_post_embedding(post):
    """
    Generate embedding for a single post using its metadata.
    """
    text_fields = [
        post.get("title", ""),
        " ".join(post.get("tags", [])),
        post.get("topic", {}).get("name", ""),
        post.get("category", {}).get("description", "")
    ]
    text = " ".join(text_fields)
    return embedding_model.encode(text, convert_to_tensor=True)


def build_user_embedding(user_data):
    """
    Build a user embedding by averaging embeddings of interacted posts.
    Returns None if no interactions (cold start).
    """
    interacted_posts = (
        user_data["liked_posts"] +
        user_data["inspired_posts"] +
        user_data["rated_posts"] +
        user_data["viewed_posts"]
    )
    if not interacted_posts:
        return None

    embeddings = [get_post_embedding(post) for post in interacted_posts]
    return np.mean(embeddings, axis=0)


def recommend_with_embeddings(user_data, project_code=None, top_k=10):
    """
    Generate recommendations using:
    - Personalized scores (based on interactions)
    - Cold start fallback (engagement/popularity)
    - Embedding similarity

    Returns JSON in the required format:
    {
        "status": "success",
        "post": [...]
    }
    """
    all_posts = user_data["all_posts"]
    user_embedding = build_user_embedding(user_data)

    # Compute similarity scores
    embedding_scores = {}
    if user_embedding is not None:
        for post in all_posts:
            post_emb = get_post_embedding(post)
            sim = util.cos_sim(user_embedding, post_emb).item()
            embedding_scores[post["id"]] = sim
    else:
        # Cold start fallback: simple engagement-based scoring
        for post in all_posts:
            engagement = post.get("view_count", 0) * 0.05 + post.get("upvote_count", 0) * 0.2
            embedding_scores[post["id"]] = engagement

    # Blend with personalization (interaction counts)
    final_scores = {}
    for post in all_posts:
        pid = post["id"]
        base_score = embedding_scores.get(pid, 0)

        personal_score = 0
        if pid in {p["id"] for p in user_data["liked_posts"]}: personal_score += 5
        if pid in {p["id"] for p in user_data["inspired_posts"]}: personal_score += 4
        if pid in {p["id"] for p in user_data["rated_posts"]}: personal_score += 3
        if pid in {p["id"] for p in user_data["viewed_posts"]}: personal_score += 1

        final_scores[pid] = base_score * 0.6 + personal_score * 0.4

    # Sort candidates by score
    candidate_posts = sorted(all_posts, key=lambda x: final_scores[x["id"]], reverse=True)

    # Apply category filter if project_code is provided
    if project_code:
        candidate_posts = [
            p for p in candidate_posts
            if p.get("topic", {}).get("project_code") == project_code
        ]

    # Return top_k posts in exact required format
    return {
        "status": "success",
        "post": candidate_posts[:top_k]
    }
