---
title: Analysis of the International Trade Network (ITN) with Community Detection
categories: economics
comments: true
layout: post
---

TLDR: **12 July 2026, Sunday**:  This is the foundation/1st part of the article on an interesting paper implementation I am working on. The article will be updated as and when I implement more parts of it. Do go ahead and read the progress so far. Cheers!

-----------------------------------------------

Hello,

An interesting subject in the field of economics is international trade. My understanding of this subject is quite informal and have been wanting to look into it in a serious manner. Practically, international trade consists of nations importing and exporting a variety of goods and services to and from another set of nations and this is what makes it one large network, the international trade network (ITN). I think there are different facets to this network.

1. The trade network is not homogenous in nature. It can be viewed at different levels of granularity. For example, one can focus on broad regions (Americas, Europe, Asia etc.,), or individual nations or even at firm level [14].    
2. The levels of granularity may not be just in terms of geographies and legel entities but also at the industry and commodity level. One might want to observe the trade of oil, or gold & silver, steel, agricultural produce, military equipment, electronics and so on.   
3. The international trade network observed is a result of policies (internal and foreign affairs), trade agreements among nations and regions, MoUs among and between so many parties.   
4. The ITN is a gateway to the broader world of international trade which is one of the core areas in international economics.   
5. International macroeconomics (capital flows, monetary systems, exchange rates) are strongly linked to international trade.

With the subject being quite vast, I would like to start small. Just to get a good view of the international trade network, how it looks like in 2026, its evolution over years and decades, observe some interesting aspects of ITN in a legible and consistent manner would be a good start.

While searching for publications that can be good starting points for this endevour, I came across a host of publications that views the ITN as one large complex graph/network and using it to conduct certain analysis on them. One class of publications dealt with identifying different unique groups of importance (formally known as **communities**) within the trade network. For example, if we consider the international trade network of the textile industry at the granularity of nations, China, India, Bangladesh and Vietnam would be the 4 **nodes** of importance because they lead in textile production and China-India-Bangladesh-Vietnam can be seen as a **community** from Asia which have trade flows (or **linkages**) with a large number of nations. Similarly, France and Italy individually are leaders in the classic luxury industry, and them along with a few other european nations which lead in more nuanced luxury would form a **community** based in Europe. US distantly followed by France and other countries probably form a community for military equipment production and export. At a macro-level, it would be quite interesting to see which nodes and communities are formed (from both production and consumption point of view) at the aggregate level or at granular level (industry/commodity), we would get a sense of who is exporting a lot, who is big on imports, look at how questions like "how has the world changed post globalization", "is the world become more globalized or regionalized" and so on.

Identifying communities in a given trade network seems to be a niche research field in itself where researchers and economists have spent good part of their lives improving the methods to do it and to gain better insights post analysis. One interesting publication I came across in this genre is "The Rise of China in the ITN" [11] from 2014, which discusses the rise of China in the ITN over the last few decades. China's rise as a trade superpower has been a hot topic of discussion atleast in the last decade if not more, so it will be interesting to take a closer look at it. The paper is fairly simple, it is understandable, and most importantly, the datasets and methods used for analysis are all available for public use. And the analysis can be extended (and I am sure it has already been extended) in many directions once we get a hold of the paper.

This article is an attempt to take a serious stab at understanding international trade. It will be about understanding and implementing that paper. The goal is to first reproduce the results in the paper, document the learnings thus far and then see in which direction we can go.

## 1. What is the paper about?

Let us take a look at the paper in a bit more detail in this section.

The paper [14] is named "The Rise of China in the ITN: A Community Core Detection Approach", published in 2014 by a couple of physicists and mathematicians from Europe. At a high level, the paper attempts to look at the evolution of the international trade network, observe the stark changes it has undergone and conduct analysis to find reasons behind the changes. Consider the following diagram from the paper.

![2. 1995 - ITN Diagram](/assets/2026-07-12-analysis-of-itns-community-detection/2%20-%20ITN%20diagram%201995.jpg)

