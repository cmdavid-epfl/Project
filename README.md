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
We mainly plan on using the **PatentsView database**, which covers an extensive list of features for each of the patents in its database.
Link: http://www.patentsview.org/api/doc.html

The PatentsView data  is available through an API, which we can access through simple GET requests in Python. An extensive list of well structured information is available for each patent, though the documentation does warn that some inconsistencies are to be expected. As we would be querying for specific data directly from the API, we would not need to get redundant columns, which should help to minimize the possibilities of inconsistencies (for example, the database includes the location of the patent assignees, as well as the latitude and longitude of patent assignees, though the documentation states that these two latter variables depend directly on the first, so we should only use the location variable).

We may also use the **Stanford Patent Citations Network** to help us in the visualizations. The dataset is structured as a direct graph, showing US citations as pairs of nodes (one patent citing another) represented in two columns in a txt.file. The size and format of this dataset should not be an issue. A drawback, however, is that it only contain data for the time period 1975-1999, solely in the US. Making it potentially less suitable to answer some of the research questions.


# A list of internal milestones for the remainder of the project
Week 48
- TBD

Week 49
- TBD

Week 50
- TBD

Week 51 - Week 3 (2019)
- Creation of the poster presentation
- Printing out the poster
- Preparing for the presentation

# Questions for TAa
TBD
