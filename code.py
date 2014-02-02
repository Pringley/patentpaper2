"""Patent citation network case study."""

import scipy.stats
import pandas
import networkx
import matplotlib.pyplot as plt
import collections

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

def unique_sets(dct):
    """Given a dict of iterables, return unique elements in each."""
    result = {}
    for key, category in dct.items():
        remaining = dct.copy()
        del remaining[key]
        all_others = set()
        for others in remaining.values():
            all_others |= set(others)
        result[key] = set(category) - all_others
    return result

def analyze_indegree(graph, show_table=False, show_plot=False):
    """Run analysis on indegree."""
    indegrees = pandas.Series(graph.in_degree(), name='indegree')
    if show_table:
        print('There are {} nodes with indegree <5.'
                .format(len(indegrees[indegrees < 5].values)))
        print('There are {} nodes with indegree <10.'
                .format(len(indegrees[indegrees < 10].values)))
        print('There are {} nodes with indegree <50.'
                .format(len(indegrees[indegrees < 50].values)))
        print('There are {} nodes with indegree >99.'
                .format(len(indegrees[indegrees > 99].values)))
    if show_plot:
        hist = indegrees[indegrees < 50].hist()
        hist.set_title('Histogram of indegrees (<50)')
        hist.set_ylabel('Number of patents')
        hist.set_xlabel('Indegree')
        plt.show()

def analyze_pagerank(graph, show_table=False, show_plot=False):
    """Run analysis on pagerank."""
    if not (show_table or show_plot):
        return # expensive computation, skip if unneccessary
    indegrees = pandas.Series(graph.in_degree(), name='indegree')
    pagerank = pandas.Series(networkx.pagerank_scipy(graph, max_iter=200),
            name='pagescore')
    table = (pandas.DataFrame({'indegree': graph.in_degree()})
                   .sort(columns='indegree', ascending=False))
    table['indegree_rank'] = pandas.Series(range(1, len(table)+1),
                                           index=table.index)
    table = table.join(pagerank).sort(columns='pagescore',
            ascending=False)
    table['page_rank'] = pandas.Series(range(1, len(table)+1),
                                       index=table.index)
    slope, intercept, r_val, p_val, stderr = scipy.stats.linregress(
            table['pagescore'], table['indegree'])
    if show_table:
        print('pagescore and indegree have r == {}'.format(r_val))
        print(table.head(10))

def big_companies(graph, metadata, show_table=False):
    """Compute the big companies."""
    ingraph = pandas.Series({
        applnID: str(int(applnID)) in graph
        for applnID in metadata.index
    }, name='ingraph')
    metadata = metadata.join(ingraph)
    companies = (metadata[metadata['ingraph'] == True]['appMyName']
                    .dropna())
    patents = pandas.DataFrame({
        'patents': collections.Counter(companies.values)
    })
    if show_table:
        print('{}/{} ({}) nodes with company metadata'
                .format(len(companies),
                    graph.number_of_nodes(),
                    len(companies) / graph.number_of_nodes()))
        print(patents.sort(columns='patents', ascending=False)
                .head(10))

def visualize_cluster(graph, index=1, show_plot=False):
    """Display visualizations for clusters."""
    indegrees = pandas.Series(graph.in_degree(), name='indegree')
    high_indegrees = indegrees.order().tail(10).index # top 10
    nhoods = neighborhood(graph, high_indegrees)
    root = high_indegrees[-index]
    cluster = networkx.subgraph(graph, nhoods[root])
    if show_plot:
        nodelist = cluster.nodes()
        cluster_indg = [cluster.in_degree(node) for node in nodelist]
        pos = networkx.spring_layout(cluster, k=.2, iterations=500)
        fig = networkx.draw_networkx_edges(cluster, pos,
                width=.7,
                alpha=.7)
        fig = networkx.draw_networkx_nodes(cluster, pos,
                node_size=50,
                node_color=cluster_indg,
                vmin=min(cluster_indg),
                vmax=max(cluster_indg),
                nodelist=nodelist)
        plt.show()

def analyze_nhood_overlap(graph, show_table=False, show_plot=False):
    """Run analysis about neighborhood overlaps."""
    indegrees = pandas.Series(graph.in_degree(), name='indegree')
    high_indegrees = indegrees.order().tail(10).index # top 10
    nhoods = neighborhood(graph, high_indegrees)
    bignodes = pandas.Series({
        node: len(set(high_indegrees) & set(nhood))
        for node, nhood in nhoods.items()
    }, name='bignodes')
    unique_nhoods = unique_sets(nhoods)
    unique_factors = pandas.Series({
        node: len(unique_nhoods[node]) / len(nhoods[node])
        for node in nhoods
    }, name='percentunique')
    if show_table:
        table = pandas.DataFrame(indegrees)
        print(table.join(unique_factors, how='right')
                   .join(bignodes)
                   .sort(columns='indegree', ascending=False))

def analyze_nhood_size(graph, show_table=False, show_plot=False):
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
    print('Nodes', graph.number_of_nodes())
    print('Edges', graph.number_of_edges())

    # Analyses
    big_companies(graph, metadata, show_table=True)
    visualize_cluster(graph, index=1, show_plot=False)
    visualize_cluster(graph, index=5, show_plot=False)
    analyze_pagerank(graph, show_table=False, show_plot=False)
    analyze_indegree(graph, show_table=False, show_plot=False)
    analyze_nhood_overlap(graph, show_table=False)
    analyze_nhood_size(graph, show_table=False, show_plot=False)

if __name__ == '__main__':
    test()
