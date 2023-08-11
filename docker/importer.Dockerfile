# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./python_tools/importer/* /app

# Install the required dependencies
RUN pip install --no-cache-dir requests 
RUN pip install --no-cache-dir python-keycloak
RUN pip install --no-cache-dir pip install Flask-OIDC


# Specify the entrypoint command to run the importer code
CMD ["python", "./importer.py"]
