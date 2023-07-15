FROM apache/airflow:2.5.0

# env
ENV DEBIAN_FRONTEND=noninteractive
ENV SPARK_HOME=/content/spark-3.3.2-bin-hadoop3
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV SHELL=/bin/bash

USER root

# pkgs
RUN apt-get update && apt-get install -y wget

# spark
RUN wget -qO "/opt/spark-bin-hadoop3.tgz" "https://downloads.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz" && \
    tar xf "/opt/spark-bin-hadoop3.tgz" -C "/opt/" && mv "/opt/spark-3.3.2-bin-hadoop3" "/opt/spark-bin-hadoop3"
RUN mkdir -p /content && ln -sfn "/opt/spark-bin-hadoop3" "$SPARK_HOME"

# jupiter notebook
USER airflow
RUN pip install -U --no-cache-dir --user jupyter-core jupyter requests boto3 awscli apache-airflow-providers-apache-spark pyspark
RUN echo 'export PS1="\[\033[01;32m\]\u\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> /home/airflow/.bash_profile
RUN echo "export PATH='$PATH'" >> /home/airflow/.bash_profile

USER root
RUN chmod -R 775 /home/airflow/.local/share/jupyter

# jupyter
COPY scripts/docker/airflow/jupyter /app/

# entrypoint
COPY scripts/docker/airflow/entrypoint /entrypoint


