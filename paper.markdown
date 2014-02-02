---
title: Case study of approaches to finding patterns in citation networks
author: Mukkai Krishnamoorthy; Kenneth Simons; Benjamin Pringle
numbersections: true
bibliography: references.bib
---

# Introduction

## Case study: LED patents

Data supplied by @simons11data.

The `applnID` field specifies a unique identifier for each patent application
in the dataset.

## Computation

The computation for this paper was performed using the Python programming
language (<http://python.org/>) and the following libraries:

-   `networkx` for network representation and analysis [@hagberg08]
-   `pandas` for tabular data analysis [@mckinney12]
-   `matplotlib` for creating plots [@hunter07]

# Approaches

## Network structure

The graph has 127,526 nodes and 327,479 edges.

### Forward citations (indegree)

![Histogram of patents with under 50 citations](indeghist50below.png)

![Histogram of patents with 50 or more citations](indeghist50up.png)

Popularized by @garfield64, the simplest way to determine a patent is counting
its forward citations -- that is, other patents which cite the patent in
question. In a citation network where edges are drawn from the citing patent
to the cited patent, the number of forward citations for a given node is its
**indegree**, or the number of edges ending at the given node.

In our data, 89% of patents have fewer than 5 citations, and 99% have fewer
than 50. Nevertheless, there is a small group of slightly over fifty patents
with at least a hundred citations each.

The top ten most-cited patents in our dataset are shown in a table below:

 applnID  indegree
-------- ---------
47614741       444
51204521       360
52376694       339
48351911       305
45787627       283
45787665       267
46666643       235
53608703       213
54068562       213
23000850       203

### PageRank

Another technique for classifying important nodes in a graph is PageRank
[@page99rank], one of the most famous algorithms used by the Google search
engine to rank web pages.

## Clustering

![Neighborhood sizes for top 20 cited patents](nhood_sizes.png)

As noted by @satuluri11, most clustering techniques deal with undirected
graphs.  We introduce a very simple technique for defining overlapping
clusters in a *directed* citation network:

-   Select a small number of highly cited patents as seeds.
-   Each seed patent defines a cluster: all patents citing the seed are
    members (its open 1-neighborhood).

We considered using larger neighborhoods. The $n$-neighborhood can be computed
recursively by adding all patents citing any patents in the
$(n-1)$-neighborhood. However, these larger neighborhoods grow in size very
quickly. For our purposes (quick computation and visualization), we decided to
keep the smaller clusters from 1-neighborhoods.

This technique creates *overlapping* clusters, where a node can belong to more
than one cluster. Looking at the clusters created from the top 10 most-cited
patents, we computed two measures of overlapping:

-   `percentunique` is the fraction of nodes in *only* that cluster
-   `bignodes` is the number of seed nodes that appear in the cluster (for
    example, the  second cluster contains the seed patent used to generate the
    first cluster, along with three others from our original ten seeds)

The following chart shows the value of `percentunique` and `bignodes` for each
of the ten clusters:

 clustersize  percentunique  bignodes
------------ -------------- ---------
         444       0.202703         0
         360       0.100000         4
         339       0.280236         0
         305       0.163934         4
         283       0.141343         0
         267       0.101124         0
         235       0.940426         0
         213       0.985915         0
         213       0.464789         0
         203       0.226601         0

Looking at `percentunique`, many clusters have a good deal over overlap, with
unique contributions as low as 10%, although others are up to 98% unique. Our
analysis will therefore **not** assume that these clusters strictly partition
the data, and rather look at the clusters as distinct but potentially
overlapping areas of patents.

#### Computation

The $n$-neighborhood of a node can be computed using the [included
code](#code):

```python
neighborhood(graph, nbunch, depth=1, closed=False)
```

-   `graph` -- a `networkx.DiGraph` [see @hagberg08]
-   `nbunch` -- a node or nodes in `graph`
-   `depth` -- the number of iterations (defaults to 1-neighborhood)
-   `closed` -- set to `True` if the neighborhood should include the root

Returns a `set` containing the neighborhood of the node, or a `dict` matching
nodes to neighborhood `set`s.

## Metadata analytics

# Conclusions

# Code

# Unused citations

-   @batagelj03 (efficient citenet algos)
-   @garfield64 (citation nets)
-   @hummon89 (splc)

# References
