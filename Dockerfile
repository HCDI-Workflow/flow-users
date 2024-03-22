# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /users


RUN apt-get update \
    && apt-get install -y apt-utils \
    && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*


# Copy the current directory contents into the container at /server
COPY . .

# Install any needed packages specified in requirements-notebook.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 9090

# Define environment variable
ENV FLASK_APP=.env.py
ENV GOOGLE_APPLICATION_CREDENTIALS=./certs/db-admin-key.json

# Run app.py when the container launches
CMD ["python", "src/server.py", "--host=0.0.0.0"]
