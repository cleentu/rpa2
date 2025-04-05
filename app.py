from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure the Generative AI API
api_key = "AIzaSyAw_kEFyG0Kau-n2kMOkFZT3DoBXQp81xM" 
os.environ["GEMINI_API_KEY"] = "AIzaSyAw_kEFyG0Kau-n2kMOkFZT3DoBXQp81xM"
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
  system_instruction="""You are an intelligent text extraction agent. Your task is to extract relevant information from the input text and organize it into a markdown table with the following fixed columns:
Team, Priority, and Issue.

EXTRACTION RULES:
1.	Only extract information that clearly maps to the predefined columns.
2.	Do not create new columns or categories beyond what is defined.
3.	If information for any column is not found, use \"N/A\".
4.	Maintain consistent formatting for similar data types.
5.	Do not infer or assume information that isn't explicitly stated in the input.

COLUMN CRITERIA:
1. Team:
Match based on keywords from the following groups. Assign the corresponding team name if any of these sub-keywords appear:
•	Course:
Bulk Edit, Certificates, Application Fee, Courses, Course Not Found, Qualifications
•	Grants:
Course Run, Grants Calculator, API, Enrolment, Attendance, Assessment
•	Common Services:
IP Address, Access to TPG, Tables, Infrastructure, Bugs, Patches, Service Request
•	Account Access:
Permissions, Account Reactivation, Account Deactivation, TGS Access
2. Priority:
•	Most issues are Low priority unless explicitly marked otherwise.
If urgency or escalated importance is clearly stated, mark as High.
Otherwise, default to Low.
3. Issue:
Determine based on context:
•	Data
•	Application
•	Service Request
•	User Enquiry
If unclear, use \"N/A\".

OUTPUT FORMAT:
Present the extracted information using the following structure:
Team:       [TeamName]



Priority:   [PriorityLevel]



Issue:      [IssueType]

For example:
Team:       Course



Priority:   Low



Issue:      User Enquiry""",
)

chat_session = model.start_chat(
  history = [
  {
    "role": "user",
    "parts": [
      "I applied for the Cybersecurity Essentials course via the portal last week. May I know the status of my application and whether any further documents are required?"
    ]
  },
  {
    "role": "model",
    "parts": [
      "Team:       Course\n\nPriority:   Low\n\nIssue:      User Enquiry"
    ]
  },
  {
    "role": "user",
    "parts": [
      "I recently completed the Data Literacy Foundations course and noticed my name was misspelled on the certificate. Could you please re-issue the certificate with the correct spelling: Anjali Verma?"
    ]
  },
  {
    "role": "model",
    "parts": [
      "Team:       Course\n\nPriority:   Low\n\nIssue:      Data"
    ]
  },
  {
    "role": "user",
    "parts": [
      "We've noticed a mismatch in the enrolment data pushed to the SSG API for the April intake. Kindly review the submission and advise on next steps to ensure compliance."
    ]
  },
  {
    "role": "model",
    "parts": [
      "Team:       Grants\n\nPriority:   Low\n\nIssue:      Data"
    ]
  },
  {
    "role": "user",
    "parts": [
      "Could you clarify the expected response schema for the /disbursementStatus endpoint in the new TGS Grant API v2.1? We're facing parsing issues during the integration testing."
    ]
  },
  {
    "role": "model",
    "parts": [
      "Team:       Grants\n\nPriority:   Low\n\nIssue:      User Enquiry"
    ]
  }
]

    
)

#msg = input('How can I help you?')
#response = chat_session.send_message(msg)

#print(response.text)


# Route to render the index.html page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/generate', methods=['POST'])
def generate_ideas():
    try:
        # Get user input from the form
        user_input = request.form.get('prompt', '')

        # Initialize a chat session for each request
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=generation_config,
            system_instruction="""You are an intelligent text extraction agent. Your task is to extract relevant information from the input text and organize it into a markdown table with the following fixed columns:
Team, Priority, and Issue.

EXTRACTION RULES:
1.	Only extract information that clearly maps to the predefined columns.
2.	Do not create new columns or categories beyond what is defined.
3.	If information for any column is not found, use \"N/A\".
4.	Maintain consistent formatting for similar data types.
5.	Do not infer or assume information that isn't explicitly stated in the input.

COLUMN CRITERIA:
1. Team:
Match based on keywords from the following groups. Assign the corresponding team name if any of these sub-keywords appear:
•	Course:
Bulk Edit, Certificates, Application Fee, Courses, Course Not Found, Qualifications
•	Grants:
Course Run, Grants Calculator, API, Enrolment, Attendance, Assessment
•	Common Services:
IP Address, Access to TPG, Tables, Infrastructure, Bugs, Patches, Service Request
•	Account Access:
Permissions, Account Reactivation, Account Deactivation, TGS Access
2. Priority:
•	Most issues are Low priority unless explicitly marked otherwise.
If urgency or escalated importance is clearly stated, mark as High.
Otherwise, default to Low.
3. Issue:
Determine based on context:
•	Data
•	Application
•	Service Request
•	User Enquiry
If unclear, use \"N/A\".

OUTPUT FORMAT:
Present the extracted information using the following structure:
 Team:       [TeamName]



Priority:   [PriorityLevel]



Issue:      [IssueType]

For example:
Team:       Course



Priority:   Low



Issue:      User Enquiry""",
        )
        chat_session = model.start_chat(history=[
            {"role": "user", "parts": [user_input]}
        ])

        # Generate the response
        response = chat_session.send_message(user_input)

        # Return the generated response
        generated_text = response.text.replace('*', '\n')
        return jsonify({"output": generated_text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)

