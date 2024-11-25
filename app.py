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
            "data": data or {}
        }
        # Add a timestamp to the response data
        response["data"]["created_at"] = datetime.now().isoformat()
        return response


base64 = "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"


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
    "stattusmessage": fields.String(description="Status message", example="Send Vitalsign Success."),
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
                "error": "Not Found Data",
                "processed_at": datetime.now().isoformat()}, 400

        try:
            response_data = {
                "statuscode":StatusCode.OK,
                "statusmessage": "Send Vitalsign Success.",
                "data":{
                    **input_data,
                    "created_at":datetime.now().isoformat()
                },
                "processed_at": datetime.now().isoformat()
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
    # @api.param('vn', 'Visit number (e.g., 1111, 2222)', required=True)
    # @api.param('hn', 'Hospital number (e.g., 3333, 4444)', required=True)
    @api.response(200, 'Transaction processed successfully')
    @api.response(400, 'Missing JSON data in the request body OR hn or vn query parameter')
    @api.response(404, 'Invalid hn or vn value')
    @api.response(500, 'Internal server error')
    def post(self):
        # Retrieve query parameters
        # hn = request.args.get('hn')
        # vn = request.args.get('vn')

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
                "statuscode":StatusCode.COMPLETED,
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
    @api.param('cid', 'The CID of the patient to retrieve information e.g 1111111111111 , 2222222222222', required=False)
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
            return {
                  "statuscode": StatusCode.NOT_FOUND,
                  "statusmessage": "not found hn or cid",
                  "data":""}, 404

        # Check if the CID exists in the mock data
        #patient_info = patients_data.get(cid)

        if cid:
            patient_info = patients_data_cid.get(str(cid) )
        elif hn:
            patient_info = patients_data_hn.get(str(hn))

        if not patient_info:
            return {
                  "statuscode": StatusCode.NOT_FOUND,
                  "statusmessage": "not found patient in system",
                  "data":"",
                  "processed_at": datetime.now().isoformat()}, 404


        response_data = {
                "statuscode":StatusCode.OK,
                "statusmessage": "Get Patient Success!",
                "data":patient_info,
                "processed_at": datetime.now().isoformat()
            }
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
