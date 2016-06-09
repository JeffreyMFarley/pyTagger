FROM jeffreymfarley/pytagger

RUN ["pip", "install", "eyed3", "nose"]

# Copy over the local directory
ADD . /home/project
WORKDIR /home/project

# Run the tests
CMD ["python", "setup.py", "test"]