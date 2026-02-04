FROM mcr.microsoft.com/playwright/python:v1.55.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install any required system packages
RUN apt-get update && apt-get install -y ffmpeg libgl1 && apt-get clean

CMD ["bash"]
