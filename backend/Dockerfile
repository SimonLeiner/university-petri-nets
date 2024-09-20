# If you have a Mac with an M1 (Apple Silicon) processor, you should use the ARM64 version of Docker images.
# arm64
# linux/amd64
# cvxopt not working on arm64

# install python 3.12 for platform linux/amd64
FROM --platform=linux/amd64 python:3.12

# set working directory
WORKDIR /workspace

# install git 
RUN apt-get update && apt-get install --no-install-recommends  -y \
    # graphviz
    graphviz \
    # github
    git \
    # for installing packages
    curl \
    # for interacting with remote servers
    openssh-client\
    # for psutil
    gcc python3-dev\
    # Java Runtime Environment
    openjdk-17-jdk \
    # clean up
    && apt-get clean\
    && rm -rf /var/lib/apt/lists/*

# copy and install requirments
COPY requirements.txt requirements.txt
RUN pip install -U -r requirements.txt

# setting up pre commit hooks
COPY .pre-commit-config.yaml .
RUN git init . && pre-commit install

# Expose the port FastAPI server will run on
EXPOSE 4000

# Command to run the FastAPI server
CMD ["uvicorn", "server:app", "--reload", "--host", "0.0.0.0", "--port", "4000"]
