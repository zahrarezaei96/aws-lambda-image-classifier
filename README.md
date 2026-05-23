# AWS Lambda Image Classifier — Performance & Scalability Analysis

> Cloud Computing Project | Sapienza University of Rome | A.Y. 2025/2026

A serverless AI-based image classification service deployed on **AWS Lambda**, evaluated under varying workload conditions (1–100 concurrent users). The application uses **MobileNetV2** (pre-trained on ImageNet) packaged as a Docker container image.

---

## Architecture

```
Client (Locust) → API Gateway (HTTP API) → AWS Lambda (MobileNetV2) → Response
                                                    ↑
                                              Amazon ECR
                                          (Docker container image)
```

**AWS Services used:**
- AWS Lambda (512 MB, 120s timeout, x86_64)
- Amazon ECR (container image registry)
- Amazon API Gateway (HTTP API)
- Amazon CloudWatch (monitoring & metrics)
- Amazon EC2 (Docker build environment only)

---

## Project Structure

```
├── lambda_function.py        # Lambda handler — MobileNetV2 inference
├── Dockerfile                # Container image definition
├── requirements.txt          # Python dependencies
├── locustfile.py             # Load testing script (Locust)
├── colab_image_classifier.ipynb  # Colab notebook for local testing
└── results/
    ├── performance_analysis.png
    ├── performance_table.png
    ├── per_image_size_analysis.png
    ├── cloudwatch_metrics.png
    └── cost_analysis.png
```

---

## Key Results

| Concurrent Users | RPS   | Median RT (ms) | Failure Rate |
|-----------------|-------|----------------|--------------|
| 1               | 0.36  | 570            | 0.00%        |
| 10              | 4.03  | 420            | 0.00%        |
| 25              | 9.90  | 420            | 0.00%        |
| 50              | 18.66 | 440            | 0.02%        |
| 100             | 30.81 | 530            | 0.02%        |

- **85.6× throughput increase** for 100× increase in concurrent users
- **Zero throttles** across all warm test levels (CloudWatch)
- Lambda auto-scaled from **1.00 to 10.70 concurrent executions**

---

## Cold Start Observation

| Metric | Cold (1st session) | Warm (2nd session) |
|--------|-------------------|-------------------|
| Failure rate @ 100 users | 15.7% | 0.02% |
| Median RT @ 100 users | 13,000 ms | 530 ms |

Failures began between **82–86 concurrent users** during cold start, caused by model weight loading latency (~87 MB MobileNetV2 weights).

---

## Setup & Deployment

### Prerequisites
- AWS CLI v2
- Docker
- Python 3.11+
- AWS account (or AWS Academy Learner Lab)

### 1. Build and push Docker image to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name image-classifier --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t image-classifier .

# Tag and push
docker tag image-classifier:latest \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/image-classifier:latest

docker push \
  <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/image-classifier:latest
```

### 2. Deploy Lambda

1. Go to AWS Lambda Console → **Create function** → **Container image**
2. Select the ECR image
3. Set memory: **512 MB**, timeout: **120 seconds**
4. Use existing role (e.g., `LabRole`)

### 3. Attach API Gateway

1. In Lambda → **Add trigger** → **API Gateway**
2. Select **HTTP API**, Security: **Open**
3. Note the endpoint URL

### 4. Test

```bash
curl -X POST <API_GATEWAY_URL>/default/image-classifier \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://images.dog.ceo/breeds/retriever-golden/n02099601_3004.jpg"}'
```

### 5. Load Testing

```bash
pip install locust pillow
python -m locust -f locustfile.py --host=<API_GATEWAY_URL>
# Open http://localhost:8089
```

---

## Cost Analysis (6-month estimate, us-east-1)

| Solution | 6-Month Total |
|----------|--------------|
| AWS Lambda (512 MB) + API GW | $284.47 |
| EC2 t2.small + API GW | $196.09 |
| EC2 t3.medium + API GW | $276.44 |

*Scenario: 50 concurrent users, 8 h/day, 180 days. Pricing from [AWS official documentation](https://aws.amazon.com/lambda/pricing/).*

---

## Tech Stack

![AWS Lambda](https://img.shields.io/badge/AWS_Lambda-FF9900?style=flat&logo=awslambda&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=flat&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)

---

## Author

**Zahra Rezaei** — Sapienza University of Rome
