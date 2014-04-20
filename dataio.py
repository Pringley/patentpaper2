"""Patent citation network case study."""

import os
import os.path
import time
import pickle
import contextlib
import collections

import scipy.stats
import pandas
import networkx
import matplotlib.pyplot as plt
import redis

_graph = None
_metadata = None

def graph():
    global _graph
    if _graph is None:
        load_graph_and_metadata()
    return _graph

def metadata():
    global _metadata
    if _metadata is None:
        load_graph_and_metadata()
    return _metadata

def load_graph_and_metadata():
    redis_read = os.environ.get('PATENT_REDIS_READ', True)
    redis_write = os.environ.get('PATENT_REDIS_WRITE', True)
    redis_host = os.environ.get('REDIS_HOST', 'localhost')
    redis_port = os.environ.get('REDIS_PORT', 6379)
    redis_prefix = os.environ.get('PATENT_REDIS_PREFIX', 'patentdata:')

    # Attempt to connect to Redis server.
    try:
        rc = redis.StrictRedis(host=redis_host, port=redis_port,
                               socket_timeout=2)
    except redis.ConnectionError:
        print('Could not connect to Redis instance at {}:{}. '
              'Caching disabled.'.format(redis_host, redis_port))
        rc = None
        redis_read = redis_write = None

    # Check Redis server for pre-loaded graph and metadata.
    graph_key = redis_prefix + 'main_graph'
    metadata_key = redis_prefix + 'main_metadata'
    if redis_read:
        pickled_graph = rc.get(graph_key)
        pickled_metadata = rc.get(metadata_key)
    else:
        pickled_graph = None

    # If we found pre-loaded data in Redis, unpickle it.
    if pickled_graph and pickled_metadata:
        graph = pickle.loads(pickled_graph)
        metadata = pickle.loads(pickled_metadata)

    # If there was no data in Redis, load it from file instead.
    else:
        data_dir = os.environ.get('PATENT_DATA_DIR',
            os.path.expanduser('~/Downloads/PatentNetworks'))
        graph_file = os.path.join(data_dir,
            'citation pairs by applnID simple try sorted by citing.txt')
        meta_files = [
            os.path.join(data_dir, filename)
            for filename in (
                'LEDs patents keyinfo.txt',
                'LEDs patents applicants longform.txt',
                'LEDs patents ipcas longform.txt',
            )]
        with timed('Loading graph from file'):
            graph = read_graph(graph_file)
            metadata = read_metadata(meta_files)
            annotate_graph(graph, metadata)

        # If allowed, pickle the graph and metadata and write it back to Redis.
        if redis_write:
            pickled_graph = pickle.dumps(graph)
            pickled_metadata = pickle.dumps(metadata)
            rc.set(graph_key, pickled_graph)
            rc.set(metadata_key, pickled_metadata)

    global _graph
    global _metadata
    _graph = graph
    _metadata = metadata

@contextlib.contextmanager
def timed(description):
    """Print timing information on code within the context."""
    print('{}...'.format(description), end='', flush=True)
    start = time.clock()
    yield
    end = time.clock()
    print('done after {} seconds.'.format(end - start))

def histogram(dct):
    """Return a Series of the lengths of dct's values, indexed by key."""
    return pandas.Series({key: len(val) for key, val in dct.items()})

def read_graph(filename):
    """Read edgelist from tsv file, return a networkx.DiGraph."""
    frame = read_tsv(filename)
    clean_frame = frame.dropna() # ignore missing data
    edgelist = [
        (int(src), int(dst)) # convert edges to integers
        for src, dst in clean_frame.values.tolist()
    ]
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

if __name__ == '__main__':
    main()
