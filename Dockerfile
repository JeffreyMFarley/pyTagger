FROM alpine

RUN apk add --update python py-pip ca-certificates

# Copy over the local directory
ADD . /home/project
WORKDIR /home/project

# Run the tests
CMD ["python", "setup.py", "test"]