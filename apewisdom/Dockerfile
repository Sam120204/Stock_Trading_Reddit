# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN pip install --upgrade pip

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Streamlit app
COPY . /app
WORKDIR /app

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app.py"]
CMD ["--server.port", "8080", "--server.enableCORS", "false"]
