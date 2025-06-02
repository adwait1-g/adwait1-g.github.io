---
title: Artificial Intelligence & Machine Learning
categories: aiml
layout: page
permalink: /ai-ml/
comments: false
---

# 1. Deep Learning

1. [Dive into Deep Learning](https://d2l.ai/)   
2. [Neural Networks: Zero to Hero](https://youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ&si=XhjSpxeVGG_fb_k_) by Andrej Karpathy: This is how I got started with AI-ML.
3. [UV-A Deep Learning Course](https://uvadlc.github.io/)    
4. [Deep Learning](https://www.deeplearningbook.org/): I am trying my best to read this book regularly, I post about it [here](/dlbook/)   
5. [Pattern Recognition and Machine Learning](https://libgen.is/book/index.php?md5=B616EF565E2D48AE23EE2E19D7B0ADD2)  
6. [On the opportunities and risks of Foundation Models](https://arxiv.org/abs/2108.07258)   
7. [A cookbook of Self-Supervised Learning](https://arxiv.org/abs/2304.12210)

# 2. Autoencoders

1. [Introduction to Autoencoders](https://arxiv.org/abs/2201.03898)   
2. [Autoencoders](https://www.deeplearningbook.org/contents/autoencoders.html): Chapter from [Deep Learning Book](https://www.deeplearningbook.org/)   
3. [Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114): Foundation paper on VAEs (Variational AutoEncoders)   

I am a management/analytics guy, and even today most of the data I work with is structured data (even though it generally needs good bit of data-cleanup, feature engineering to make it useful and so on). I am still working inside the realm of structured data - Tables, Graphs, Time-Series Data as opposed to Text & Images. While the Deep learning research on unstructured data (text & images) today has literally exploded, the same for structured data is slowly picking its pace as I see it. Add to that, the kind of data I am working with is tabular data, but when processed using a normal deteministic algorithm, it results in graph data. So this whole area of research is very relevant for me and I find it quite interesting too. So will be listing stuff about structured data (Tabular-Graph-Time Series data in particular).

# 1. Graph Data

1. [Introduction to Graph Neural Networks: Foundations, Frontiers & Applications](https://openlibrary.telkomuniversity.ac.id/pustaka/files/201062/abstraksi/graph-neural-networks-foundations-frontiers-and-applications.pdf) by Lingfei Wu   
2. [Introduction to Graph Neural Networks](https://github.com/LiuChuang0059/Complex-Network/blob/master/Books/Introduction%20to%20Graph%20Neural%20Networks.pdf): A Textbook
3. [Introduction to Graph Neural Networks: A Starting Point for Machine Learning Engineers](https://arxiv.org/abs/2412.19419)    
4. [A Gentle Introduction to Graph Neural Networks](https://distill.pub/2021/gnn-intro/)    
5. [Graph Neural Networks in Big Data Analytics: Introduction](https://gds.techfak.uni-bielefeld.de/_media/teaching/2022winter/graphnet/introduction-201022.pdf)    
6. [Introduction to Graph Neural Networks](https://web.media.mit.edu/~xdong/teaching/aims/lecture-slides/MT21/AIMS_CDT_SP_MT21_D4.pdf): Lecture @ EPFL    
7. [Introduction to Graph Neural Networks](https://cs.stanford.edu/~jiaxuan/files/Intro_to_Graph_Neural_Networks.pdf): Lecture @ Stanford     
8. [Graph Foundation Models: Concepts, Opportunities & Challenges](https://arxiv.org/pdf/2310.11829): March 2025   
9. [Position: Graph Foundation Models are Already Here](https://arxiv.org/abs/2402.02216)    
10. [A Comprehensive Survey on Graph Neural Networks](https://arxiv.org/pdf/1901.00596): August 2019     
11. [A Comprehensive Survey on Deep Graph Representation Learning](https://arxiv.org/abs/2304.05055)    
12. [Deep Learning on Graphs: A Survey](https://arxiv.org/abs/1812.04202): 2020   

# 2. Tabular Data

1. [Deep Neural Networks and Tabular Data: A Survey](https://arxiv.org/abs/2110.01889): A near survey on Deep Learning and Tabular Data. A side note: Dr. Vadim Borisov runs a cool startup called [tabularis.ai](https://tabularis.ai), check it out if interested.   
2. [A Short Chronology of Deep Learning for Tabular Data](https://sebastianraschka.com/blog/2022/deep-learning-for-tabular-data.html) by Sebastian Raschka (this article is god's work!): July 2022  
3. [Why Tabular Foundation Models Should be a Research Priority](https://arxiv.org/html/2405.01147v1): May 2024
4. [Is Deep Learning finally better than Decision Trees on Tabular Data](https://arxiv.org/pdf/2402.03970v2): Feb 2025
5. [Towards Foundation Models for Learning Tabular Data](https://openreview.net/pdf?id=hz2zhaZPXm): 2024    
6. [TabICL: A Tabular Foundation Model for In-Context Learning on Large Data](https://arxiv.org/abs/2502.05564)   
7. [Language Models are Realistic Tabular Data Generators](https://arxiv.org/abs/2210.06280): Another paper whose aim I am interested in. Business Processes are my domain of interest, and from what I understand there is not a single large, standard dataset. Old datasets of BPI Challenges (2012-2022) are generally used even today. I think generating realistic synthetic datasets based on features of those smaller, old datasets might help research, just a vague idea.    
8. [Deep Learning within Tabular Data: Foundations, Challenges, Advances & Future Directions](https://arxiv.org/abs/2501.03540): 2025
9. [A Survey on Deep Tabular Learning](https://arxiv.org/abs/2410.12034): Oct 2024   
10. 

# 3. Time-Series Data

1. [Time Series Data Augmentation for Deep Learning: A Survey](https://arxiv.org/abs/2002.12478): March 2022
2. [Deep Learning for Time Series Forecasting: A Survey](https://arxiv.org/abs/2503.10198)    
3. [TIme Series Forecasting with Deep Learning: A Survey](https://arxiv.org/abs/2004.13408)   

1. [From Tables to Time: How TabPFN-v2 Outperforms Specialized Time Series Forecasting Models](https://arxiv.org/abs/2501.02945): This is kind of thing I am looking for. I am working on data that can be interpreted as Tabular Data, Graph Data or Time-Series Data - all 3 are deterministic transformations of one another. So this kind of work where a Tabular Foundation Model works better for a certain Time Series data than a specialized Time Series model itself enthuses me.