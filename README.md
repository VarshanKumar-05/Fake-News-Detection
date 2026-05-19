# Nexus Fake News AI Dashboard 🚨
*Complete DevOps & MLOps Transformation*

## Project Overview
A complete, professional AI-powered Fake News Detection web application. This project leverages state-of-the-art NLP models (DistilBERT) and a futuristic Streamlit interface. It has been transformed into a **Complete Industry-Level DevOps Project** featuring Docker containerization, Git LFS for large model storage, GitHub Actions for CI/CD, and AWS EC2 deployment.

---

## 🏗️ DevOps Architecture & Workflow

This project follows a professional DevOps lifecycle:

```text
Developer (Code + Git LFS for Models)
   ↓
GitHub Repository (Version Control)
   ↓
GitHub Actions CI/CD (Automated Build & Test Pipeline)
   ↓
Docker Image (Containerized Application)
   ↓
AWS EC2 Deployment (Cloud Infrastructure)
   ↓
Live AI Fake News Detection Application
```

---

## 🛠️ Phase 1: Local Docker Setup & Run

We use Docker to containerize the application, ensuring it runs identically across all environments.

### 1. Build the Docker Image
Open Windows PowerShell in the project directory and run:
```powershell
# Build the Docker image from the Dockerfile
docker build -t fake-news-app .
```

### 2. Run the Docker Container
```powershell
# Run the container, mapping port 8501
docker run -d -p 8501:8501 --name fake-news-detector fake-news-app
```

Alternatively, use **Docker Compose** for easier management:
```powershell
# Start the application in the background
docker-compose up -d

# Stop the application
docker-compose down
```

The application will be available at `http://localhost:8501`.

---

## 📦 Phase 2: Git LFS (Large File Storage)

Machine learning models (like DistilBERT's `.safetensors` or `.bin`) and datasets (`.csv`) are too large for standard Git (GitHub has a 100MB limit). We use Git LFS.

### Step-by-Step Setup
1. Download and install [Git LFS](https://git-lfs.github.com/).
2. Initialize Git LFS in Windows PowerShell:
   ```powershell
   git lfs install
   ```
3. The `.gitattributes` file is already configured in this repo to track large files:
   ```powershell
   # If you need to manually track a new large file extension:
   git lfs track "*.pth"
   git lfs track "*.csv"
   ```
4. Add, commit, and push normally. Git LFS handles the large files in the background:
   ```powershell
   git add .
   git commit -m "Add large ML models via Git LFS"
   git push origin main
   ```

---

## ⚙️ Phase 3: GitHub Actions CI/CD

This project includes a continuous integration pipeline (`.github/workflows/ci-cd.yml`).
Every time code is pushed to the `main` branch, GitHub Actions automatically:
1. Clones the repository and pulls large models via Git LFS.
2. Sets up Python 3.9.
3. Installs dependencies to validate `requirements.txt`.
4. Builds the Docker image to ensure the environment is pristine and deployment-ready.

---

## ☁️ Phase 4: AWS EC2 Deployment Guide

Follow these steps to deploy the application on AWS EC2.

### 1. Launch EC2 Instance
- Log into AWS Console -> EC2 -> **Launch Instance**.
- Name: `Fake-News-Server`.
- OS: **Ubuntu 22.04 LTS**.
- Instance Type: **t3.medium** (Recommended for ML models) or `t2.micro` (Free tier, but might be slow/run out of memory).
- Create and download a new Key Pair (`.pem` file).

### 2. Configure Security Group
In the EC2 Network Settings, add these Inbound Rules:
- **SSH (Port 22)**: Source `My IP` (for terminal access).
- **Custom TCP (Port 8501)**: Source `Anywhere - IPv4` (0.0.0.0/0) (For Streamlit access).

### 3. Connect via SSH (Windows PowerShell)
```powershell
ssh -i "your-key.pem" ubuntu@<your-ec2-public-ip>
```

### 4. Install Docker and Git LFS on EC2
Run these commands inside the EC2 terminal:
```bash
# Update system
sudo apt-get update -y

# Install Docker
sudo apt-get install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# Install Git LFS
sudo apt-get install git-lfs -y
git lfs install
```
*(Tip: Disconnect and reconnect SSH for the Docker group permission to take effect).*

### 5. Clone, Build, and Run
```bash
# Clone the repository
git clone https://github.com/VarshanKumar-05/Fake-News-Detection.git
cd Fake-News-Detection

# Build Docker image
docker build -t fake-news-app .

# Run Docker container
docker run -d -p 8501:8501 --name fake-news-detector fake-news-app
```

### 6. Access the App
Open your browser and visit: `http://<your-ec2-public-ip>:8501`

---

## 🎓 Presentation / Viva Preparation Support

Use this section to prepare for academic or professional interviews.

### Q: Why did you use Docker for an ML project?
**A:** Machine Learning projects often face "it works on my machine" issues due to complex dependency trees (like PyTorch, Transformers). Docker containerizes the application, ensuring that the exact same environment (OS, Python version, libraries) is replicated across development, testing, and production (AWS), eliminating dependency conflicts.

### Q: How did you handle GitHub's 100MB file size limit for your ML models?
**A:** I implemented **Git LFS (Large File Storage)**. Instead of pushing massive `.safetensors` or `.csv` files directly to the Git repository, Git LFS replaces them with lightweight text pointers inside Git, while storing the actual large files on a remote server. The `.gitattributes` file manages this tracking.

### Q: Can you explain your CI/CD Pipeline?
**A:** I used **GitHub Actions**. The pipeline defined in `ci-cd.yml` triggers on every push to the `main` branch. It automates the testing phase by checking out the code, setting up Python, installing requirements, and building the Docker image. If any dependency is broken or the Dockerfile is faulty, the pipeline fails, preventing broken code from reaching production.

### Q: Why did you open port 8501 in AWS Security Groups?
**A:** Streamlit, the framework used for the web interface, runs on port 8501 by default. The Security Group acts as a virtual firewall for the EC2 instance. By opening inbound port 8501 to `0.0.0.0/0`, I allow global internet traffic to access the Streamlit web dashboard.

### Q: How did you optimize the Docker container?
**A:** I used a lightweight base image (`python:3.9-slim`), prevented Python from writing unnecessary byte-code (`PYTHONDONTWRITEBYTECODE=1`), used the `--no-cache-dir` flag in pip to avoid storing downloaded packages, and utilized a `.dockerignore` file to prevent copying unnecessary local files (like `.git` and `__pycache__`) into the image.

---

## 🔮 Future Improvements
- **Kubernetes (EKS)**: To handle massive traffic, orchestrate multiple Docker containers using AWS EKS for auto-scaling.
- **Monitoring (Prometheus/Grafana)**: Implement monitoring to track model inference times and system resource utilization on EC2.
