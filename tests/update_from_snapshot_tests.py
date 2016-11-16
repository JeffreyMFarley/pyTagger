import unittest
from tests import *


SANDBOX_DIRECTORY = os.path.join(RESULT_DIRECTORY, 'mp3s')


def setUpModule():
    if sampleFilesExist and not os.path.exists(SANDBOX_DIRECTORY):
        os.makedirs(SANDBOX_DIRECTORY)


def tearDownModule():
    if os.path.exists(SANDBOX_DIRECTORY):
        shutil.rmtree(SANDBOX_DIRECTORY)

if __name__ == '__main__':
    unittest.main()
