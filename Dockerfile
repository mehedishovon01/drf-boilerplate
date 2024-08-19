# Use the official Python image from Docker Hub
FROM python:3.12-slim

# Set environment variables to avoid buffering and to set the working directory inside the container
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt /usr/src/app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . /usr/src/app/

# Create migrations 
ENTRYPOINT ["bash", "docker-entrypoint.sh"]

# Expose the application port
EXPOSE 8000

# Command to run the Django development server
CMD ["gunicorn", "--workers=3", "--timeout=120", "--bind 0.0.0.0:8000", "config.wsgi"]