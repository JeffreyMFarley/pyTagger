
def buildArgParser():
    description = 'Extract image from MP3 files'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('path',  nargs='?', metavar='path',
                   default=os.getcwd(),
                   help='the path to scan')
    p.add_argument('outputDir',  nargs='?', metavar='outputDir',
                   default=os.path.join(os.getcwd(), 'images'),
                   help='the directory where the extracted images are stored')
    p.add_argument('-f', '--use-file', dest='useFile',
                   metavar='filename',
                   help='a text file with the list of files to extract')

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    pipeline = ExtractImages(args.outputDir)
    pipeline.log.setLevel(logging.INFO)
    if args.useFile:
        pipeline.extractFrom(args.useFile)
    else:
        pipeline.extractAll(args.path)
