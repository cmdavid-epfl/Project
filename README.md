# The Dynamics of Innovation

## Complete Data Story can be found **[here](https://cmdavid-epfl.github.io/)**

## Front Matter
Innovation today is certainly among the most important factors determining the success of organizations, universities, start-ups, etc. While innovation is often portrayed as the product of either one charismatic leader - or a ragtag team of geniuses - in reality we suspect that innovations, however important, happen in small steps supported by large networks of people.

We also believe that this former image of innovation is counter-productive, insofar as it creates unrealistic expectations of what it takes to be an innovator. We think that it is important for people to realize the extent to which innovation is mostly bred by networks of collaboration. But how to explore this issue in a quantitative manner?

One possible way is through patents. By looking at one patent’s citations, for instance, we can get an idea about which prior inventions either inspired, supported, or even made possible the other patents development. By peeling back these layers, we can then visualize a network of innovation steps, and the people behind them.


## Research Questions

### Part 1.

In this first part, we answer the following questions:
- What does the typical patent-holder look like today, and how has that evolved between today and the 1990's?
- Is a migration of innovators through time visible in the data, e.g. a convergence towards certain innovation centers?
- How has the number of assignees and inventors evolved in this period?

The goal here is to address the main issue that brought us to chose this subject for our data story, by clearly showing how innovation today transcends geographies.

### Part 2.

In this second part, we look at specific examples of innovation networks for patents held by specific similar assignees. By looking at these networks, we answer the following questions:
- If we take a few different types of companies / government bodies / academic institutions, and look at the network supporting some of their patents, what do these networks look like, in light of the conclusions from Part 1?
- Within the same companies, how have their networks evolved between today and the 1990's, if we look at patents similar to those above?
- Across companies of the same type, to what extent, if any, will their networks be similar?


## Dataset
We use the **PatentsView database**, which covers an extensive list of features for each of the patents in its database.
Link: http://www.patentsview.org/api/doc.html

The PatentsView data is available through an API, which we can access through simple GET or POST requests in Python. The procedure that we follow to extract useful data from the API is explained in the Methodology notebook.

## Files and Modules
The project files in the repository are as follows:
- Methodology.ipynb
- pipeline.py
- visualizations.py

### Methodology.ipynb
This notebook contains the details of the procedure we followed to answer the research questions. The notebook can also be found **[on the story website](https://cmdavid-epfl.github.io/methodology/)**.

### pipeline.py
This python file contains all the preprocessing and data formatting functions required for the analysis.

- **patentsviewAPI**: puts together the query string, the output fields string and the options string, and then extracts and saves the data returned by the PatentsView API in json format. To do so, calls on the following functions:
  - **query**: Forms query filters string to pass into **get_data**.
  - **get_data** : Extract and save data from the PatentsView API to disk.

- **load_data**: preprocesses the raw json data from the PatentsView API for a given range (For our purposes, we call it for the time range 1990-2016). To do so, calls on the following functions:
  - **get_full_year_data**: Fetches PatentsView data for a full year, one quarter at a time, to deal with the PatentsView query-limits. To do so, calls on **patentsviewAPI**
  - **preprocess_data**: Preprocesses saved json data to the format used for the data analysis.
  
- **get_ts**: Extracts time series data from the loaded and preprocessed dataset.

- **get_all_locations**: Returns list of locations and the number of inventors at each location for the given data, in the format required by the Folium heatmap plugin.

- **get_top_k_locations**: Returns list of locations and the number of inventors at each location, considering only the data from the top k assignees, ranked by number of patent applications.

- **get_assignee_ts**: Returns the time series of the number of inventors for the specified assignees

- **load_layers_data**: Loads preprocessed data from disk and converts some of the data from json format to Pandas DataFrame. To do so, calls on the following functions:
  - **get_layers_data**: Fetches all data from disk, one layer at a time. To do so, calls on:
    - **get_cited_patents_data**: Fetches the data for the given list of patent_numbers from the PatentsView API - using the function **patentsviewAPI** - and saves the raw data to disk.
    - **preprocess_layer_data**: Preprocesses saved raw json data from disk to the format used for the data analysis.

### visualizations.py
This python file contains all the functions to create the visuals which are included in the data story.

- **get_html**: Produces HTML rendering of Folium map of the distribution of the inventors, for the given type (All Assignees, All or top K US Assignees, or All or top K Non-US Assignees) for the given year, and saves it to working directory.
  
- **get_timeseries_fig**: Produces a figure containing various time series plots and saves to working directory.

- **get_assignees_plot**: Produces a figure comparing the time series plots of the number of inventors for two lists of assignees, and saves to working directory.

- **save_layers**: Produce HTML rendering of Folium map of the distribution of the inventors in each layer of the network supporting a specific patent.


## Plan for the weeks to come

