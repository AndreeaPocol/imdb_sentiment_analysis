import json
import csv
import numpy as np
import scipy.stats as sts
from scipy.optimize import curve_fit
from re import sub
import seaborn as sns
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer


sia = SentimentIntensityAnalyzer()
englishSpeakingCountries = ["Australia", "New Zealand", "UK", "USA"]
genresToConsider = {
    "Horror": [],
    "Romance": [],
    "Comedy": [],
    "Action": [],
    "Adventure": [],
    "Animation": [],
    "Crime": [],
}


def releasedInEnglishSpeakingCountry(countries):
    for country in countries:
        if country in englishSpeakingCountries:
            return True
    return False


def addMoviesToGenreLists(plot, compoundScore, revenue, movieGenres):
    for genre in movieGenres:
        if genre in genresToConsider.keys():
            movie = {"Plot": plot, "CompoundScore": compoundScore, "Revenue": revenue}
            genresToConsider[genre].append(movie)


def presentResults(sentimentScore, boxOfficeRevenue, genre):
    # compute Pearson correlation coefficient
    if (len(sentimentScore) < 2) or (len(boxOfficeRevenue) < 2):
        print("Not enough movies to present {genre} results".format(genre=genre))
        return
    if len(sentimentScore) != len(boxOfficeRevenue):
        print("Number of sentiment score points doesn't equal number of revenue points")
        return
    pearsonCorCoef, pValue = sts.pearsonr(sentimentScore, boxOfficeRevenue)
    print(
        "Pearson correlation coefficient: {pearsonCorCoef}, p-value: {pValue}".format(
            pearsonCorCoef=pearsonCorCoef, pValue=pValue
        )
    )

    # graph results
    fig = plt.figure()
    plt.plot(sentimentScore, boxOfficeRevenue, "o", color="black")

    title = "The Effect of {genre} Movie Summary Sentiment Score on Box Office Revenue".format(
        genre=genre
    )
    filename = "sentiment_score_vs_box_office_revenue_{genre}_genre".format(
        genre=genre.lower()
    )
    fig.suptitle(title, wrap=True)
    plt.xlabel("Summary Sentiment Score")
    plt.ylabel("Box Office Revenue")
    plt.savefig(filename + ".png")
    plt.show()

    # write results
    points = zip(sentimentScore, boxOfficeRevenue)
    header = ["Sentiment Score", "Box Office Revenue"]
    with open(filename + ".csv", "w+") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=",")
        filewriter.writerow(header)
        filewriter.writerows(points)


def processGenres():
    for genre in genresToConsider.keys():
        sentimentScore = []
        boxOfficeRevenue = []
        movies = genresToConsider[genre]
        numMovies = len(movies)
        for movie in movies:
            compoundScore = movie["CompoundScore"]
            revenue = movie["Revenue"]
            boxOfficeRevenue.append(int(revenue))
            sentimentScore.append(int(compoundScore))
        print(
            "Finished processing {numMovies} {genre} movies".format(
                numMovies=numMovies, genre=genre
            )
        )
        presentResults(sentimentScore, boxOfficeRevenue, genre)


def processAllGenres():
    sentimentScore = []
    boxOfficeRevenue = []
    numMovies = 0

    with open("imdb.omdb_rated_movies_1960_2019.json") as f:
        for line in f:
            movie = json.loads(line)
            if (
                "BoxOffice" not in movie
                or "Plot" not in movie
                or "Title" not in movie
                or "Type" not in movie
                or "Country" not in movie
            ):
                continue
            if movie["Type"] != "movie":
                continue
            countries = movie["Country"].split(",")
            if not releasedInEnglishSpeakingCountry(countries):
                continue
            plot = movie["Plot"]
            boxOffice = movie["BoxOffice"]
            if boxOffice == "N/A" or plot == "N/A":
                continue
            numMovies += 1
            revenue = float(sub(r"[^\d.]", "", boxOffice))
            movieGenres = movie["Genre"].split(",")
            compoundScore = sia.polarity_scores(plot)["compound"]
            sentimentScore.append(compoundScore)
            boxOfficeRevenue.append(revenue)
            addMoviesToGenreLists(plot, compoundScore, revenue, movieGenres)
        print("Finished processing {numMovies} movies".format(numMovies=numMovies))

        presentResults(sentimentScore, boxOfficeRevenue, "all")


def main():
    processAllGenres()
    processGenres()


if __name__ == "__main__":
    main()
