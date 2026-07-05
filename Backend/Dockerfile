# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the backend code into the container
COPY . .

# Expose the port your backend runs on (assuming 8000 for FastAPI/Flask)
EXPOSE 8000

# Command to run your app (Change 'app.py' to 'main.py' if that is your entry point)
CMD ["python", "app.py"]