FROM apache/airflow:2.5.0

# env
ENV TZ=Asia/Ho_Chi_Minh
ENV DEBIAN_FRONTEND=noninteractive
ENV SPARK_HOME=/content/spark-3.3.2-bin-hadoop3
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV SHELL=/bin/bash

USER root

# pkgs
RUN apt-get update && apt-get install -y --no-install-recommends gcc wget jq

# spark
RUN wget -qO "/opt/spark-bin-hadoop3.tgz" "https://downloads.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz" && \
    tar xf "/opt/spark-bin-hadoop3.tgz" -C "/opt/" && mv "/opt/spark-3.3.2-bin-hadoop3" "/opt/spark-bin-hadoop3"
RUN mkdir -p /content && ln -sfn "/opt/spark-bin-hadoop3" "$SPARK_HOME"

# java
COPY --from=adoptopenjdk/openjdk8:jdk8u-debianslim-nightly /opt/java/openjdk "$JAVA_HOME"

# mongo tool
RUN wget https://downloads.mongodb.com/compass/mongodb-mongosh_1.10.1_amd64.deb -O /tmp/mongodb-mongosh_amd64.deb
RUN dpkg -i /tmp/mongodb-mongosh_amd64.deb
RUN wget https://fastdl.mongodb.org/tools/db/mongodb-database-tools-debian11-x86_64-100.7.3.deb -O /tmp/mongodb-database-tools.deb
RUN dpkg -i /tmp/mongodb-database-tools.deb

# jupiter notebook
USER airflow
RUN pip install --no-cache-dir jupyter-core jupyter requests \
    boto3 awscli apache-airflow-providers-apache-spark pyspark findspark \
    praw pymongo spacy nltk apache-airflow-providers-mongo
RUN echo 'export PS1="\[\033[01;32m\]\u\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "' >> /home/airflow/.bash_profile
RUN echo "export PATH='$PATH'" >> /home/airflow/.bash_profile

USER root
RUN chmod -R 775 /home/airflow/.local/share/jupyter

# jupyter
COPY scripts/docker/airflow/jupyter /app/

# entrypoint
COPY scripts/docker/airflow/entrypoint /entrypoint


