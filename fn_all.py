import uuid
import random



def generate_id():
    # Generate a 24-character hexadecimal ID
    unique_id = uuid.uuid4().hex[:24]
    return unique_id

def genNumber(num =6):

   return ''.join(str(random.randint(0, 9)) for _ in range(num))


def is_valid_idcard(idcard):
    # Check if the ID card is exactly 13 digits and all are numbers
    if len(idcard) != 13 or not idcard.isdigit():
        return False

    # Calculate the checksum
    total = sum(int(idcard[i]) * (13 - i) for i in range(12))
    check_digit = (11 - (total % 11)) % 10

    # Compare the calculated check digit to the last digit of the ID card
    return check_digit == int(idcard[-1])