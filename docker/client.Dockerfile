# Use a slim version of Python 3.9
FROM python:3.9-slim

# Create and set working directory
WORKDIR /app

# Copy the Python script to the image
COPY ./python_tools/client/* /app

# Install necessary dependencies
RUN pip install keycloak

# Set the command to run the client script by default
CMD ["python", "./main.py"]
