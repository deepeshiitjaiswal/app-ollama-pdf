# PDF Chat Assistant

A full-stack application that allows users to chat with and get summaries of PDF documents using Ollama and Mistral AI.

## Project Structure

```
ollama-pdf-chat-app/
├── app.py                 # Flask backend server
├── index.html             # Root HTML template
├── package.json           # Node.js dependencies and scripts
├── vite.config.js         # Vite configuration
├── src/                   # Frontend source code
│   ├── App.jsx           # Main React component
│   └── main.jsx          # React entry point
└── uploads/              # PDF file upload directory (created at runtime)
```

## Features

- PDF file upload and text extraction
- Interactive chat with PDF content
- PDF summarization
- Modern React UI with Chakra UI components
- Flask backend with Ollama integration

## Setup Instructions

1. Install dependencies:
   ```bash
   # Install Python dependencies
   pip install flask PyPDF2 ollama

   # Install Node.js dependencies
   npm install
   ```

2. Start the backend server:
   ```bash
   python app.py
   ```

3. Start the frontend development server:
   ```bash
   npm run dev
   ```

4. Access the application at http://localhost:5173

## Technical Stack

### Frontend
- React 18
- Chakra UI
- Axios for API calls
- Vite as build tool

### Backend
- Flask
- PyPDF2 for PDF processing
- Ollama for AI model integration
- Mistral model for text generation

## API Endpoints

- `POST /upload` - Upload and process PDF files
- `POST /chat` - Chat with the PDF content
- `POST /summarize` - Generate PDF summary