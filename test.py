import collections

import statistics

import dataio

def main():
    graph = dataio.graph()
    metadata = dataio.metadata()

    key = 'ipcaA'
    series_dirty = metadata[key]
    print('Total entries:', len(series_dirty))
    series = series_dirty.dropna()
    print('Nan entries:', len(series_dirty) - len(series))

    index_counts = collections.Counter(series.index).values()
    print('IPCAs per appln (min):', min(index_counts))
    print('IPCAs per appln (max):', max(index_counts))
    print('IPCAs per appln (mean):', statistics.mean(index_counts))
    print('IPCAs per appln (median):', statistics.median(index_counts))

if __name__ == '__main__':
    main()
