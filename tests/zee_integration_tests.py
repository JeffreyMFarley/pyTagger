import unittest
import os
import json
import csv
import sys
import shutil
import unicodedata
import datetime
import uuid
import binascii
if sys.version < '3':
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: codecs.open(fileName, 'w', encoding='utf-8')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
    _output = lambda fileName: open(fileName, 'w', encoding='utf-8')
import pyTagger
from tests import *

INTEGRATION_TEST_DIRECTORY = os.path.join(
    RESULT_DIRECTORY, r'integration-test'
)


def walk(path):
    for currentDir, subdirs, files in os.walk(unicode(path)):
        # Get the absolute path of the currentDir parameter
        currentDir = os.path.abspath(currentDir)

        # Traverse through all files
        for fileName in files:
            fullPath = os.path.join(currentDir, fileName)
            yield fullPath


def setUpModule():
    if not os.path.exists(INTEGRATION_TEST_DIRECTORY):
        os.makedirs(INTEGRATION_TEST_DIRECTORY)

    for fullPath in walk(unicode(SOURCE_DIRECTORY)):
        if fullPath[-3:].lower() in ['mp3']:
            shutil.copy(fullPath, INTEGRATION_TEST_DIRECTORY)


def tearDownModule():
    shutil.rmtree(unicode(INTEGRATION_TEST_DIRECTORY))


class TestIntegration(unittest.TestCase):
    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_01_update(self):
        updateFile = os.path.join(RESULT_DIRECTORY, r'update.json')

        snapshot = {}
        stamp = datetime.date.today()
        for fullPath in walk(unicode(INTEGRATION_TEST_DIRECTORY)):
            id = uuid.uuid1()
            asString = binascii.b2a_base64(id.bytes).strip()
            snapshot[fullPath] = {
                'media': 'DIG',
                'ufid': {'DJTagger': asString},
                'comments': [{'lang': 'eng', 'text': '', 'description': ''},
                             {'lang': '', 'text': '', 'description': ''},
                             {'lang': 'eng', 'text': '',
                              'description': 'iTunes_CDDB_IDs'},
                             {'lang': 'eng', 'text': '',
                              'description': 'iTunNORM'},
                             {'lang': 'eng', 'text': '',
                              'description': 'iTunPGAP'},
                             {'lang': 'eng', 'text': '',
                              'description': 'iTunSMPB'},
                             ],
                'group': '',
                'subtitle': stamp.isoformat()
            }

        with _output(updateFile) as f:
            json.dump(snapshot, f, indent=2)

        target = pyTagger.UpdateFromSnapshot()
        target.update(updateFile, upgrade=True)

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_02_scan(self):
        target = pyTagger.Mp3Snapshot(False)
        columns = pyTagger.mp3_snapshot.Formatter.columns
        outFile = os.path.join(RESULT_DIRECTORY, r'snapshot.json')

        target.createFromScan(INTEGRATION_TEST_DIRECTORY, outFile, columns)
        assert os.path.getsize(outFile) > 0

    def test_03_convert(self):
        target = pyTagger.SnapshotConverter()
        inFile = os.path.join(RESULT_DIRECTORY, r'snapshot.json')
        outFile = os.path.join(RESULT_DIRECTORY, r'snapshot.txt')

        target.convert(inFile, outFile)
        assert os.path.getsize(outFile) > 0

    def test_04_convertBack(self):
        target = pyTagger.ConvertBack()
        inFile = os.path.join(RESULT_DIRECTORY, r'snapshot.txt')
        outFile = os.path.join(RESULT_DIRECTORY, r'snapshot2.json')

        target.convert(inFile, outFile)

        original = os.path.join(RESULT_DIRECTORY, r'snapshot.json')
        with _input(original) as f:
            a = json.load(f)
        with _input(outFile) as f:
            b = json.load(f)

        for path, tags in b.items():
            a_tags = a[path]
            for tag, value in tags.items():
                if not value:
                    assert tag not in a_tags or not a_tags[tag]
                else:
                    assert value == a_tags[tag]

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_05_extractAll(self):
        targetDir = os.path.join(RESULT_DIRECTORY, r'images')
        target = pyTagger.ExtractImages(targetDir)

        # Clear directory
        for name in os.listdir(targetDir):
            os.remove(os.path.join(targetDir, name))

        target.extractAll(INTEGRATION_TEST_DIRECTORY)

        files = [name for name in os.listdir(targetDir)]
        self.assertEqual(27, len(files))

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_06_rename(self):
        targetDir = os.path.join(RESULT_DIRECTORY, u'renamed', '')
        if os.path.exists(targetDir):
            shutil.rmtree(targetDir)

        target = pyTagger.Rename(targetDir)

        # Copy over files
        for f in walk(os.path.join(SOURCE_DIRECTORY, u'Checkin')):
            shutil.copy(f, targetDir)

        prepare = pyTagger.PrepareCheckIn()
        prepare.run(targetDir)
        target.run(targetDir)

        files = [name for name in os.listdir(targetDir)]
        self.assertEqual(7, len(files))

        expected = os.path.join(targetDir, 'Beck', 'Dreams', '01 Dreams.mp3')
        self.assertTrue(os.path.exists(expected))

    @unittest.skipUnless(sampleFilesExist, 'MP3 Files missing')
    def test_00_extractFromList(self):
        fileName = os.path.join(RESULT_DIRECTORY, 'extract_list.txt')
        with _output(fileName) as f:
            f.writelines([os.path.join(
                INTEGRATION_TEST_DIRECTORY, '01 Oh No.mp3'
            ), '\n'])
            f.writelines([os.path.join(
                INTEGRATION_TEST_DIRECTORY, '08 - Aeroplane.mp3'
            ), '\n'])

        targetDir = os.path.join(RESULT_DIRECTORY, r'some_images')
        target = pyTagger.ExtractImages(targetDir)
        target.extractFrom(fileName)

        files = [name for name in os.listdir(targetDir)]
        assert len(files) == 2

if __name__ == '__main__':
    unittest.main(failfast=True, exit=False)
