import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import logging
import sys
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Load model and data once for fallback ML prediction
logger.info("Loading MBTI dataset...")
df = pd.read_csv("data/mbti_1.csv")
logger.info(f"Dataset loaded with {len(df)} rows")

logger.info("Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("SentenceTransformer model loaded")

logger.info("Encoding posts...")
X = model.encode(df["posts"].tolist())
y = LabelEncoder().fit_transform(df["type"])
logger.info("Posts encoded")

logger.info("Training classifier...")
clf = LogisticRegression(max_iter=1000)
clf.fit(X, y)
logger.info("Classifier trained")

types = df["type"].unique()
logger.info(f"Available MBTI types: {types}")

# Load questions for trait mapping
with open("app/questions.json", "r") as f:
    questions = json.load(f)

# Predefined explanations for each MBTI type
MBTI_EXPLANATIONS = {
    "ISTJ": "You are practical, fact-minded, and reliable. You prefer structure and order, and you approach tasks systematically with attention to detail.",
    "ISFJ": "You are warm-hearted, conscientious, and cooperative. You want harmony in your environment and work with determination to establish it.",
    "INFJ": "You seek meaning and connection in ideas, relationships, and material possessions. You want to understand what motivates people and are insightful about others.",
    "INTJ": "You have original minds and great drive for implementing your ideas and achieving your goals. You quickly see patterns in external events and develop long-range explanatory perspectives.",
    "ISTP": "You are tolerant and flexible, quiet observers until a problem appears, then act quickly to find workable solutions. You analyze what makes things work and readily get through large amounts of data to isolate the core of practical problems.",
    "ISFP": "You are quiet, friendly, sensitive, and kind. You enjoy the present moment and what's going on around you. You like to have your own space and to work within your own time frame.",
    "INFP": "You are idealistic, loyal to your values and to people who are important to you. You want an external life that is congruent with your values. You are curious, quick to see possibilities, and can be catalysts for implementing ideas.",
    "INTP": "You seek to develop logical explanations for everything that interests you. You are theoretical and abstract, interested more in ideas than in social interaction. You are quiet, contained, flexible, and adaptable.",
    "ESTP": "You are flexible and tolerant, taking a pragmatic approach focused on immediate results. You are bored by theories and conceptual explanations; you want to act energetically to solve the problem.",
    "ESFP": "You are outgoing, friendly, and accepting. You are exuberant lovers of life, people, and material comforts. You enjoy working with others to make things happen.",
    "ENFP": "You are warmly enthusiastic and imaginative. You see life as full of possibilities. You make connections between events and information very quickly, and confidently proceed based on the patterns you see.",
    "ENTP": "You are quick, ingenious, stimulating, alert, and outspoken. You are resourceful in solving new and challenging problems. You are adept at generating conceptual possibilities and then analyzing them strategically.",
    "ESTJ": "You are practical, realistic, matter-of-fact. You are decisive, quickly move to implement decisions. You organize projects and people to get things done, focus on getting results in the most efficient way possible.",
    "ESFJ": "You are warmhearted, conscientious, and cooperative. You want harmony in your environment and work with determination to establish it. You like to work with others to complete tasks accurately and on time.",
    "ENFJ": "You are warm, empathetic, responsive, and responsible. You are highly attuned to the emotions, needs, and motivations of others. You find potential in everyone and want to help others fulfill their potential.",
    "ENTJ": "You are frank, decisive, assume leadership readily. You quickly see illogical and inefficient procedures and policies, develop and implement comprehensive systems to solve organizational problems."
}

def predict_personality_by_traits(answers):
    """
    Predict MBTI personality type based on trait scoring from questionnaire answers
    """
    # Initialize trait scores
    trait_scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
    
    # Score each answer based on the trait mapping in questions
    for i, answer in enumerate(answers):
        if i < len(questions):
            question = questions[i]
            for option in question['options']:
                if option['text'] == answer:
                    trait = option['trait']
                    if trait != 'X':  # Ignore neutral answers
                        trait_scores[trait] += 1
                    break
    
    # Determine MBTI type based on highest scores in each dimension
    mbti_type = ""
    
    # Extraversion vs Introversion
    if trait_scores['E'] > trait_scores['I']:
        mbti_type += 'E'
    elif trait_scores['I'] > trait_scores['E']:
        mbti_type += 'I'
    else:
        # Tie-breaker: default to I (more common in dataset)
        mbti_type += 'I'
    
    # Sensing vs Intuition
    if trait_scores['S'] > trait_scores['N']:
        mbti_type += 'S'
    elif trait_scores['N'] > trait_scores['S']:
        mbti_type += 'N'
    else:
        # Tie-breaker: default to N (more common in dataset)
        mbti_type += 'N'
    
    # Thinking vs Feeling
    if trait_scores['T'] > trait_scores['F']:
        mbti_type += 'T'
    elif trait_scores['F'] > trait_scores['T']:
        mbti_type += 'F'
    else:
        # Tie-breaker: default to F (slightly more common)
        mbti_type += 'F'
    
    # Judging vs Perceiving
    if trait_scores['J'] > trait_scores['P']:
        mbti_type += 'J'
    elif trait_scores['P'] > trait_scores['J']:
        mbti_type += 'P'
    else:
        # Tie-breaker: default to P (more common in dataset)
        mbti_type += 'P'
    
    logger.info(f"Trait scores: {trait_scores}")
    logger.info(f"Determined MBTI type: {mbti_type}")
    
    return mbti_type

def predict_personality_by_ml(answers):
    """
    Fallback ML prediction based on sentence embeddings (original method)
    """
    combined_input = " ".join(answers)
    emb = model.encode([combined_input])
    pred = clf.predict(emb)[0]
    mbti = types[pred]
    
    logger.info(f"ML predicted MBTI type: {mbti}")
    return mbti

def predict_personality(answers):
    """
    Predict MBTI personality type using trait-based scoring with ML fallback
    """
    logger.info(f"Predicting personality for {len(answers)} answers")
    
    # Primary method: trait-based scoring
    try:
        mbti_type = predict_personality_by_traits(answers)
        method = "trait-based"
    except Exception as e:
        logger.warning(f"Trait-based prediction failed: {e}, falling back to ML")
        mbti_type = predict_personality_by_ml(answers)
        method = "ML-based"
    
    # Get predefined explanation
    explanation = MBTI_EXPLANATIONS.get(mbti_type, f"Based on your responses, you have been classified as {mbti_type} personality type.")
    
    logger.info(f"Final prediction ({method}): {mbti_type}")
    return mbti_type, explanation
