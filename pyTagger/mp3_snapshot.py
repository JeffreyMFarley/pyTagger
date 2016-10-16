# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def buildArgParser():
    import argparse

    description = 'Scan directories and build a snapshot of the MP3s'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('path',  nargs='?', metavar='path',
                   default=os.getcwd(),
                   help='the path to scan')
    p.add_argument('--compact', action='store_true', dest='compact',
                   help='output the JSON in a compact format')

    return p

if __name__ == '__main__':
    from pyTagger.models import Snapshot

    parser = buildArgParser()
    args = parser.parse_args()

    columns = Snapshot.columnsFromArgs(args)
    pipeline = Mp3Snapshot(args.compact)
    pipeline.log.setLevel(logging.INFO)
    pipeline.createFromScan(args.path, args.outfile, list(set(columns)))
