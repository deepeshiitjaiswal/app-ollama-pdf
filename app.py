from flask import Flask, request, render_template, jsonify
import PyPDF2
import os
import logging
import ollama

app = Flask(__name__)
app.config.update({
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
    'ALLOWED_EXTENSIONS': {'pdf'},
    'UPLOAD_FOLDER': 'uploads'
})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pdf_context = ""
CHUNK_SIZE = 3500  # Optimal for processing

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    global pdf_context
    if 'file' not in request.files:
        logger.error('No file part in request')
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        logger.warning('Empty filename submitted')
        return jsonify({'error': 'No file selected'}), 400
    
    if not (file and allowed_file(file.filename) and file.mimetype == 'application/pdf'):
        logger.error(f'Invalid file type: {file.mimetype}')
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    try:
        pdf_context = ""
        pdf_reader = PyPDF2.PdfReader(file.stream)
        if len(pdf_reader.pages) == 0:
            logger.error('Empty PDF file uploaded')
            return jsonify({'error': 'The PDF file is empty'}), 400

        extracted_text = []
        for page_num, page in enumerate(pdf_reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    extracted_text.append(f"Page {page_num}:\n{page_text.strip()}")
            except Exception as e:
                logger.warning(f"Error extracting page {page_num}: {str(e)}")
                continue
                
        if not extracted_text:
            logger.error('PDF text extraction failed')
            return jsonify({'error': 'No text could be extracted (scanned PDF?)'}), 400
            
        pdf_context = "\n".join(extracted_text)
        logger.info(f'Successfully processed PDF with {len(extracted_text)} text pages; total text length: {len(pdf_context)}')
        return jsonify({
            'message': f'PDF processed successfully ({len(extracted_text)} pages with text)',
            'page_count': len(extracted_text)
        })
        
    except PyPDF2.errors.PdfReadError as e:
        logger.error(f'PDF read error: {str(e)}')
        return jsonify({'error': 'Corrupted or encrypted PDF file'}), 400
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return jsonify({'error': f'PDF processing failed: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    global pdf_context
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            logger.warning('Invalid chat request format')
            return jsonify({'error': 'Invalid request format'}), 400
            
        query = data['query'].strip()
        logger.info(f'Chat request: {query[:50]}...')
        
        if not pdf_context:
            logger.warning('Chat attempted without PDF context')
            return jsonify({'error': 'No PDF content available - upload first'}), 400
            
        if len(query) < 3:
            logger.warning('Short query received')
            return jsonify({'error': 'Please ask a meaningful question (min 3 characters)'}), 400

        context_lines = pdf_context.split('\n')[:10]  # First 10 lines
        context = "\n".join(context_lines)[:CHUNK_SIZE]
        
        prompt = (
            "Use this PDF context to answer the question.\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n"
            "Answer:"
        )
        
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        answer = response['message']['content'].strip()
        
        return jsonify({'answer': answer})

    except Exception as e:
        logger.error(f'Chat error: {str(e)}')
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    global pdf_context
    try:
        if not pdf_context:
            logger.warning('Summarization attempted without PDF context')
            return jsonify({'error': 'No PDF content available - upload first'}), 400

        logger.info(f'Summarizing PDF content of length: {len(pdf_context)}')
        
        # Updated summarization prompt for clarity and detail
        prompt = (
            "You are a helpful assistant. Summarize the following PDF content in a clear, concise manner, "
            "highlighting the key points and main ideas.\n"
            "PDF Content:\n"
            f"{pdf_context[:CHUNK_SIZE]}\n"
            "Summary:"
        )
        
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        summary = response['message']['content'].strip()
        
        # If summary is too short, try a second prompt
        if not summary or len(summary) < 10:
            logger.warning("Received a short summary. Retrying with adjusted prompt.")
            prompt = (
                "You are a helpful assistant. Please provide a detailed summary of the following PDF content, "
                "covering all major points and ideas.\n"
                f"{pdf_context[:CHUNK_SIZE]}\n"
                "Summary:"
            )
            response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
            summary = response['message']['content'].strip()
        
        return jsonify({'summary': summary})

    except Exception as e:
        logger.error(f'Summarization error: {str(e)}')
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)