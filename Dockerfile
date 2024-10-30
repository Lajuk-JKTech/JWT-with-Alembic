FROM python:3.11

# Set work directory
WORKDIR /usr/srv

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install PostgreSQL client utilities for `pg_isready`
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

RUN useradd -rm -d /code -s /bin/bash -g root -G sudo -u 1001 ubuntu

# Copy requirements file and install dependencies
COPY ./requirements.txt /usr/srv/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application files, including run_migrations.sh
COPY . .

# Ensure the migration script is executable
RUN chmod +x /usr/srv/run_migrations.sh

# Switch to non-root user
USER ubuntu

# Expose FastAPI port
EXPOSE 8000

# Update ENTRYPOINT to explicitly use `sh`
ENTRYPOINT ["sh", "/usr/srv/run_migrations.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
