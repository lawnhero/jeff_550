# ISOM 550 Virtual Teaching Assistant

A Virtual Teaching Assistant application built for ISOM 550 - Data and Decision Analytics MBA core course. This application uses LangChain and Streamlit to provide an interactive interface for students to get help with course-related questions.

## Features

- 📚 Knowledge Base Administration
- 💬 Interactive Q&A with course materials
- 🔍 Smart document search and retrieval
- 🎓 Course-specific responses

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv virtual-ta
source virtual-ta/bin/activate  # On Unix/macOS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
Create a `.env` file with your API keys (do not commit this file)

4. Run the application:
```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Main Streamlit application
- `pages/`: Additional Streamlit pages
- `utils/`: Utility functions and LangChain components
- `data/`: Storage for FAISS index and other data files

## License

See the [LICENSE](LICENSE) file for details. 
