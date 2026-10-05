from flask import Flask, request, jsonify
from flask_cors import CORS
from agent import classify_idea, generate_documents

app = Flask(__name__)
CORS(app)

@app.route('/classify', methods=['POST'])
def classify():
    data = request.json
    if not data or 'idea' not in data:
        return jsonify({"error": "Missing 'idea' in request"}), 400
        
    try:
        result = classify_idea(data['idea'])
        return jsonify(result.model_dump())
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    if not data or 'idea' not in data or 'tier' not in data:
        return jsonify({"error": "Missing 'idea' or 'tier' in request"}), 400
        
    try:
        result = generate_documents(data['idea'], data['tier'])
        return jsonify(result.model_dump())
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
