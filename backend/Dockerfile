# Step 1: Use a base Python image
FROM python:3.9-slim

# Step 2: Set the working directory
WORKDIR /app

# Step 3: Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the app files into the container
COPY . /app/

# Step 5: Expose the port the app will run on
EXPOSE 5000

# Step 6: Run the Flask app
CMD ["python", "backend.py"]
