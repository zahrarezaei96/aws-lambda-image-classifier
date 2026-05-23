from locust import HttpUser, task, between
import json
import base64
import requests
from PIL import Image
from io import BytesIO

def get_resized_b64(url, size):
    """Download and resize image, return as base64 string"""
    resp = requests.get(url)
    img = Image.open(BytesIO(resp.content)).convert("RGB")
    img = img.resize(size)
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

URL = "https://images.dog.ceo/breeds/retriever-golden/n02099601_3004.jpg"

print("Preparing images...")
small_b64  = get_resized_b64(URL, (64, 64))    # ~3 KB
medium_b64 = get_resized_b64(URL, (224, 224))  # ~30 KB
large_b64  = get_resized_b64(URL, (800, 800))  # ~200 KB
print("Images ready!")

class ImageClassifierUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def classify_small(self):
        self.client.post(
            "/default/image-classifier",
            json={"image_b64": small_b64},
            name="small_64x64"
        )

    @task(2)
    def classify_medium(self):
        self.client.post(
            "/default/image-classifier",
            json={"image_b64": medium_b64},
            name="medium_224x224"
        )

    @task(1)
    def classify_large(self):
        self.client.post(
            "/default/image-classifier",
            json={"image_b64": large_b64},
            name="large_800x800"
        )
