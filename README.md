# Intelligent Product Scraper

This project is a conversational assistant that helps users generate precise product recommendations from Snapdeal using those keywords. It leverages a language model (LLM) to extract exactly 3 relevant keywords from user input, then scrapes Snapdeal for matching products in parallel for fast results.

## Features
- Conversational interface for e-commerce product search
- LLM-powered keyword extraction (always 3 keywords)
- Fast, concurrent scraping of Snapdeal for each keyword
- Robust validation and error handling

## Requirements
- Python 3.8+
- See `requirements.txt` for Python dependencies

## Installation
1. **Clone the repository**
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

## Environment Variables
Create a `.env` file in the project root with your Groq API key:
```
groq_api_key=YOUR_GROQ_API_KEY
```

## Usage
Run the assistant:
```bash
python Connect.py
```

- The assistant will greet you and prompt for your shopping needs.
- Enter your request (e.g., "I need a budget smartphone with good battery").
- The assistant will extract 3 keywords, scrape Snapdeal for each, and show you product options.
- Type `exit` or `quit` to end the session.

## Notes
- The Snapdeal scraper uses Playwright in headless mode and runs all keyword searches in parallel for speed.
- If the LLM does not return exactly 3 keywords, you will be prompted to rephrase your request.
- Make sure your network allows outbound connections to Snapdeal and Playwright can launch browsers.

## Troubleshooting
- If scraping does not work, ensure Playwright browsers are installed and your network/firewall allows access.
- If you see errors about missing dependencies, re-run `pip install -r requirements.txt`.

