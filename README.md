# The Dynamics of Innovation

# Abstract
Today, innovation is certainly among the most important factors determining the success of organizations, universities, start-ups, etc. While innovation is often portrayed as the product of either one charismatic leader - or a ragtag team of geniuses - in reality we suspect that innovations, however important, happen in small steps supported by large networks of people.

We also believe that this former image of innovation is counter-productive, insofar as it creates unrealistic expectations of what it takes to be an innovator. We think that it is important for people to realize the extent to which innovation is mostly bred by networks of collaboration. But how to explore this issue in a quantitative manner?

One possible way to measure innovation is through patents. By looking at one patent's citations, for instance, we can get an idea about which prior inventions either inspired, supported, or even made possible the other patents development. By peeling back these layers, we can then visualize a network of "innovation steps", and the people behind them.

While we're at it, we can go even more in depth and ask a variety of questions which could help us further understand the dynamics of innovation.


# Research questions
Answering the following questions will help us understand the dynamics of innovation and come up with a meaningful analysis.
- **Q1** What does the typical patent-holder look like today (Corporation, Universities, Governments, Individuals), and how has that evolved throughout time / geographies ?
- **Q1.1** Is a migration of innovators through time visible in the data, e.g. a convergence towards certain innovation centers?
- **Q1.2** How has the number of assignees and inventors evolved through time for different patent types? Are there significant differences in these numbers between different geographies?  
- **Q2** How can we best identify and visualize different geographical innovation networks? Can we estimate the number of people in such networks?
- **Q2.1** If we then take a few examples of different types of companies and look at the network of patents supporting their own patents, will these networks match up with the former innovation networks, or will they be more self-contained? In the latter case, can we estimate the number of people that make up these networks? Are these innovation networks concentrated around specific areas, or are they spread out ?
- **Q2-2** Do similar companies use the same knowledge bases to innovate? For example, if we look at different social networking companies, will the networks supporting their patents be distinct? Will a given companies patents mostly cite their own previous patents, or will they tap outside innovation networks? On what scale?
- **Q2.3**  What about if we look at university/academic knowledge bases and compare them with those of the companies analyzed above?
- **Q2.4** What about governmental or non-governmental organizations, or international agencies?  
- **Q2.5** How have the innovation networks identified above evolved through time?


# Dataset
We use the **PatentsView database**, which covers an extensive list of features for each of the patents in its database.
Link: http://www.patentsview.org/api/doc.html

The PatentsView data is available through an API, which we can access through simple GET or POST requests in Python. The procedure that we follow to extract useful data from the API is explained in the preprocessing.ipynb notebook.

# Files and Modules
The project files in the repository are as follows:
- preprocessing.ipynb
- pipeline.py
- analysis.ipynb

## preprocessing.ipynb
This notebook contains the details of the procedure we followed to determine the data we need to answer the research questions. To summarize :
- We start by going through the questions and coming up with the list of features which we need to extract from the **PatentsView API**, as well as the filters we need to get the right data.
- We then provide explanations of how we set-up the data gathering from the API and the preliminary data formatting.
- We provide an example of the analysis that was carried out on the data to check for inconsistencies and usability.
- Finally, we use the knowledge gathered through the above steps to come up with a data cleaning procedure.

## pipeline.py
This python file contains all the functions that resulted from the analysis carried out in the preprocessing.ipynb notebook and which are used for
- building the query strings in the **PatentsView API** format;
- querying and saving the data from the API;
- cleaning the data and gathering it in a minimal number of Pandas DataFrames.

## analysis.ipynb
This notebook contains the first the outline for the data story we want to tell. For now it is mostly a discussion of the procedure we plan to follow in order to write the story. The main insight from this outline is that we will need to focus a lot of energy on making sure that the visualizations are simple yet detailed enough to succintly convey the message we want to share.


# Weekly plan until Milestone 3
With preprocessing and cleaning steps done, we begin the three remaining weeks with the objectives of performing processing of the data to answer the questions we asked, as well as interpreting the results and visually displaying them in an attractive way. 

## Week 48
- Obtention of first results for Question 1 and its sub-parts: implementation of **Folium** maps and **HoloViews** interactive graphic depictions
- Editing of the notebook with results from those first processing steps
- First trials of maps visualization with **Jekyll** platform
- Aim at the end of the week: Results and Interpretations of Q1.1 & Q1.2

## Week 49
- Implementation of Question 2 and its sub-parts: evolution through time of patent networks using **networkx** graphs for three types of organisations (companies, universities and non-governmental organisations)
- Continuation of our data story building with **Jekyll** platform with results of Question 2 
- Extension of the notebook with textual descriptions of Question 2 results  
- Aim at the end of the week: Results and Interpretations of Q2.1 to Q2.5

## Week 50
- According to TAs feedback following Milestone 2 and to the evolution of our work, answering to the additional questions concerning the fields of innovation, the number of most innovating patents, the geographical zones of innovation industry and its evolution through time
- Completion of the data story with comments on illustrated phenomena 
- Aim at the end of the week: Handing back of the data story together with the completed notebook on Sunday 16th December 

## Until poster presentation
- Poster preparation with selection of most striking results and training for oral presentation 


# Questions for TAs
We have dropped from the project an entire block of questions which asked if it was possible to visualize the innovation centers for different industries. The main reason behind this decision is that we realized that the PatentsView database did not already contain a refined classification of the patents by specific industry. We decided that while it was certainly possible to use statistical measures, such as TFIDF (please refer to the end of the paragraph), or Machine Learning / Natural Language Processing to implement this classification ourselves using e.g. patent titles and abstracts, it would be risky (time and performance - wise) to do this. So now it turns out that the greatest technical challenge for the data story will be to create a small number of visualizations which are simple yet detailed enough to show the enormous amount of information we want to convey. We are worried though that maybe this is not enough of a technical challenge. Do you think this is sufficient for you to be able to evaluate everything it is that needs to be evaluated through this project? 

NB: TFIDF (term frequency-inverse document frequency) method appears to be a way to extract the field of a certain patent: the main topic to which the patent is related to can be detected by looking for words that have high occurrence frequency in the so-called patent but low occurrence frequency in the whole patents dataset.
