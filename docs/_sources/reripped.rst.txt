The Reripping Process
=====================

Overview
--------

I have a lot of CDs.  I started ripping my CD collection almost as soon as the
technology was available.  This was a good thing at the time for carrying
around my music collection, but eventually I was dealing with a backlog of poor
quality (96kbps) MP3s.

Part of the reason I created pyTagger was to help with the process of replacing
ripped CDs in my collection with newer, higher quality rips.

For each of these steps, it is recommended that the ~20 configuration options
be stored in a ``config.ini`` file

Step 1
------

.. code-block:: bash

   pyTagger reripped 1

* Push the snapshot of the entire library to Elasticsearch
* Using a snapshot of the reripped files, see if they are referenced in the
  library
* Build an interview to resolve any collisions or missing files
* Conduct the interview
* Edit the album tags
* Create a CSV version of the results to review

Step 1.5
--------

* Review the CSV file and make any additional edits

Step 2
------
.. code-block:: bash

   pyTagger reripped 2

* Using the output from Step 2 to create a goal snapshot
* Build a list of files to delete
* Build a list of new files that will be moved to the library
* Build a list of files that will be replaced in the library
* Write the updated tags to the intake version of the MP3s
* Extract the images from the current library files

Step 2.5
--------

* Determine if there are any better versions of the extracted images
* Add the images to the newer version of the MP3 files

Step 3
------
.. code-block:: bash

   pyTagger reripped 3

* Delete files
* Move files
* Replace files
* Delete empty directories from the intake directory

*Related Code*

* :py:func:`pyTagger.actions.reripped.process`
