import base64
import requests

# URL of the image
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/NonFreeImageRemoved.svg/640px-NonFreeImageRemoved.svg.png"

# Download the image
response = requests.get(image_url)

if response.status_code == 200:
    # Convert the image to base64
    image_base64 = base64.b64encode(response.content).decode('utf-8')
    print(image_base64)  # Print the base64 string
else:
    print("Failed to retrieve the image.")
