FROM jeffreymfarley/pytagger

RUN ["pip", "install", "eyed3", "nose", "python-coveralls"]

# Copy over the local directory
ADD . /home/project
WORKDIR /home/project

# Run the tests
CMD ["coverage", "run", "setup.py", "test"]