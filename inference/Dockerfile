FROM python:3.11-slim

# Install as root
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user and switch to it
RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app

# Copy rest of the app (own it to user)
COPY --chown=user . .

# Run app as user
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]