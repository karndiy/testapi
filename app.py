from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_restx import Api, Resource, fields
from datetime import datetime
#from fn_all import generate_id
import fn_all
import unittest
from faker import Faker

import requests

# Initialize the Flask app
app = Flask(__name__)


fn = fn_all
# Initialize the Limiter (using app.config)

# Initialize Flask-RESTx API
api = Api(app, doc='/apidoc', title="GATEWAY API", description="GATE API DATA")
HOST = "http://localhost"
PORT = 5051

fake = Faker('th_TH')


class TestPatientInfo(unittest.TestCase):
    def setUp(self):
        birthdate = fake.date_of_birth(minimum_age=15, maximum_age=80)
        formatted_birthdate = birthdate.strftime('%Y-%d-%m')
        # Generate a single set of fake data with consistent field names
        self.fake_data = {
            "hn": str(fake.random_number(digits=4, fix_len=True)),
            "vn": str(fake.random_number(digits=4, fix_len=True)),
            "cid": fake.ssn(),
            "prefix_name": fake.prefix(),
            "fname": fake.first_name(),
            "lname": fake.last_name(),
            "birthdate": formatted_birthdate,
            "gender": fake.random_element(elements=("male", "female", "อื่น ๆ")),
            "phone": str(fake.random_number(digits=10, fix_len=True)),
            "img": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAwAB/0p8qOUAAAAASUVORK5CYII="
        }

    def generate_patient_data(self, cid=None,hn=None,vn=True):
        """Returns a new dictionary with fake patient data."""
        birthdate = fake.date_of_birth(minimum_age=15, maximum_age=80)
        formatted_birthdate = birthdate.strftime('%Y-%d-%m')
        _hn = ""
        _vn = ""

        if hn == True:
            _hn = str(fake.random_number(digits=5, fix_len=True))
        else :
            _hn = str(hn)


        if vn == True:
           _vn =  str(fake.random_number(digits=5, fix_len=True))
        else :
            _vn = str(vn)

        return {
            "hn": _hn,
            "vn": _vn,
            "cid": str(cid),
            "prefix_name": fake.prefix(),
            "fname": fake.first_name(),
            "lname": fake.last_name(),
            "birthdate": formatted_birthdate,
            "gender": fake.random_element(elements=("male", "female", "อื่น ๆ")),
            "phone": f"0{str(fake.random_number(digits=9, fix_len=True))}",
            "img": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAwAB/0p8qOUAAAAASUVORK5CYII="
        }


    def test_patient_data_structure(self):
        """Test that fake data matches the expected structure."""
        expected_keys = {
            "hn", "vn", "cid", "prefix_name", "fname", "lname", "birthdate",
            "gender",  "phone","img"
        }
        self.assertEqual(set(self.fake_data.keys()), expected_keys)

    def test_patient_data_values(self):
        """Check that each value is correctly generated and not empty."""
        for key, value in self.fake_data.items():
            self.assertIsNotNone(value, f"{key} should not be None")

class StatusCode:
    OK = 100
    CREATED = 101
    ACCEPTED = 102
    COMPLETED = 103
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

    INVALID_IDCARD = 422
    INVALID_VN = 1001
    INVALID_HN = 1002

class StatusMessage:
     
     GETPATIENT_OK = "Get Patient Success!"
     GETPATIENT_NOT_FOUND_CID_HN = "not found hn or cid"
     GETPATIENT_NOT_FOUND_SYSTEM = "not found patient in system!"


class Response:
    @staticmethod
    def create(status_code, status_message, data=None):
        """
        Create a standardized response.

        Args:
            status_code (int): The status code from StatusCode class.
            status_message (str): A message describing the status.
            data (dict, optional): Additional data to include in the response.

        Returns:
            dict: A structured response dictionary.
        """
        response = {
            "statuscode": status_code,
            "statusmessage": status_message,
            
        }
        if data is not None:
            response["data"] = data
        # Add a timestamp to the response data
        response["processed_at"] = datetime.now().isoformat()
        return response



# Generate mock data for multiple patients
def create_mock_patient_data(xtype=None):
    test_instance = TestPatientInfo()
    test_instance.setUp()  # Initialize data in setUp

    # Create multiple patient entries
    if xtype == "cid":
        patients_data = {
            "1111111111111": test_instance.generate_patient_data("1111111111111","11111",True),
            "1111111111119": test_instance.generate_patient_data("1111111111119","11111",True),
            "2222222222227": test_instance.generate_patient_data("2222222222227","22222",True),
            "3333333333333": test_instance.generate_patient_data("3333333333333","33333",True),
            "4444444444444": test_instance.generate_patient_data("4444444444444","44444",True),
            "3440300015187": test_instance.generate_patient_data("3440300015187","34403",True),
            "1710501456572": test_instance.generate_patient_data("1710501456572","17105",""),
            "3102100818892":  test_instance.generate_patient_data("3102100818892","31021",True)
        }

    if xtype == "hn":
        patients_data = {
            "11111": test_instance.generate_patient_data("1111111111111","11111",True),
            "22222": test_instance.generate_patient_data("2222222222227","22222",True),
            "33333": test_instance.generate_patient_data("3333333333333","33333",True),
            "44444": test_instance.generate_patient_data("4444444444444","44444",True),
            "34403": test_instance.generate_patient_data("3440300015187","34403",True),
            "17105": test_instance.generate_patient_data("1710501456572","17105",""),
            "31021":  test_instance.generate_patient_data("3102100818892","31021",True)
        }


    return patients_data

