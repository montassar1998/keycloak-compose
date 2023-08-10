# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ../python_tools/client_generator/. /app

# Install the required dependencies
RUN pip install --no-cache-dir Flask faker

# Expose the port the app runs on
EXPOSE 5000

# Specify the entrypoint command to run the generator code
CMD ["python", "./cg.py"]
