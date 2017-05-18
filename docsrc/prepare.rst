The Prepare Process
===================

Overview
--------

Whenever I get new music via digital download, I like to process it so that
it is consistent with other files in my music library.

This code is specifically tuned to work on digital files downloaded from Amazon

For each of these steps, it is recommended that the configuration options
be stored in a ``config.ini`` file

Step 1
------

.. code-block:: bash

   pyTagger prepare 1

* Walk the download directory and for each file:

  * Remove "featuring xxx" from the title
  * Remove "[Explicit]" or "[Extended]" type of annotations from the album name
  * Add a tag that identifies the day this file was added to the library
  * Add a tag with a unique library identifier
  * Change the media tag to be "DIG"
  * Clear any existing comments
  * Clear the "group" tag

* Create a snapshot of the downloaded files
* Create a CSV version of the snapshot

Step 1.5
--------

* Review CSV file and make any additional changes

Step 2
------

.. code-block:: bash

   pyTagger prepare 2

* Convert the CSV back to the snapshot format
* Update the files with the additional changes
* Rename the files to conform with library standards

*Related Code*

* :py:func:`pyTagger.actions.prepare.process`
* :py:func:`pyTagger.operations.conform.LibraryStandard._expel`
* :py:func:`pyTagger.operations.conform.LibraryStandard.assignID`
* :py:func:`pyTagger.operations.conform.LibraryStandard.clearComments`
* :py:func:`pyTagger.operations.conform.LibraryStandard.clearMedia`
* :py:func:`pyTagger.operations.conform.LibraryStandard.clearRating`
* :py:func:`pyTagger.operations.conform.LibraryStandard.digitalMedia`
* :py:func:`pyTagger.operations.conform.LibraryStandard.extractArtist`
* :py:func:`pyTagger.operations.conform.LibraryStandard.processFile`
* :py:func:`pyTagger.operations.conform.LibraryStandard.removeAnnotations`
* :py:func:`pyTagger.operations.conform.LibraryStandard.timestamp`
* :py:func:`pyTagger.operations.on_directory.prepareForLibrary`
