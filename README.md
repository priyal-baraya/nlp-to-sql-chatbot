# Natural Language to SQL Chatbot

A conversational web application that converts natural language questions into SQL queries using Google Gemini, executes them on a MySQL database, and returns accurate responses and query results.

---

## Features

- Natural language question interpretation  
- Context-aware follow-up support  
- Chat-like user interface for interaction  
- SQL query preview with each answer  
- Structured table view for result data  
- "Clear Chat" functionality  
- Secure environment-based configuration  

---

## Technologies Used

| Technology       | Purpose                                              |
|------------------|------------------------------------------------------|
| Flask            | Web application framework                           |
| LangChain        | LLM prompt management and tool integration           |
| Google Gemini    | Language model for SQL generation and explanation    |
| SQLAlchemy       | SQL database connectivity and ORM                    |
| Jinja2           | HTML templating in Flask                             |
| MySQL            | Relational database                                  |
| HTML/CSS         | Frontend design                                      |
| python-dotenv    | Environment variable management                      |

---

## Setup Instructions

### Prerequisites

- Python 3.9 or higher  
- MySQL database instance  
- Google Gemini API Key  

### Installation

```bash
git clone https://github.com/your-username/nl-to-sql-chatbot.git
cd nl-to-sql-chatbot
python -m venv venv
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory and add:

```
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_db_name
GOOGLE_API_KEY=your_gemini_api_key
```

> The `.env` file is already excluded via `.gitignore`.

---

## Running the App

```bash
python chatbot.py
```

Visit: [http://localhost:5000](http://localhost:5000)

---

## Example Questions

- Show all dealer names  
- How many users joined this month?  
- What are the top 5 products by sales?  
- Give me total revenue in April  

---

## Project Structure

```
nl-to-sql-chatbot/
│
├── app.py                 # Chatbot logic and Gemini API integration
├── chatbot.py             # Flask app with routing and chat interface
├── templates/
│   └── index.html         # Chat interface HTML template
├── .env                   # Environment variable configuration
├── .gitignore
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## Future Enhancements

- Role-based access (RBAC)  
- Download results as CSV/Excel  
- Dockerized deployment  
- Query caching for performance  
- Input validation and query safety checks  

---

## Data Privacy Notice

This app sends user prompts and context to Google's Gemini API for query generation. Avoid sharing any sensitive or personal information. For production use, consult Google’s data usage policy and implement necessary privacy measures.

---

## License

This project is licensed under the MIT License.

---

## References

- [LangChain Documentation](https://docs.langchain.com/)  
- [Google AI Studio](https://ai.google.dev/)  
- [SQLAlchemy](https://docs.sqlalchemy.org/)  
- [Flask Framework](https://flask.palletsprojects.com/)