patients_data_cid = create_mock_patient_data("cid")

patients_data_hn = create_mock_patient_data("hn")


getPatientInfo_model = api.model('getPatientInfo', {
    'cid': fields.String(required=True, description="เลขบัตรประจำตัวประชาชนของผู้ป่วย"),
    'hn': fields.String(description="หมายเลขประจำตัวผู้ป่วยในโรงพยาบาล"),
    'vn': fields.String(description="หมายเลข visit number"),
    'prefix_name': fields.String(description="คำนำหน้าชื่อ (เช่น นาย, นาง, นางสาว)"),
    'fname': fields.String(description="ชื่อจริงของผู้ป่วย"),
    'lname': fields.String(description="นามสกุลของผู้ป่วย"),
    "brithdate": fields.String(description="วันเดือนปีเกิดผู้ป่วย"),
    'gender': fields.String(description="เพศของผู้ป่วย (ชาย, หญิง, อื่น ๆ)"),
    'phone': fields.String(description="หมายเลขโทรศัพท์มือถือของผู้ป่วย"),
    'img': fields.String(description="รูปภาพของผู้ป่วยในรูปแบบ base64"),
})

# Define PatientInfo_data as a response model
PatientInfo_data = api.model('PatientInfoData', {
    'statuscode': fields.Integer(description='Status Code Numner',example=100),
    'statusmessage': fields.String(description='Status message for the response',example="Get Patient Success!"),
    'data': fields.Nested(getPatientInfo_model, description='Patient information data')
})

# Define the model schema for validation/documentation purposes (optional but recommended)
# Define the transaction model schema
transaction_model = api.model('Transaction', {
    'hn': fields.String(required=True, description="Hospital number"),
    'vn': fields.String(required=True, description="Visit number"),
    'cid': fields.String(required=True, description="Claim type"),
    'status': fields.String(required=True, description="Transaction status"),
    'appointment_id': fields.String(required=True, description="Appointment ID"),
    'claim_type': fields.String(required=True, description="Claim type"),
    'claim_code': fields.String(required=True, description="Claim code"),
    'doctor_note': fields.String(required=True, description="Doctor Note"),
    'chief_complain': fields.String(description="Complaint ID"),
    'prescription_text': fields.String(description="Prescription text"),



})
# Define the model for vital sign data
vital_sign_data = api.model('VitalSignData', {
    "stattusmessage": fields.String(description="Status message", example="insert vitalsign success"),  
    "statuscode":fields.String(description="Status code", example= StatusCode.OK),
    "data": fields.Nested(api.model('VitalSignDetails', {
        "vn": fields.String(required=True, description="visit number", example="1111"),
        "hn": fields.String(required=True, description="hostital Number", example="2222"),
        "cid": fields.String(required=True, description="Public ID IDCard 13 digits", example="111111111111"),
        "bmi": fields.String(description="Body Mass Index", example="24.74"),
        "bpd": fields.String(description="Diastolic Blood Pressure", example="80"),
        "bps": fields.String(description="Systolic Blood Pressure", example="120"),
        "fbs": fields.String(description="Fasting Blood Sugar", example="1111"),
        "pulse": fields.String(description="Pulse rate", example="89"),
        "rr": fields.String(description="Respiratory rate", example="90"),
        "spo2": fields.String(description="Oxygen saturation level", example="99"),
        "temp": fields.String(description="Temperature in Celsius", example="37.5"),
        "height": fields.String(description="Patient height in cm", example="173"),
        "weight": fields.String(description="Patient weight in kg", example="75.6"),
        "cc": fields.String(description="Chief Complaint", example="อาการเบื้องต้น"),
        "created_at": fields.String(description="Creation timestamp", example=datetime.now().isoformat())
    }))
})

# Define model for incoming vital sign data
send_vital_sign = api.model('SendVitalSign', {
      "vn": fields.String(required=True, description="visit number"),
    "hn": fields.String(required=True, description="hostital Number"),
    'cid': fields.String(required=True, description='Citizen ID'),
    'bmi': fields.String(description='Body Mass Index'),
    'bpd': fields.String(description='Diastolic Blood Pressure'),
    'bps': fields.String(description='Systolic Blood Pressure'),
    'fbs': fields.String(description='Fasting Blood Sugar', default="N/A"),
    'rr': fields.String(description='Respiratory Rate', default="N/A"),
    'pulse': fields.String(description='Pulse Rate', default="N/A"),
    'spo2': fields.String(description='Oxygen Saturation', default="N/A"),
    'temp': fields.String(description='Temperature', default="N/A"),
    'height': fields.String(description='Height', default="N/A"),
    'weight': fields.String(description='Weight', default="N/A"),
    'cc': fields.String(description='Chief Complaint', default="N/A"),
})

