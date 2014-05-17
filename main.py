import os
import time
import contextlib

import pandas
import networkx

import analysis

@contextlib.contextmanager
def timed(description):
    """Print timing information on code within the context."""
    print('{}...'.format(description), end='', flush=True)
    start = time.clock()
    yield
    end = time.clock()
    print('done after {} seconds.'.format(end - start))

def read_graph(filename):
    """Read edgelist from tsv file, return a networkx.DiGraph."""
    frame = read_tsv(filename)
    clean_frame = frame.dropna() # ignore missing data
    edgelist = [
        (int(src), int(dst)) # convert edges to integers
        for src, dst in clean_frame.values.tolist()
    ]
    return networkx.DiGraph(edgelist)

def read_metadata(filename, index_col='applnID'):
    """Read metadata from tsv file and return a pandas.DataFrame."""
    return read_tsv(filename, index_col=index_col)

def read_tsv(filename, index_col=None):
    """Return a pandas.DataFrame of a tsv file."""
    return pandas.read_csv(filename,
                           delimiter='\t',
                           encoding='ISO-8859-1',
                           index_col=index_col,
                           dtype=object,
                           low_memory=False)

def main():
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

    with timed('Loading graph'):
        graph = read_graph(graph_file)
    with timed('Loading metadata'):
        metas = [read_metadata(filename) for filename in meta_files]
    with timed('Merging metadata'):
        clean = lambda s: s.loc[graph.nodes()].dropna()
        metadata = {
            'novelty': clean(metas[0]['applnIpcaNovelty']),
            'date': clean(metas[0]['applnFilingDate']),
            'company': clean(metas[1]['appMyName']),
            'ipca': clean(metas[2]['ipcaA']
                       + metas[2]['ipcaB']
                       + metas[2]['ipcaC']
                       + metas[2]['ipcaD']
                       + metas[2]['ipcaE']
                        ),
        }


    #  {0: Index(['applnAuth', 'applnNr', 'applnKind', 'applnFilingDate',
    #  'applnGrantDate', 'grantedAll', 'utilityModel', 'docdbFamilyID',
    #  'inpadocFamilyID', 'equivGroupID', 'applnDocdbCountries',
    #  'applnDocdbGrantedCountries', 'applnInpadocCountries',
    #  'applnInpadocGrantedCountries', 'chunknum', 'applnNumIPCAs',
    #  'applnIpcaNovelty', 'applnNFirstInIPCA', 'applnNFirstInIPCAPair',
    #  'applnNumUSClasses', 'applnUSClassNovelty', 'applnNFirstInUSClass',
    #  'applnNFirstInUSClassPair'], dtype='object'), 1: Index(['applnAuth',
    #  'applnNr', 'applnKind', 'appSNam', 'appMyName', 'acquirerMyName',
    #  'acqAnnounceDate', 'acqCompleteDate', 'chunknum', 'appNum'],
    #  dtype='object'), 2: Index(['applnFilingDate', 'applnGrantDate',
    #  'grantedAll', 'utilityModel', 'ipcaA', 'ipcaB', 'ipcaC', 'ipcaD',
    #  'ipcaE', 'ipcaVersion', 'ipcaInventive', 'ipcaMainClass', 'ipcaAuthor',
    #  'j'], dtype='object')}

    with timed('Analyzing...\n'):
        analysis.AnnotatedNetwork(graph, metadata).report()

if __name__ == '__main__':
    main()
