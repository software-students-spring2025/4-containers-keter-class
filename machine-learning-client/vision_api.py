from google.cloud import vision
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="client_secrets.json"

client = vision.ImageAnnotatorClient()

#FILE_NAME = 'card1.png'
FILE_PATH = r'Images\card1.png'

def detect_text(path):
    """Detects text in the file."""

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print("Texts:")

    for text in texts:
        print(f'\n"{text.description}"')

        vertices = [
            f"({vertex.x},{vertex.y})" for vertex in text.bounding_poly.vertices
        ]

        print("bounds: {}".format(",".join(vertices)))

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

detect_text(FILE_PATH)