It is a simple representation of the international trade network (ITN) in the year 1995. It has 3 communities (denoted by different colors): Americas, Europe and Asia-Oceania. Each community has different nations in it, some nations with trade flows with multiple other nations (who have many linkages), some at the periphery with trade linkages with only a few nations. Intuitively speaking, it is easy to tell who is the **leader** of the community. For example, in the Asia-Oceania community (Blue), Japan (JPN) seems to have trade linkages with many nations, whereas China (CHN) has a couple of linkages (with Korea/KOR, Hong Kong/HKG and USA). In the community of Americas (Yellow), USA clearly emerges as the leader. In the Europe community (Red), Germany (Deutschland/DEU) seems like the leader immediately followed by France (FRA) and Great Britain (GBR). Now consider the following diagram.

![3. ITN evolution](/assets/2026-07-12-analysis-of-itns-community-detection/3%20-%20ITN%20evolution.jpg)

We now have snapshots of ITN for 3 years: 1995, 2002 and 2011. One can observe how the ITN has changed/evolved with time. Interestingly, the Asia-Oceania community (Blue) seems to have disappeared in the 2002 ITN and has merged with the Americas (Yellow). But fast forward 2011, Asia-Oceania community (Blue) reemerges with a new contender for the leadership, China. And apart from that, it can be seen how trade linkages has grown among nations.

Along with these, the paper also looks at how important a particular nation is to the community, formally defined as **community core**: What nations are the core of a community, what is the importance of each nation inside its community. Look at the below diagram from the paper.

![4. Community core](/assets/2026-07-12-analysis-of-itns-community-detection/4%20-%20community%20core%20.jpg)

On the two ends of the spectrum (0 to 1 scale) are Yellow and Red. The Redder the nation, more important it is to its community. USA has always been one of the high importance nations inside its community across decades. In 1995, Japan is the only nation that is Red in the Asia-Oceania community pointing to its high importance. That disappeared in 2002 and is orange in 2011, whereas China has gone completely Red pointing to the fact that its importance in the Asia-Oceania is very high.

The paper does not stop here. It goes one step further to explain the dynamics of the Asia-Oceania community. The paper attempts to find if there is a correlation between the leadership change inside the Asia-Oceania community (a regional phenomenon) and the disappearance and reemergence of the Asia-Oceania as a separate community (a global phenomenon). To explain this, the paper goes into the inter-community trade vs intra-community trade. Consider the following diagram from the paper.

![5. Inter vs. Intra Community Trade Ratio b/n Asia-Oceania and America](/assets/2026-07-12-analysis-of-itns-community-detection/5%20-%20inter-intra-comm-trade-ratio-asia-america.jpg)

First of all, Inter-Community Trade is the trade that happens across communities. Intra-Community Trade is the trade that happens among the nations inside a community. Intuitively, we are seeing where the inter-community trade (between Asia-Oceania and Americas) stood with respect to the respective intra-community trades. Apart from the years 1997-2003, the average of the ratio seems to be around 0.45. In those peak years, the average went well beyond 0.5 (probably above). So there were those 5-6 years (1997-2003) when inter-community trade increased quite a bit which probably led to the merger of the communities (as seen in the ITN 2002). But when the inter-community trade reduced and the ratio went back to average, we see the reemergence of Asia-Oceania community (the merger broke off due to reduction in inter-community trade). This is something we should confirm by looking at ITN 2005 (and not ITN 2011, which is 9 years after 2002). But this is what the paper is pointing at. Another change that seemed to have occured during this time is the change in leadership inside the Asia-Oceania community, which also we should confirm by looking at ITN 2005 (and not ITN 2011). Checkout the below diagram from the paper.

![6. Intra and Inter-Community Strengh of Japan and China](/assets/2026-07-12-analysis-of-itns-community-detection/6%20-%20inter-intra%20community%20strength%20of%20jpn%20and%20chn.jpg)

