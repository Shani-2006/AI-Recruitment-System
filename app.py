from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import requests
import json
import os

app = Flask(__name__)
CORS(app) 


client = OpenAI(api_key="The-Client-Key")


MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/tqy9h8ct8i5i8sg4lmjygt28qp3gw9kn"


SCHEMA = {
    "type": "object",
    "properties": {
        "candidate_name": {"type": "string"},
        "job_title": {"type": "string"},
        "experience_years": {"type": "integer"},
        "top_skills": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"}
    },
    "required": ["candidate_name", "job_title", "experience_years", "top_skills"]
}

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
      
        data = request.json
        user_text = data.get("text", "")
        
        if not user_text:
            return jsonify({"status": "error", "message": "No text provided"}), 400


        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a recruitment assistant. Extract details in JSON format. If a piece of information like candidate_name or experience_years is missing from the text, use 'Unknown' or 0 for years. Provide a short 1-sentence professional summary."},
                {"role": "user", "content": user_text}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "recruitment_extraction",
                    "schema": SCHEMA
                }
            }
        )

        json_result_string = response.choices[0].message.content
        json_result_object = json.loads(json_result_string)

        
        requests.post(MAKE_WEBHOOK_URL, json=json_result_object)

        
        return jsonify({
            "status": "success", 
            "data": json_result_object
        })

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    
    app.run(port=5000, debug=True)