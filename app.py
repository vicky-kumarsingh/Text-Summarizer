from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

def summarize_text(text, num_sentences=3):
    try:
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        
        # Remove empty sentences
        sentences = [s for s in sentences if s.strip()]
        
        # If we have fewer sentences than requested, return all
        if len(sentences) <= num_sentences:
            return ' '.join(sentences)
            
        # Take the first few sentences as summary
        summary = ' '.join(sentences[:num_sentences])
        return summary
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/api/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
            
        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
            
        summary = summarize_text(text)
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Text Summarizer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            textarea {
                width: 100%;
                height: 150px;
                margin: 10px 0;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: inherit;
            }
            button {
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: #45a049;
            }
            .summary-container {
                margin-top: 20px;
                display: none;
            }
            .visible {
                display: block;
            }
            .error-message {
                color: red;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Text Summarizer</h1>
            <textarea id="inputText" placeholder="Enter text to summarize..."></textarea>
            <button onclick="summarize()">Summarize</button>
            <div class="summary-container" id="summaryContainer">
                <h2>Summary:</h2>
                <textarea id="summaryText" placeholder="Summary will appear here"></textarea>
            </div>
            <div id="errorMessage" class="error-message"></div>
        </div>

        <script>
            async function summarize() {
                const inputText = document.getElementById('inputText').value.trim();
                const errorMessage = document.getElementById('errorMessage');
                const summaryContainer = document.getElementById('summaryContainer');
                const summaryText = document.getElementById('summaryText');
                
                if (!inputText) {
                    errorMessage.textContent = 'Please enter some text to summarize.';
                    return;
                }
                
                errorMessage.textContent = '';
                summaryContainer.classList.remove('visible');
                
                try {
                    const response = await fetch('/api/summarize', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({ text: inputText })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        summaryContainer.classList.add('visible');
                        summaryText.value = result.summary;
                    } else {
                        throw new Error(result.error || 'An error occurred');
                    }
                } catch (error) {
                    errorMessage.textContent = error.message;
                }
            }
        </script>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
