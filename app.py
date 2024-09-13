from flask import Flask, request, jsonify, render_template, send_from_directory
from SAGE import TravelBot

app = Flask(__name__)

# Directly set API keys here
weather_api_key = ''
search_api_key = ''
search_cse_id = ''

# Initialize the SAGE bot
bot = TravelBot(name="SAGE", weather_api_key=weather_api_key, search_api_key=search_api_key, search_cse_id=search_cse_id)

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form.get('user_input', '')
    try:
        response_text = bot.process_query(user_input)
        return jsonify({
            'response': response_text,
            'audio_url': '/static/response.mp3'
        })
    except Exception as e:
        return jsonify({
            'response': 'There was an error processing your request.',
            'audio_url': ''
        }), 500

@app.route('/static/<filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)
