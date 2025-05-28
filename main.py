import flask
from flask import Flask, request, jsonify
from summarise_feed import give_text
from pipeline import execute

app= flask.Flask(__name__)

@app.route('/generate-minecraft', methods=['POST'])
def generate_minecraft():
    try:
        data = request.json
        print("Received data:", data)
        text = data.get('text')
        print("Text to be processed:", text)
        voice_id = data.get('voice_id', 'JBFqnCBsd6RMkjVDRZzb')
        font_path = data.get('font_path', 'fonts/font.ttf')
        title = data.get('title', 'You won\'t believe what just happened!')
        description = data.get('description', 'Stay updated with the latest news in just 30 seconds!')

        execute(text, voice_id, font_path, title, description)
        return jsonify({"status": "success", "message": "Video generated successfully!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
if __name__ == '__main__':
    app.run(port=5000)