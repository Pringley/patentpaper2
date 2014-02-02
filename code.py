"""Patent citation network case study."""

import pandas
import networkx
import matplotlib.pyplot as plt

def neighborhood(graph, nbunch, depth=1, closed=False):
    """Return the neighborhood of a node or nodes."""
    if nbunch in graph:
        return next(neighborhood_iter(graph, nbunch, depth))[1]
    else:
        return dict(neighborhood_iter(graph, nbunch, depth))

def neighborhood_iter(graph, nbunch=None, depth=1, closed=False):
    """Return the neighborhood of a node or nodes as an iterator."""
    if nbunch is None:
        nbunch = graph.nodes()
    for root in graph.nbunch_iter(nbunch):
        nhood = set([root])
        for _ in range(depth):
            for node in nhood.copy():
                nhood |= set(graph.predecessors(node))
        if not closed:
            nhood.remove(root)
        yield root, nhood

def histogram(dct):
    """Return a Series of the lengths of dct's values, indexed by key."""
    return pandas.Series({key: len(val) for key, val in dct.items()})

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

def annotate_graph(graph, metadata):
    """Annotate graph with metadata fields."""
    for column, series in metadata.iteritems():
        clean_series = series.dropna() # ignore missing data
        for index, value in clean_series.iteritems():
            if index not in graph:
                continue # ignore nodes not in graph
            graph.node[index][column] = value

def read_tsv(filename, index_col=None):
    """Return a pandas.DataFrame of a tsv file."""
    return pandas.read_csv(filename,
                           delimiter='\t',
                           encoding='ISO-8859-1',
                           index_col=index_col,
                           dtype=object,
                           low_memory=False)

def analyze_neighborhoods(graph, show_table=False, show_plot=False):
    """Run analysis about neighborhood sizes."""
    indegrees = pandas.Series(graph.in_degree(), name='indegree')
    high_indegrees = indegrees.order().tail(20).index # top 20
    nhoods = {
        depth: neighborhood(graph, high_indegrees, depth)
        for depth in range(1, 4)
    }
    nhood_hists = pandas.DataFrame({
        '{}-nhood'.format(depth): histogram(nhood)
        for depth, nhood in nhoods.items()
    }).join(indegrees).sort(columns='indegree', ascending=False)
    if show_table:
        print(nhood_hists)
    if show_plot:
        del nhood_hists['indegree']
        nhood_hists.index = range(20)
        nhood_fig = nhood_hists.plot()
        nhood_fig.set_title('N-neighborhood sizes for top indegree nodes')
        nhood_fig.set_ylabel('Neighborhood size')
        nhood_fig.set_xlabel('Node (sorted by highest indegree)')
        plt.show()

def test():
    """Run some basic tests."""
    graphfile = ('/Users/ben/Downloads/PatentNetworks/'
                 'citation pairs by applnID simple try '
                 'sorted by citing.txt')
    metafiles = ('/Users/ben/Downloads/PatentNetworks/'
                 'LEDs patents keyinfo.txt',
                 '/Users/ben/Downloads/PatentNetworks/'
                 'LEDs patents applicants longform.txt')
    print('Loading data...', end='', flush=True)
    graph = read_graph(graphfile)
    metadata = read_metadata(metafiles)
    annotate_graph(graph, metadata)
    print('done.')

    # Analyses
    analyze_neighborhoods(graph, show_table=True, show_plot=False)

if __name__ == '__main__':
    test()
