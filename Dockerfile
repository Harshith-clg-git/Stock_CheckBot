FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install xvfb for virtual display
RUN apt-get update && apt-get install -y xvfb

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port for dummy web server (Render sets PORT environment variable)
EXPOSE 10000

# Start xvfb and run the main script
# xvfb-run creates a virtual X server so Playwright can run in headless=False
CMD xvfb-run --auto-servernum --server-args="-screen 0 1280x800x24" python main.py
