# Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy backend source
COPY backend/ .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose Flask default port
EXPOSE 4000

# Run the app
CMD ["python", "api.py"]
