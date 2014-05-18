---
title: Patent writeup
...

We want to see if we can use the network structure to create similar
clusterings to those we would find using the metadata (such as International
Patent Classification).

# Clustering

We created 20 clusters using the technique described in [section], then
compared them to the clusters of 20 the most common IPC numbers.

The best matches were as follows:

    header
    83%    1%  7   0

(something about joining clusters)

    new reulsts
    50%   10%  .. . ..

# Classification

Since recreating the clusters themselves was only successful in one direction,
we can still use it for prediction purposes.

Given a patent with unknown classification, we can guess using the following
technique:

-   Take the 5 citations with highest indegree
-   Report the N most common IPCs among those 5 patents

Our success rate is:

    .....
