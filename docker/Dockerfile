FROM jupyter/pyspark-notebook:latest

USER root

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# Install TensorFlow and other data science libraries
RUN pip install --quiet --no-cache-dir \
    tensorflow \
    psycopg2-binary \
    matplotlib \
    pandas \
    seaborn

# Environment variables for Spark
ENV SPARK_OPTS="--driver-java-options=-Dlog4j.logLevel=info"
