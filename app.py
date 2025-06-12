from flask import Flask, request, jsonify, render_template_string
import re
import os

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

def handler(event, context):
    try:
        # Get the request body
        body = event.get('body', '')
        
        # Parse the JSON body
        data = {}
        if body:
            try:
                import json
                data = json.loads(body)
            except json.JSONDecodeError:
                pass
        
        # Get the text from the request
        text = data.get('text', '')
        if not text:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No text provided'
                })
            }
        
        # Generate summary
        summary = summarize_text(text)
        
        # Return the response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'summary': summary
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization'
            }
        }
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization'
            }
        }

# For local testing
if __name__ == '__main__':
    from flask import Flask, request, jsonify
    app = Flask(__name__)
    
    @app.route('/api/summarize', methods=['POST'])
    def summarize():
        event = {
            'body': request.get_data(as_text=True)
        }
        response = handler(event, None)
        return response['body'], response['statusCode'], response['headers']
    
    @app.route('/', methods=['GET'])
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                    min-height: 150px;
                    margin: 10px 0;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    resize: vertical;
                }
                button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #45a049;
                }
                .summary-container {
                    margin-top: 20px;
                    border-top: 1px solid #ddd;
                    padding-top: 20px;
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
                <textarea id="inputText" placeholder="Enter text to summarize"></textarea>
                <button onclick="summarize()">Summarize</button>
                <div class="summary-container" id="summaryContainer" style="display: none;">
                    <h2>Summary:</h2>
                    <textarea id="summaryText" placeholder="Summary will appear here" readonly></textarea>
                </div>
                <div id="errorMessage" class="error-message"></div>
            </div>

            <script>
                async function summarize() {
                    const inputText = document.getElementById('inputText').value.trim();
                    const summaryText = document.getElementById('summaryText');
                    const summaryContainer = document.getElementById('summaryContainer');
                    const errorMessage = document.getElementById('errorMessage');
                    
                    if (!inputText) {
                        errorMessage.textContent = 'Please enter some text to summarize';
                        return;
                    }

                    try {
                        errorMessage.textContent = '';
                        summaryContainer.style.display = 'block';
                        
                        const response = await fetch('/.netlify/functions/api/summarize', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Accept': 'application/json'
                            },
                            body: JSON.stringify({ text: inputText })
                        });

                        if (!response.ok) {
                            throw new Error('Failed to generate summary');
                        }

                        const data = await response.json();
                        summaryText.value = data.summary;
                        summaryText.removeAttribute('readonly');
                    } catch (error) {
                        errorMessage.textContent = 'Error generating summary';
                        console.error('Error:', error);
                        summaryContainer.style.display = 'none';
                    }
                }
            </script>
        </body>
        </html>
    ''')

    if __name__ == '__main__':
        port = int(os.environ.get('FLASK_RUN_PORT', 8000))
        host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
        app.run(host=host, port=port)
