# MBTI Personality Predictor MVP

A simplified MBTI personality prediction system that presents users with 10 questions and predicts their personality type based on their responses.

## Features

- **Interactive Web Interface**: Clean, responsive web UI for taking the personality test
- **10 Question Assessment**: Streamlined questionnaire covering key MBTI dimensions
- **Real-time Progress Tracking**: Visual progress bar showing completion status
- **Instant Results**: Immediate personality type prediction with detailed explanations
- **Machine Learning Prediction**: Uses sentence transformers and logistic regression trained on MBTI data
- **Containerized Deployment**: Easy deployment with Docker

## Quick Start

### Using Docker (Recommended)

1. **Build and run the application:**
   ```bash
   docker-compose up --build
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:8000
   ```

3. **Take the test:**
   - Answer all 10 questions
   - Click "Get My Personality Type"
   - View your results!

### Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## Architecture

### Core Components

- **`app/main.py`**: FastAPI web server with embedded HTML interface
- **`app/model.py`**: ML model for personality prediction using sentence transformers
- **`app/questions.json`**: 10 carefully crafted MBTI assessment questions
- **`data/mbti_1.csv`**: Training dataset for the ML model

### Technology Stack

- **Backend**: FastAPI (Python)
- **ML**: scikit-learn, sentence-transformers
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Deployment**: Docker, Docker Compose

## API Endpoints

- **`GET /`**: Web interface for taking the test
- **`GET /questions`**: Returns the 10 assessment questions
- **`POST /predict`**: Accepts user responses and returns MBTI prediction

### Example API Usage

```bash
# Get questions
curl http://localhost:8000/questions

# Submit answers for prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"responses": ["I go out or call friends", "Plan everything carefully", ...]}'
```

## Changes from Previous Version

### Removed Components
- ✅ **Ollama Integration**: Removed local LLM dependency for faster startup
- ✅ **Complex Dependencies**: Simplified requirements to core ML libraries
- ✅ **External API Calls**: Eliminated network dependencies

### Simplified Features
- ✅ **Predefined Explanations**: Fast, consistent personality type descriptions
- ✅ **Streamlined UI**: Single-page application with embedded interface
- ✅ **Quick Deployment**: Reduced Docker build time and complexity

## Testing

Run the test script to verify core functionality:

```bash
python3 test_mvp.py
```

## File Structure

```
├── app/
│   ├── main.py           # FastAPI application with web interface
│   ├── model.py          # ML prediction logic
│   └── questions.json    # Assessment questions
├── data/
│   └── mbti_1.csv       # Training dataset
├── docker-compose.yml    # Docker deployment configuration
├── Dockerfile           # Container build instructions
├── requirements.txt     # Python dependencies
├── test_mvp.py         # Core functionality tests
└── README.md           # This file
```

## MBTI Types Supported

The system can predict all 16 MBTI personality types:

**Analysts**: INTJ, INTP, ENTJ, ENTP  
**Diplomats**: INFJ, INFP, ENFJ, ENFP  
**Sentinels**: ISTJ, ISFJ, ESTJ, ESFJ  
**Explorers**: ISTP, ISFP, ESTP, ESFP  

## Development

### Adding New Questions

Edit `app/questions.json` following this structure:

```json
{
  "id": 11,
  "question": "Your question here?",
  "options": [
    { "text": "Option 1", "trait": "E" },
    { "text": "Option 2", "trait": "I" },
    { "text": "Option 3", "trait": "X" }
  ]
}
```

### Customizing Explanations

Modify the `MBTI_EXPLANATIONS` dictionary in `app/model.py` to customize personality type descriptions.

## License

This project is for educational and demonstration purposes.
