Basic Commands
=================

scan
----
After installing, the first thing you would probably want to do is scan a
directory of MP3s to extract their tags.  This can be done with:

.. code-block:: bash

   pyTagger scan path/to/mp3s

This will scan basic MP3 information about each file into a :term:`snapshot`

Several options are available to control the scanning.  These can be found by
running:

.. code-block:: bash

   pyTagger scan --help


*Related Code*

* :py:func:`pyTagger.actions.scan.process`
* :py:func:`pyTagger.models.Snapshot.columnsFromArgs`
* :py:func:`pyTagger.operations.hash.hashBuffer`
* :py:func:`pyTagger.operations.on_directory.buildSnapshot`
* :py:func:`pyTagger.operations.on_directory.walk`
* :py:func:`pyTagger.operations.on_directory.walkAll`
* :py:func:`pyTagger.proxies.id3.ID3Proxy.extractTags`
* :py:func:`pyTagger.proxies.id3.ID3Proxy.extractTagsFromTrack`
* :py:func:`pyTagger.proxies.id3.ID3Proxy.loadID3`

images
------
pyTagger not only extracts the ID3 information from MP3s, it can also extract
any embedded images from the files:

.. code-block:: bash

   pyTagger images path/to/mp3s path/to/where/images/are/stored

This command will extract any images from the MP3s found in the given path and
place them in the destination directory.

1. The name of the image files take the form ``<artist> - <album> - <title>``
2. If the image is the same for all MP3s in an album, only one image file will
   be extracted

*Related Code*

* :py:func:`pyTagger.actions.images.process`
* :py:func:`pyTagger.operations.hash.hashFile`
* :py:func:`pyTagger.operations.name.imageFileName`
* :py:func:`pyTagger.operations.on_directory.buildHashTable`
* :py:func:`pyTagger.operations.on_directory.extractImages`
* :py:func:`pyTagger.operations.on_mp3.extractImages`
* :py:func:`pyTagger.proxies.id3.ID3Proxy.extractImages`

rename
------
This command is used to apply (my) naming standards to a directory of MP3s

.. code-block:: bash

   pyTagger rename path/to/mp3s path/to/new/home

The naming format is: ``<artist:40>/<album:40>/<track> <title>``

*Related Code*

* :py:func:`pyTagger.actions.rename.process`
* :py:func:`pyTagger.operations.name.buildPath`
* :py:func:`pyTagger.operations.on_directory.needsMove`
* :py:func:`pyTagger.operations.on_directory.renameFiles`

to-csv
------
Without developer tools, it can be difficult to read or update :term:`snapshot`
files.  Often, it is more convenient to use Excel, or similar tools to view
the MP3 tags.

.. code-block:: bash

   pyTagger to-csv path/to/snapshot

This will convert the snapshot into a tabular format.

Several options are available to control the conversion.  These can be found by
running:

.. code-block:: bash

   pyTagger to-csv --help


*Related Code*

* :py:func:`pyTagger.actions.export.process`
* :py:func:`pyTagger.operations.to_csv.flattenOne`
* :py:func:`pyTagger.operations.to_csv.flattenSnapshot`
* :py:func:`pyTagger.operations.to_csv.listFlattenedColumns`
* :py:func:`pyTagger.operations.to_csv.writeCsv`

convert-csv
------------
Of course, if there is a way to create a tabular version of a snapshot, there
needs to be a way to convert back to the :term:`snapshot` format:

.. code-block:: bash

   pyTagger convert-csv path/to/csv

This will convert the tabular version into the pyTagger format.

Several options are available to control the conversion.  These can be found by
running:

.. code-block:: bash

   pyTagger convert-csv --help


*Related Code*

* :py:func:`pyTagger.actions.convert_csv.process`
* :py:func:`pyTagger.operations.from_csv.convert`

update
------
After changes have been made to a snapshot, either directly, or through the
CSV process, you can write the changes into the MP3 files with this command:

.. code-block:: bash

   pyTagger update path/to/snapshot

This will update the ID3 tags in the MP3 files.

Several options are available to control the updates.  These can be found by
running:

.. code-block:: bash

   pyTagger update --help


*Related Code*

* :py:func:`pyTagger.actions.update.process`
* :py:func:`pyTagger.operations.on_mp3.updateFromSnapshot`
* :py:func:`pyTagger.operations.on_mp3.updateOne`
* :py:func:`pyTagger.operations.two_tags.difference`
* :py:func:`pyTagger.proxies.id3.saveID3`

diff
----

where
-----
