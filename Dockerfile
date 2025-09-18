FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libgtk-3-0 \
    libqt5gui5 \
    libqt5core5a \
    libqt5dbus5 \
    libqt5network5 \
    libqt5widgets5 \
    qt5-gtk-platformtheme \
    wget \
    && rm -rf /var/lib/apt/lists/*

ENV OPENCV_HEADLESS=1
ENV DISPLAY=""
ENV QT_QPA_PLATFORM=offscreen

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY app.yaml .

RUN mkdir -p /app/models

ENV FLASK_ENV=production
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "src.main:app"]
