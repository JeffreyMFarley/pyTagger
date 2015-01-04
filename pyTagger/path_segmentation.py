import posixpath
import ntpath
import sys

#-------------------------------------------------------------------------------
# Classes
#-------------------------------------------------------------------------------

class PathSegmentation():
    def __init__(self, pathSep):
        self.pathSep = pathSep

    def split(self, fullPath):
        if self.pathSep == '/':
            path, filename = posixpath.split(fullPath)
            result = {'fullPath': fullPath, 'directory': path, 'file': filename}
        else:
            drive, path = ntpath.splitdrive(fullPath)
            path, filename = ntpath.split(path)
            result = {'fullPath': fullPath, 'drive': drive, 'directory': ntpath.join(drive, path), 'file': filename}
   
        dirSplit = path.split(self.pathSep)
        if len(dirSplit) > 2:
            lastTwoSubdir = dirSplit[-2:]
            headSubdir = dirSplit[:len(dirSplit) - 2]

            result['root'] = self.pathSep.join(headSubdir)
            result['subdir'] = self.pathSep.join(lastTwoSubdir)

        return result

    def join(self, parts):
        pass

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print('this is intended to be used as a helper class and not a free-executing script')

