from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.model import predict_personality
import json
import logging
import sys

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

class Answers(BaseModel):
    responses: list[str]

@app.get("/", response_class=HTMLResponse)
def home():
    logger.info("Serving web interface")
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MBTI Personality Test</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
                line-height: 1.6;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .question {
                margin-bottom: 25px;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 8px;
                border-left: 4px solid #007bff;
            }
            .question h3 {
                margin-top: 0;
                color: #333;
            }
            .options {
                margin-top: 15px;
            }
            .option {
                margin: 10px 0;
                padding: 10px;
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .option:hover {
                border-color: #007bff;
                background: #f0f8ff;
            }
            .option.selected {
                border-color: #007bff;
                background: #007bff;
                color: white;
            }
            .option input[type="radio"] {
                margin-right: 10px;
            }
            button {
                background: #007bff;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 20px;
                width: 100%;
                transition: background 0.3s ease;
            }
            button:hover {
                background: #0056b3;
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .result {
                margin-top: 30px;
                padding: 20px;
                background: #e8f5e8;
                border-radius: 8px;
                border-left: 4px solid #28a745;
            }
            .result h2 {
                color: #155724;
                margin-top: 0;
            }
            .loading {
                text-align: center;
                padding: 20px;
            }
            .progress {
                background: #e0e0e0;
                border-radius: 10px;
                height: 10px;
                margin: 20px 0;
            }
            .progress-bar {
                background: #007bff;
                height: 100%;
                border-radius: 10px;
                transition: width 0.3s ease;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>MBTI Personality Test</h1>
            <div class="progress">
                <div class="progress-bar" id="progressBar" style="width: 0%"></div>
            </div>
            <div id="questionnaire"></div>
            <button id="submitBtn" onclick="submitAnswers()" disabled>Get My Personality Type</button>
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            let questions = [];
            let answers = [];
            let currentQuestion = 0;

            async function loadQuestions() {
                try {
                    const response = await fetch('/questions');
                    questions = await response.json();
                    displayQuestions();
                } catch (error) {
                    console.error('Error loading questions:', error);
                }
            }

            function displayQuestions() {
                const questionnaire = document.getElementById('questionnaire');
                questionnaire.innerHTML = '';
                
                questions.forEach((q, index) => {
                    const questionDiv = document.createElement('div');
                    questionDiv.className = 'question';
                    questionDiv.innerHTML = `
                        <h3>Question ${index + 1}</h3>
                        <p>${q.question}</p>
                        <div class="options">
                            ${q.options.map((option, optIndex) => `
                                <div class="option" onclick="selectOption(${index}, ${optIndex}, '${option.text}')">
                                    <input type="radio" name="q${index}" value="${option.text}" id="q${index}_${optIndex}">
                                    <label for="q${index}_${optIndex}">${option.text}</label>
                                </div>
                            `).join('')}
                        </div>
                    `;
                    questionnaire.appendChild(questionDiv);
                });
            }

            function selectOption(questionIndex, optionIndex, text) {
                // Remove previous selection
                const questionDiv = document.querySelectorAll('.question')[questionIndex];
                questionDiv.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));
                
                // Add selection to clicked option
                const selectedOption = questionDiv.querySelectorAll('.option')[optionIndex];
                selectedOption.classList.add('selected');
                selectedOption.querySelector('input').checked = true;
                
                // Store answer
                answers[questionIndex] = text;
                
                // Update progress
                const progress = (answers.filter(a => a).length / questions.length) * 100;
                document.getElementById('progressBar').style.width = progress + '%';
                
                // Enable submit button if all questions answered
                if (answers.filter(a => a).length === questions.length) {
                    document.getElementById('submitBtn').disabled = false;
                }
            }

            async function submitAnswers() {
                const submitBtn = document.getElementById('submitBtn');
                submitBtn.disabled = true;
                submitBtn.textContent = 'Analyzing...';
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            responses: answers.filter(a => a)
                        })
                    });
                    
                    const result = await response.json();
                    displayResult(result);
                } catch (error) {
                    console.error('Error getting prediction:', error);
                    alert('Error getting prediction. Please try again.');
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Get My Personality Type';
                }
            }

            function displayResult(result) {
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = `
                    <h2>Your Personality Type: ${result.mbti}</h2>
                    <p>${result.explanation}</p>
                    <button onclick="restartTest()" style="width: auto; margin-top: 15px;">Take Test Again</button>
                `;
                resultDiv.style.display = 'block';
                resultDiv.scrollIntoView({ behavior: 'smooth' });
            }

            function restartTest() {
                answers = [];
                document.getElementById('result').style.display = 'none';
                document.getElementById('submitBtn').disabled = true;
                document.getElementById('progressBar').style.width = '0%';
                
                // Clear all selections
                document.querySelectorAll('.option').forEach(opt => {
                    opt.classList.remove('selected');
                    opt.querySelector('input').checked = false;
                });
            }

            // Load questions when page loads
            loadQuestions();
        </script>
    </body>
    </html>
    """

@app.get("/questions")
def get_questions():
    logger.info("Questions endpoint called")
    with open("app/questions.json", "r") as f:
        questions = json.load(f)
    return questions

@app.post("/predict")
def predict(data: Answers):
    logger.info(f"Prediction request received with {len(data.responses)} responses")
    mbti_type, explanation = predict_personality(data.responses)
    logger.info(f"Prediction completed: {mbti_type}")
    return {"mbti": mbti_type, "explanation": explanation}

@app.on_event("startup")
async def startup_event():
    logger.info("MBTI Predictor application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("MBTI Predictor application shutting down...")
