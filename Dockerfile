FROM jeffreymfarley/pytagger

ENV SRC_HOME /home/project/

WORKDIR $SRC_HOME

ADD requirements.txt $SRC_HOME
RUN pip install -r requirements.txt

# Copy over the local directory
ADD . $SRC_HOME

# Run the tests
CMD ["coverage", "run", "setup.py", "test"]