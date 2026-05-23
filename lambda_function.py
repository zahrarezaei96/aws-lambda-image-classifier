import json
import base64
import torch
import torchvision.transforms as transforms
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
from PIL import Image
from io import BytesIO
import requests
import os

os.environ["TORCH_HOME"] = "/tmp"

print("Cold start: loading model...")
weights = MobileNet_V2_Weights.IMAGENET1K_V1
model = mobilenet_v2(weights=weights)
model.eval()
categories = weights.meta["categories"]

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

def lambda_handler(event, context):
    try:
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        elif isinstance(event.get("body"), dict):
            body = event["body"]
        else:
            body = event

        if "image_url" in body:
            resp = requests.get(body["image_url"], timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            img = Image.open(BytesIO(resp.content)).convert("RGB")
        elif "image_b64" in body:
            img_bytes = base64.b64decode(body["image_b64"])
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Provide image_url or image_b64"})}

        input_tensor = preprocess(img).unsqueeze(0)
        with torch.no_grad():
            output = model(input_tensor)

        probs = torch.nn.functional.softmax(output[0], dim=0)
        top5_prob, top5_idx = torch.topk(probs, 5)

        predictions = [
            {"label": categories[idx], "confidence": round(p.item() * 100, 2)}
            for p, idx in zip(top5_prob, top5_idx)
        ]

        return {
            "statusCode": 200,
            "body": json.dumps({"predictions": predictions, "model": "MobileNetV2"})
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
