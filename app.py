
from flask import Flask, jsonify, request
from email_validation_utils import verify_email

app = Flask(__name__)
app.env = "development"
app.config['JSON_SORT_KEYS'] = False

import nest_asyncio
nest_asyncio.apply()

@app.route('/')
def welcome():
    return jsonify("Welecome to email validation!")
    
@app.route('/email_verify',methods=['POST'])
async def email_verification():
    """ 
    This is the email verify  endpoint.

    endpoitn:
        POST: email_verify
    Request Body:
        email: abc@gmail.com
    Returns:
        It return json response with email details.

    """
    data = request.get_json()
    data ,response_data= verify_email(data['email'])
    return jsonify({
        "data":response_data[1] if type(response_data) == tuple else response_data
    })
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)





