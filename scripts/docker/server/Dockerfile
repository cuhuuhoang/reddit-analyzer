FROM python:3.8-slim-bullseye
ENV TZ=Asia/Ho_Chi_Minh
RUN yes | cp -f /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


# Set the working directory
WORKDIR /app

ENV PYTHONPATH=/app
ENV SOURCE_DIR=/app

# Install pip package
RUN pip install --no-cache-dir pymongo flask

# Copy the necessary files to the container
COPY src /app/src
COPY scripts /app/scripts
COPY resources /app/resources

# Set the main command to run the submissions_main.py script
CMD python src/server/server.py