2003 seems to be the tipping point where the strengths of the 4 trade flows are almost the same. Post 2003, China's trade flows (both inter and intra community) are stronger than those of Japan's and the gap has only increased. And this tipping point is around the time the leadership change inside the Asia-Oceania community has happened. We can evaluate this too.

The authors not only look at ITNs and analysis on them, but also have looked at different trade agreements for these nations (especially China's agreements with nations inside and outside its community) to corroborate with the information we have.

The abstract is a good one paragraph summary of the paper.

> Theory of complex networks proved successful in the description of a variety of static networks ranging from biology to computer and social sciences and to economics and finance. Here we use network models to describe the evolution of a particular economic system, namely the International Trade Network (ITN). Previous studies often assume that globalization and regionalization in international trade are contradictory to each other. We re-examine the relationship between globalization and regionalization by viewing the international trade system as an interdependent complex network. We use the modularity optimization method to detect communities and community cores in the ITN during the years 1995-2011. We find rich dynamics over time both inter- and intra-communities. Most importantly, we have a multilevel description of the evolution where the global dynamics (i.e., communities disappear or reemerge) tend to be correlated with the regional dynamics (i.e., community core changes between community members). In particular, the Asia-Oceania community disappeared and reemerged over time along with a switch in leadership from Japan to China. Moreover, simulation results show that the global dynamics can be generated by a preferential attachment mechanism both inter- and intra-communities. 

In essence, the paper is about observing the evolution of the international trade network over time and explaining what caused these changes. This particular paper emphasises on China and mostly the global and regional dynamics of the Asia-Oceania community, but I think the techniques used can be applied in a variety of contexts.

The ideal next step here would be to talk about each of sections in the paper in detail and plan the implementation. But one of the important pre-requisites to the next step is to understand how these communities that we have intuitively understood even generated from the international trade network. The concept of **community detection** is what makes it happen. So we take a deroute here to take a quick look into community detection and then go back to the paper.

## 2. What is Community Detection?

The world is full of large graphs. One can find graphs and complex networks in every field. One of the most intuitive variety of graphs are the social graphs [1], typically formed by big social media platforms, where people (or their accounts) are the nodes and the connections/follows are the edges. Knowledge Graphs [2] is one which has lots of knowledge sources linked together along with linkages to authors and users in a meaningful manner. Search companies like Google and Microsoft have their own knowledge graphs, DBpedia [3] is a knowledge graph built out of Wikipedia. The academic world also has knowledge graphs. One obvious example is where academic publications are the nodes and the citations can be seen as linkages (each of the large academic publishing companies would definitely have such knowledge graphs [15]). There are highly complex network structures found in biology [4], one example is cells as nodes and the variety of interactions they have with other cells as linkages. On the business side, we come across large logistics/transportation networks [16]. As we have seen, in economics, we have trade networks where goods and services flow from one nation to another.

One obvious characteristic you might observe in real world networks is that no two nodes are the same, the nodes are all different. Certain nodes tend to have higher importance, with the meaning of **importance** being very context-specific to the network at discussion. When it comes to social networks, nodes with very high influence (primarily measured by number of followers) are nodes of higher importance. In the context of knowledge graphs, there could be knowledge sources (websites, documents) which have been highly visited and are ranked higher than others. Or in the context of international trade in textile industry, China leads the production followed by India, Bangladesh and Vietnam, these are important nodes in the textile trade. Another example would be how France is a highly important node in the luxury industry. In all these examples, the linkages to these nodes are very high in number.

Going one step further, there can be group of nodes which are densely connected among each other but are sparsely/weakly connected to nodes outside of that group. Consider the following diagram.

![1. community definition](/assets/2026-07-12-analysis-of-itns-community-detection/1%20-%20community%20definition.png)

There are 4 groups of nodes which are strongly linked with each other, but weakly linked to other groups. Such groups can vaguely be defined as **communities**. We already saw communities in the international trade network and a glimpse into how they appear/disappear/merge/separate based on the interactions.

While the concept of communities inside a complex network is quite intuitive to understand, detecting and identifying them computationally is a non-trivial problem. To put it clearly, we have a complex network (nodes, edges and possibly weights for these edges), we need to find the communities. This problem is formally known as graph partitioning [13] in computer science. The graph is partitioned in different pieces based on certain condition. This is a known NP-Hard problem, meaning no polynomial-time algorithm exists, and the complexity to find those communities exponentially increases proportional to the number of nodes. There is a great deal of research on this very problem, and there are a variety of approaches to tackle it [5]. Of these approaches, this paper uses the **modularity optimization** method by Girvan and Newman [8]. There are a variety of algorithms based on this method, the landmark ones are as follows: Girvan-Newman [8], the introduction of **modularity** as the objective function for optimization [9] which is used now in different shapes and forms today as well, the 2008 Louvain algorithm [6] and the recent 2019 Leiden algorithm [7] which identified problems with the Louvain algorithm and suggested an improved method.

The authors in the paper use the Girvan-Newman algorithm [8] for community detection, but Louvain [6] and Leiden [7] are better. We would be using one of these for community detection. It is important to have a fair understanding of Louvain algorithm. I would suggest the reader to watch the video [17] and then the actual paper[6]. There is already a python implementation of the Louvain algorithm [18] with which one can experiment with to get a hang of it. For Leiden, I would suggest these: Video [19], paper [7], python implementation [20]. Consider the following sample example of Louvain algorithm in action. The below is a simple network, an unpartitioned one (one where community detection algorithm has not been executed).

![8. before louvain](/assets/2026-07-12-analysis-of-itns-community-detection/8%20-%20before%20louvain.jpg)

If we want to find the communities, we run the louvain algorithm and below is what we get.

![9. after louvain - output 1](/assets/2026-07-12-analysis-of-itns-community-detection/9.%20after%20louvain%20-%20output%201.jpg)

If you run the algorithm a couple of times, you might end up seeing a different partition, like this.

![10. after louvain - output 2](/assets/2026-07-12-analysis-of-itns-community-detection/10.%20after%20louvain%20-%20output%202.jpg)

Different factors like starting point, order in which the nodes are processed by the algorithm decide how the partition looks like. It is in a way similar to K-means clustering. The paper gives some explanation as to why it is this way. You may find here[21] the jupyter notebook for code used above.

## 3. Implementation Plan

Now that we broadly know what the paper does and what community detection is, we can come up with an implementation plan. Here are the steps.

1. **Constructing ITN from Datasets**: This is the foundational step, where we take a closer look at the dataset, give it a good descriptive analysis and understand it better. Get the dataset for a particular time instance ready (say 1995) and implement the community detection algorithm (Louvain/Leiden) on it. We should have a rich descriptive analysis and visualization of the trade network of a particular time instance. As we saw earlier, the below is the ITN 1995 generated from the dataset.

![2. 1995 - ITN Diagram](/assets/2026-07-12-analysis-of-itns-community-detection/2%20-%20ITN%20diagram%201995.jpg)

2. **Evolution of ITNs over time**: Once we have the ITN construction solution for one time instance, we can incrementally apply the same solution for data of the time instances we want (say we want 1995, 2002, 2005, 2011 or more). We should have all the details for each of these ITNs. With that we should be able to see the global phenomenon of disappearance and reemergence of the Asia-Oceania community from the global ITN, and ideally be able to reproduce all the other relevant observations (like leaders of communities and change of leadership in Asia-Oceania community and so on) as seen below.

![3. ITN evolution](/assets/2026-07-12-analysis-of-itns-community-detection/3%20-%20ITN%20evolution.jpg)

3. **Community Core Detection**: The paper then discusses community core detection, that tells us the importance of each node in its community. The below is the diagram from the paper. The community core detection is an incremental solution that can be programmed along with traditional community detection, which we will in this step (Check Sections IIB and Figure 1 in the paper [11]).

![4. Community core](/assets/2026-07-12-analysis-of-itns-community-detection/4%20-%20community%20core%20.jpg)

4. **Linkage between global and regional dynamics**: Step 2 should help us observe the global phenomenon of disappearance and reemergence of Asia-Oceania region as a community during 1997-2003. Step 3 should help us observe the regional phenonemon leadership change of Asia-Oceania community from Japan to China during the same time period. But those are observations. In this step, we conduct the analysis necessary to forge the linkage between the two (Section V in its entirety). We will look at the inter-community trade vs. intra-community trade we saw earlier and other details necessary to understand this link.

5. **Understanding agreements and policies**: The paper looks just at China's trade agreements inside and outside of its community to corroborate with the analysis performed earlier. Below is a table from the paper. We should go further and look at not just China's but other nations' as well.

![11 - china's RTA](/assets/2026-07-12-analysis-of-itns-community-detection/11%20-%20chinas%20rta.jpg)

This should ideally cover all aspects of the paper, but we can have one more section to tie up the loose ends in case.

## 4. Future Work and Conclusion

This post is the foundation article of the paper implementation [11]. It sets the skeleton in place. The actual implementation, analysis and discussion will be updated in parts inside the same article in due time. Thank you for reading.

Cheers!   
Adwaith

## References

1. [The Rise of Social Graphs for Businesses - HBR](https://hbr.org/2015/02/the-rise-of-social-graphs-for-businesses)    
2. [Knowledge Graphs on the Web: An Overview](https://arxiv.org/pdf/2003.00719)   
3. [DBpedia: A Nucleus for a Web of Open Data - 2007](https://link.springer.com/chapter/10.1007/978-3-540-76298-0_52)    
4. [Scale-free Networks in Cell Biology by R. Albert, 2005](https://arxiv.org/pdf/q-bio/0510054)     
5. [Community Structure in Graphs: 2007](https://arxiv.org/pdf/0712.2716)   
6. [Fast unfolding of communities in large networks - the Louvain algorithm, 2008](https://arxiv.org/abs/0803.0476)   
7. [From Louvain to Leiden: Guaranteeing well-connected communities, 2018](https://arxiv.org/abs/1810.08473)   
8. [Finding and evaluating community structure in networks: Girvan & Newman algorithm, 2002](https://arxiv.org/abs/cond-mat/0308217)    
9. [Modularity and community structure in networks: Newman, 2006](https://arxiv.org/abs/physics/0602124)    
10. [Identifying the Community Structure of the International-Trade Multi Network, 2011](https://arxiv.org/abs/1009.1731)   
11. [The Rise of China in the International Trade Network: A Community Core Detection Approach, 2014](https://arxiv.org/abs/1404.6950)   
12. [Asia-Oceania, by Ministry of Foreign Affairs, Japan](https://www.mofa.go.jp/policy/other/bluebook/2016/html/chapter2/c020100.html)   
13. [Graph Partitioning, Wikipedia](https://en.wikipedia.org/wiki/Graph_partition)    
14. [Firm-to-Firm Trade Networks: A Focus on Latin-America and the Carribean](https://publications.iadb.org/publications/english/document/Firm-to-Firm-Trade-Networks-A-Focus-on-Latin-America-and-the-Caribbean.pdf)    
15. [Springer SN SciGraph](https://communities.springernature.com/users/82895-sn-scigraph)    
16. [Community core detection in transportation networks, 2013](https://arxiv.org/pdf/1304.0141)   
17. [Discovering Communities: Modularity & Louvain, Splience 2023 - Video](https://www.youtube.com/watch?v=Xt0vBtBY2BU)    
18. [python-louvain](https://github.com/taynaud/python-louvain)   
19. [Leiden Algorithm Explained: A Smarter Way to Detect Communities in Networks - Video](https://www.youtube.com/watch?v=hIQM0XLyQiQ)   
20. [leidenalg - python package](https://leidenalg.readthedocs.io/en/stable/)   
21. [Louvain - Example](/assets/2026-07-12-analysis-of-itns-community-detection/Louvain-sample.ipynb)   
