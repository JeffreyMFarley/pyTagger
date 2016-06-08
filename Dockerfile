FROM jeffreymfarley/pytagger

# Copy over the local directory
ADD . /home/project
WORKDIR /home/project

# Run the tests
CMD ["python", "setup.py", "test"]