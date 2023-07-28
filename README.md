Paper: [https://ieeexplore.ieee.org/abstract/document/9898114](https://ieeexplore.ieee.org/abstract/document/9898114)

This is a suite of scripts offering insight into the most lucrative properties of films.
Big data is harnessed to produce simple and clear visualizations.
Data is aggregated from IMDb, TMDb, and OMDb, and revenues are adjusted for inflation. 

The following is a list of all scripts included in this repository. 
Ensure `imdb.omdb_rated_movies_1960_2019.json` containing all movies resides in the same directory as whatever script you wish to run.
This data is not provided in the repository but can be obtained with a subscription to a database like IMDb.

# Genre vs Revenue
Run:
```
python3 revenue_and_genre.py
```

Output:
Produces a graph illustrating the effect of movie genre on average box office revenue


# Genre vs Sentiment
Run:
```
sentiment_and_genre.py
```

Output:
Produces a graph illustrating the effect of movie genre on average sentiment of the summary


# Sentiment vs Revenue
Run:
```
python3 sentiment_and_revenue.py
```
Parameters:
- `filter`: Decide whether or not to filter out movies with a runtime of less than 75 minute and revenue less than $1,000,000. If so, set to True.
- `loaf`, `cob1`, `cobf2`, `cobf3`: Decide whether you want a line of best fit or one of the options for curve of best fit. Set your choice and your choice only to True.
- `save`: Decide whether you want to save the resulting graph as a PNG. If so, set to True.
- `write`: Decide whether you want to save the results as a CSV file. If so, set to True.

Output:
Produces a graph illustrating the effect of movie summary sentiment on box office revenue, for all genres as well as for each genre. Pearson correlation coefficients and p-values are also provided.


# Summary Length vs Revenue
Run:
```
python3 summary_length_and_revenue.py
```

Output:
Produces a graph illustrating the effect of summary length (in words) on box office revenue


# Summary Complexity vs Revenue
Run:
```
python3 summary_complexity_vs_revenue.py
```
Parameters:
- `fleschKincaid`, `gunningFog`: Decide which readability index you want to use. Set that method and that method only to True. 

Output:
Produces a CSV file illustrating the effect of summary complexity (readability score) on box office revenue

Run:
```
python3 summary_complexity_vs_revenue_from_file.py
```
after running:
```
python3 summary_complexity_vs_revenue.py
```
Parameters:
- `fleschKincaid`, `gunningFog`: Decide which readability index you want to use. Set that method and that method only to True. The CSV file (produced as output from the summary_complexity_vs_revenue.py script) must exist in the running directory.

Output:
Produces a graph illustrating the effect of summary complexity (readability score) on box office revenue

See accompanying paper (coming soon) for results.
