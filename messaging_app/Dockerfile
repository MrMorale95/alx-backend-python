# messaging_app/Dockerfile

# 1. Use official Python base image
FROM python:3.10-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set work directory inside container
WORKDIR /app

# 4. Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 5. Copy entire app into container
COPY . .

# 6. Expose port 8000
EXPOSE 8000

# 7. Default command to run app (update this if you use gunicorn etc.)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
