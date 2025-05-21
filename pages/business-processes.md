---
title: Business Processes
categories: bp
layout: page
permalink: /business-processes/
comments: false
---

I got introduced to the subject of business processes through the Enterprise Systems course during my spring semester. It gave me a good introduction along with a sneak peek into some of the advanced stuff that happens in this field - like process mining, tools like Celonis and so on. Fortunately, I work on business processes at my internship - which is business and customer facing, more like application of this field where we work on improving/re-engineering business processes of our clients. The other side of it is management research pertaining to business processes - which deals with fundamentals of business process analysis, theory and application of process mining and so on. I plan to write about both facets here, along with listing down some good resources I come across.

The focus of this page is the entire field of Business Process Management and application of Machine Learning/Artificial Intelligence in this field.

## 1. Business Process Management

This section has some of the classic books and resources on Business Process Fundamentals.

1. [Handbook on Business Process Management: Introduction, Methods and Information Systems](http://repo.darmajaya.ac.id/5380/1/Handbook%20on%20Business%20Process%20Management%201_%20Introduction%2C%20Methods%2C%20and%20Information%20Systems%20%28%20PDFDrive%20%29.pdf)    
2. [Fundamentals of Business Process Management](https://repository.dinus.ac.id/docs/ajar/Fundamentals_of_Business_Process_Management_1.pdf)   

## 2. Process Mining

Process Mining started off as an academic endevour in the 1990s and with time it has taken 

1. [Process Mining Handbook](https://library.oapen.org/bitstream/id/e9c5f431-eb92-45dc-a4ab-3f7ecbf91426/978-3-031-08848-3.pdf): By Prof. Will van der Aalst   
2. [Prof. Will van der Aalst's Website](https://www.vdaalst.com/)   
3. [Process Mining: Data Science in Action](http://repo.darmajaya.ac.id/4319/1/Process%2520Mining_%2520Data%2520Science%2520in%2520Action%2520%2528%2520PDFDrive%2520%2529.pdf)

# 2.1 Process Discovery

1. [Foundations of Process Discovery](https://www.vdaalst.rwth-aachen.de/publications/p1330.pdf) by Prof. Will van der Aalst   
2. [Process Discovery using Graph Neural Networks](https://arxiv.org/abs/2109.05835)   
3. [Supervised Learning of Process Discovery techniques using Graph Neural Networks](https://www.sciencedirect.com/science/article/pii/S0306437923000455)   

## 3. Anomaly Detection

Please check [here](/bp-anomaly-detection/).

## 4. Next Activity Prediction

As the name suggests, there is quite a bit of research in predicting the next activity that will be executed in a given business process instance. It is essentially a forecasting method which predicts the upcoming steps/activities in currently ongoing business process instances - this helps in decision making, resource allocation, anomaly detection.

Because it is a prediction/forecasting problem, lot of experiments/research have been done using AI/ML to come up with better solutions for this problem. I list a few papers I came across.

Adding to that, just because of the nature of the problem - predicting the next activity in a process instance is very similar to predicting the next word/token/character in a sentence/token-stream/word in language modeling. So models originally designed for NLP like RNNs, GRUs, LSTMs and now Transformers are all being tried out and experimented on for Next Activity Detection. Checkout section 3.3 in the 3rd paper listed here (A 2021 survey paper).

1. [Learning from the Data to Predict the Process: Generalization Capabilities of Next Activity Prediction Algorithms](https://link.springer.com/article/10.1007/s12599-025-00936-4)    
2. [SNAP: Semantic Stories for Next Activity Prediction](https://arxiv.org/abs/2401.15621)    
3. [A systematic literature review on state-of-the-art deep learning methods for process prediction](https://arxiv.org/abs/2101.09320)   
4. [An Innovative Next Activity Prediction Approach using Process Entropy and DAW-Transformer](https://arxiv.org/pdf/2502.10573)    
5. [Exploiting Instance Graphs and Graph Neural Networks for Next Activity Prediction](https://link.springer.com/chapter/10.1007/978-3-030-98581-3_9)    

## 5. Business Process Monitoring

1. [Predictive Process Monitoring: A Use-Case-Driven Literature Review](https://dl.gi.de/server/api/core/bitstreams/81b6c5e0-f15d-4732-a281-b2ca0e12426f/content)    
2. [A Systematic Literature Review on Explainable Predictive Business Process Monitoring Techniques](https://www.researchgate.net/publication/351069101_Bringing_Light_Into_the_Darkness_-_A_Systematic_Literature_Review_on_Explainable_Predictive_Business_Process_Monitoring_Techniques)    
3. [Remaining cycle time prediction with Graph Neural Networks for Predictive Process Monitoring](https://hal.science/hal-04093621/file/ICMLT2023_LT_Duong_final_paper.pdf)    
4. [Interpretable and Explainable Machine Learning Methods for Predictive Process Monitoring: A Systematic Literature Review](https://arxiv.org/abs/2312.17584)   

## 6. Business Process Simulation

1. [Runtime Integration of Machine Learning and Simulation for Business Processes: Time and Decision Mining Predictions](https://www.sciencedirect.com/science/article/pii/S0167923620300397)    
2. [Automated Discovery of Business Process Simulation Models from Event Logs](https://www.sciencedirect.com/science/article/pii/S0167923620300397)    

## 7. Business Processes and Machine Learning

I have tried to classify papers and research based on different sub-fields in Business Process Management. Some don't fit in the above broad categories, hence putting them here.

1. [Machine Learning in Business Process Management: A Systematic Literature Review](https://arxiv.org/pdf/2405.16396)    
2. [A Review of AI and Machine Learning Contribution in Predictive Business Process Management](https://arxiv.org/abs/2407.11043): Process Enhancement and Process Improvement Approaches    
3. [Large Process Models: A Vision for Business Process Management in the Age of Generative AI](https://arxiv.org/abs/2309.00900), [Link2](https://mediatum.ub.tum.de/doc/1723158/1723158.pdf)    
4. [Artificial Intelligence-Based Methods for Business Processes: A Systematic Literature Review](https://www.researchgate.net/publication/351069101_Bringing_Light_Into_the_Darkness_-_A_Systematic_Literature_Review_on_Explainable_Predictive_Business_Process_Monitoring_Techniques)    
5. [A Technique for Determining Relevance Scores of Process Activities Using Graph Neural Networks](https://arxiv.org/abs/2008.03110)   
6. [Next-Generation Business Process Management: A Systematic Literature Review of Cognitive Computing and Improvements in BPM](https://link.springer.com/chapter/10.1007/978-3-031-72041-3_18)   