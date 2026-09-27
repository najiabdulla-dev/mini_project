import numpy as np
from sentence_transformers import SentenceTransformer

# Load a lightweight pretrained model (all-MiniLM-L6-v2) for embeddings
# We initialize it at module level so it loads once per worker process.
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def generate_profile_text(user):
    """Combine user skills, bio, and experience into a single text document."""
    parts = []
    if user.bio:
        parts.append(user.bio)
        
    skills = [us.skill.name for us in user.user_skills.filter(is_active=True)]
    if skills:
        parts.append("Skills: " + ", ".join(skills))
        
    experiences = [f"{exp.title} at {exp.company}" for exp in user.experiences.all()]
    if experiences:
        parts.append("Experience: " + ", ".join(experiences))
        
    return " ".join(parts)

def update_user_embedding(user):
    """
    AI-based content recommendation using sentence embeddings.
    Generates and saves the vector embedding for the user.
    """
    text = generate_profile_text(user)
    if not text.strip():
        text = "Empty profile"
        
    model = get_embedding_model()
    # Compute embedding and convert to list of floats for JSONField
    embedding = model.encode(text).tolist()
    
    # Save directly using update to avoid recursive save calls
    user.profile_embedding = embedding
    user.__class__.objects.filter(pk=user.pk).update(profile_embedding=embedding)

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two lists of floats."""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
