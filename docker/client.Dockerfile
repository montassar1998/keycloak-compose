# Use a slim version of Python 3.9
FROM python:3.9-slim

# Create and set working directory
WORKDIR /app

# Copy the Python script to the image
COPY ./python_tools/client/* /app

# Install necessary dependencies
RUN pip install --upgrade --no-cache-dir requests flask 
EXPOSE 5002
# Set the command to run the client script by default
CMD ["python", "./client.py"]
