# 1. Use a lightweight, official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install necessary system-level utilities for network components
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Install your Python dependencies directly
RUN pip install --no-cache-dir \
    dnspython \
    requests \
    flask \
    flask-socketio \
    eventlet

# 5. Copy the current directory contents into the container at /app
COPY . .

# 6. Inform Docker that the container listens on these ports at runtime
EXPOSE 8081
EXPOSE 5353/udp

# 7. Run the script with unbuffered output so logs print to Docker instantly
CMD ["python3", "-u", "dns_server.py"]
