# Use an official Python runtime as a parent image
FROM python:3.10

# Environment settings
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and clean up in one layer
RUN apt-get update && \
    apt-get install -y netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Add wait-for-it script (assuming it's in the same directory as the Dockerfile)
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Create a non-root user for security purposes
RUN useradd -m myuser -s /bin/bash  # Ensure the user has a standard shell
USER myuser

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run the application
CMD ["/usr/local/bin/wait-for-it.sh", "db", "3306", "30", "2", "--", "python", "manage.py", "runserver", "0.0.0.0:8000"]
