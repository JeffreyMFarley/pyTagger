import sys
import datetime

class ProgressBar:
    def __init__(self, count, title=None):
        self.total = count if not isinstance(count, (list, set, dict)) else len(count)
        self.value = 0
        self.bar = self.total / 20
        self.start = datetime.datetime.now()
        if title:
            sys.stderr.write(title)
            sys.stderr.write('\n')
        sys.stderr.write(' 1  2    5    7  9 |\n')
        sys.stderr.write('-0--5----0----5--0-|\n')
    
    def increment(self):
        self.value += 1
        if self.value > self.bar:
            sys.stderr.write('#')
            sys.stderr.flush()
            self.value = 0

    def finish(self):
        finish = datetime.datetime.now() - self.start
        sys.stderr.write('\n')
        sys.stderr.write('The operation took '+str(finish.total_seconds())+' seconds \n')


