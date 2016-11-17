

def buildArgParser():
    import argparse
    description = 'Update tag values in MP3s from a snapshot'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('infile', metavar='infile', help='the snapshot to process')
    p.add_argument('-b', '--basic', action='store_true', dest='basic',
                   help='Only update: ' + ' '.join(Snapshot.basic))
    p.add_argument('-s', '--songwriting', action='store_true',
                   dest='songwriting',
                   help='Only update: ' + ' '.join(Snapshot.songwriting))
    p.add_argument('-p', '--production', action='store_true',
                   dest='production',
                   help='Only update: ' + ' '.join(Snapshot.production))
    p.add_argument('-d', '--distribution', action='store_true',
                   dest='distribution',
                   help='Only update: ' + ' '.join(Snapshot.distribution))
    p.add_argument('-l', '--library', action='store_true', dest='library',
                   help='Only update: ' + ' '.join(Snapshot.library))
    p.add_argument('-a', '--all', action='store_true', dest='all',
                   help='include all supported fields')
    p.add_argument('--upgrade', action='store_true', dest='upgrade',
                   help='Upgrade the tags to be at least 2.3')

    return p
