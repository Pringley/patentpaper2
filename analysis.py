"""Code used in citation network analysis."""
from __future__ import print_function
import random

import networkx
import pandas

# # Setup and helpers

def normalize(series):
    """Helper function to normalize a `pandas.Series`.

    Scale values to fall within 0 and 1.

    """
    return (series - series.min()) / (series.max() - series.min())

class AnnotatedNetwork(object):
    """Class representing a network with associated metadata.

    Analysis functions defined within will have access to both the network and
    its metadata.

    Constructor arguments:

    -   **`network`** is a `networkx.DiGraph`.

    -   **`metadata`** is a `pandas.DataFrame`.

    """

    def __init__(self, network, metadata):
        self.network = network
        self.metadata = metadata

    def neighborhood(self, root, depth=1):
        """Function to calculate the neighborhood of a node.

        Arguments:

        -   **`graph`** is a `networkx.DiGraph`.

        -   **`root`** is a node in `graph` from which the neighborhood is
            generated.

        -   **`depth`** is optionally an integer specifying how many iterations are
            used to create the neighborhood.

        """
        neighborhood = set([root])
        for _ in range(depth):
            # Expand by adding all nodes adjacent to any node currently in the
            # neighborhood.
            for node in neighborhood.copy():
                neighborhood |= set(self.network.predecessors(node))
        return neighborhood

    def classify(self, node, field, max_cited=20):
        metadata = self.metadata[field]
        cited = self.network.successors(node)
        if len(cited) > max_cited:
            indegrees = pandas.Series(self.network.in_degree(cited))
            indegrees.sort(ascending=False)
            cited = indegrees.head(max_cited)
        values = metadata.loc[cited]
        mode = values.mode()
        return mode[0] if len(mode) else None

    # # Main report generator

    def report(self):
        """Generate a LaTeX report, return as `str`."""

        metrics = pandas.DataFrame({
            'indegree': self.network.in_degree(),
            'pagerank': networkx.pagerank_scipy(self.network, max_iter=200),
        })
        mean = metrics.mean()
        std = metrics.std()

        for field, series in self.metadata.items():
            successes = 0
            for node in random.sample(series.index.tolist(), 100):
                value = self.classify(node, field)
                try:
                    if value == series.loc[node] or value in series.loc[node]:
                        successes += 1
                except Exception:
                    pass
            print(field, successes)
