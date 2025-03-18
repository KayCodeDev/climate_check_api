# Climate Air Quality API.
This FastAPI application combines Google's Air Quality API with Claude AI to provide enhanced analysis of air quality data. The application fetches current air quality conditions for a given location and then uses Claude AI to generate insights.

### Author
# Kenneth I

### Tech

This project uses a number of open source projects to work properly:

* [python]
* [FastAPI]
* [Google Air Quality API]
* [Claude AI]

### Getting Started

``` sh
# Clone this repo to your local machine using
git clone [Project Repo]

# Get into the directory
cd climate_check_api

# Make it your own
pip install fastapi uvicorn pydantic httpx python-dotenv anthropic

# Edit .env file and add your mysql username, mysql password and db name
vi .env

# replace with your keys
GOOGLE_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Run API
fastapi dev main.py

# Run all tests
pytest

# Run tests with coverage report
pytest --cov=functions --cov=main --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py
```

**Enjoy :)**
