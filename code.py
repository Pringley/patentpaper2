"""Patent citation network case study."""

import pandas
import networkx

def top(series, amount=5, ascending=False):
    """Return the top amount items from a series."""
    series = pandas.DataSeries(series)
    return series.order(ascending=ascending).head(amount).index

def top2d(frame, column, amount=5, ascending=False):
    """Return the top amount items from a data frame."""
    frame = pandas.DataFrame(frame)
    return frame.sort(ascending=ascending).head(amount).index

def read_graph(filename):
    """Read edgelist from tsv file, return a networkx.DiGraph."""
    frame = read_tsv(filename)
    clean_frame = frame.dropna() # ignore missing data
    edgelist = clean_frame.values.tolist()
    return networkx.DiGraph(edgelist)

def read_metadata(filenames, index_col='applnID'):
    """Read metadata from several files and return one pandas.DataFrame."""
    frames = [read_tsv(filename, index_col=index_col)
              for filename in filenames]
    joinframe = frames[0]
    for frame in frames[1:]:
        joinframe = joinframe.join(frame, how='outer', rsuffix='_dup')
    return joinframe

def read_tsv(filename, index_col=None):
    """Return a pandas.DataFrame of a tsv file."""
    return pandas.read_csv(filename,
                           delimiter='\t',
                           encoding='ISO-8859-1',
                           index_col=index_col,
                           dtype=object,
                           low_memory=False)

def test():
    """Run some basic tests."""
    graphfile = ('/Users/ben/Downloads/PatentNetworks/'
                 'citation pairs by applnID simple try '
                 'sorted by citing.txt')
    metafiles = ('/Users/ben/Downloads/PatentNetworks/'
                 'LEDs patents keyinfo.txt',
                 '/Users/ben/Downloads/PatentNetworks/'
                 'LEDs patents applicants longform.txt')
    graph = read_graph(graphfile)
    metadata = read_metadata(metafiles)
    print(graph.number_of_edges())
    print(metadata.columns)

if __name__ == '__main__':
    test()
