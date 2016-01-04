FROM alpine

RUN apk add --update python py-pip ca-certificates

# Add the Sample Data
ADD https://github.com/JeffreyMFarley/pyTagger/releases/download/v0.1-alpha/sample-data.tar.gz /var/tmp/
WORKDIR /
RUN ["tar", "-zxvf", "/var/tmp/sample-data.tar.gz"]

# Copy over the local directory
ADD . /home/project
WORKDIR /home/project

# Run the tests
CMD ["python", "setup.py", "test"]