# Define the API endpoint with rate limiting
@api.route('/api/vitalsign')
class SendVitalSignResource(Resource):
    @api.expect(send_vital_sign)  # Expecting data as input
    @api.doc(description="Send vital signs to the system")
    @api.response(200, 'POST request processed successfully', vital_sign_data)
    @api.response(400, 'Missing JSON data in the request body ')
    @api.response(500, 'Internal server error')

    def post(self):

        # Get the JSON data from the request body
        input_data = request.get_json()
        print(input_data)
        if not input_data:
            return {
                "statuscode":StatusCode.NOT_FOUND,
                "statusmessage": "NOT_FOUND",
                "error": "Not Found Data"}, 400

        try:
            response_data = {
                "statuscode":StatusCode.OK,
                "statusmessage": "insert vitalsign success",
                "data":{
                    **input_data,
                    "created_at":datetime.now().isoformat()
                }
            }

            

            # Return the response with status code 200
            return response_data, 200
        except Exception as e:
            # Log the error if needed and return a 500 error response
            return {"error": "An internal server error occurred"}, 500

# Define the API endpoint
@api.route('/api/sendtransaction')
class SendTransactionResource(Resource):
    @api.expect(transaction_model)
    @api.doc(description="Send Transaction System")

    @api.response(200, 'Transaction processed successfully')
    @api.response(400, 'Missing JSON data in the request body OR hn or vn query parameter')
    @api.response(404, 'Invalid hn or vn value')
    @api.response(500, 'Internal server error')
    def post(self): 

        # Get the JSON data from the request body
        input_data = request.get_json()
        print(input_data)
        print(input_data['cid'])
        if not input_data:
            return {"error": "Missing JSON data in the request body"}, 400

        if not input_data['cid'] :
            return {"error": "Missing 'cid' query parameter"}, 400

        if not input_data['vn'] or not input_data['hn']:
            return {"error": "Missing 'hn' or 'vn' query parameter"}, 400

        try:
            # Process data and construct response
            response_data = {
                "statuscode":StatusCode.OK,
                "statusmessage": "success",

                "data": {
                    **input_data
                },
                "processed_at": datetime.now().isoformat()
            }
            print(response_data)

            # Return the response with status code 200
            return response_data, 200  # Let Flask-RESTX handle JSON serialization

        except Exception as e:
            # Log the error if needed and return a 500 error response
            return {"error": "An internal server error occurred"}, 500

# Define the API endpoint for getting patient info based on cid
@api.route('/api/patient')
class GetPatientInfoResource(Resource):

    @api.doc(description="Retrieve patient information based on CID")
    @api.param('cid', 'The CID of the patient to retrieve information e.g 1111111111111 , 2222222222227', required=False)
    @api.param('hn', 'The HN of the patient to retrieve information e.g 11111 . 22222', required=False)

    @api.response(200, 'Patient information retrieved successfully', PatientInfo_data)

    @api.response(400, 'Missing CID or Invalid CID')
    @api.response(404, 'Patient not found for the given CID')
    def get(self):
        """Handles GET requests to retrieve patient info based on CID"""

        # Retrieve the 'cid' parameter from the URL
        cid = request.args.get('cid')
        hn = request.args.get('hn')

        print(f"cid :{cid}")
        print(f"hn :{hn}")
        # Validate the 'cid' parameter


        if not str(cid) or not str(hn):
            return Response.create(
                status_code=StatusCode.NOT_FOUND,
                status_message=StatusMessage.GETPATIENT_NOT_FOUND_CID_HN                
            ),404
           

        # Check if the CID exists in the mock data
        #patient_info = patients_data.get(cid)

        if cid:
            patient_info = patients_data_cid.get(str(cid) )
        elif hn:
            patient_info = patients_data_hn.get(str(hn))

        if not patient_info:
            return  Response.create(
                status_code=StatusCode.NOT_FOUND,
                status_message=StatusMessage.GETPATIENT_NOT_FOUND_SYSTEM                
            ),404

        response_data = Response.create(
            status_code=StatusCode.OK,
            status_message=StatusMessage.GETPATIENT_OK,
            data=patient_info
        )

        print(response_data)

        # Return the patient info as JSON
        return response_data, 200


@app.route('/')
def index():
    # Redirect to the '/home' route
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/404')
def notfuond():
    return render_template('404.html')


# Optional: Redirect any undefined route to /home
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('home')), 302

# Run the Flask app (expose on all network interfaces)
if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0', port=PORT)
