import json
import csv
import numpy as np
import scipy.stats as sts
from scipy.optimize import curve_fit
from re import sub
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


def presentResults(sentimentScore, boxOfficeRevenue, genre, sentiment):
    # compute Pearson correlation coefficient
    if (len(sentimentScore) < 2) or (len(boxOfficeRevenue) < 2):
        print("Not enough movies to present {genre} results".format(genre=genre))
        return
    if len(sentimentScore) != len(boxOfficeRevenue):
        print("Number of sentiment score points doesn't equal number of revenue points")
        return
    pearsonCorCoef, pValue = sts.pearsonr(sentimentScore, boxOfficeRevenue)
    print(
        "Pearson correlation coefficient for {num} {sentiment} {genre} summaries: {pearsonCorCoef}, p-value: {pValue}".format(
            num=len(sentimentScore),
            pearsonCorCoef=pearsonCorCoef,
            pValue=pValue,
            sentiment=sentiment,
            genre=genre,
        )
    )

    # graph results
    fig = plt.figure()
    plt.plot(sentimentScore, boxOfficeRevenue, "o", color="black")
    plt.plot(
        np.unique(sentimentScore),
        np.poly1d(np.polyfit(sentimentScore, boxOfficeRevenue, 1))(
            np.unique(sentimentScore)
        ),
    )

    if genre == "All":
        title = (
            "The Effect of Movie Summary Sentiment Score on Box Office Revenue".format(
                genre=genre
            )
        )
    else:
        title = "The Effect of {genre} Movie Summary Sentiment Score on Box Office Revenue".format(
            genre=genre
        )
    filename = "sentiment_score_vs_box_office_revenue_{genre}_genre_{sentiment}_sentiments".format(
        genre=genre.lower(), sentiment=sentiment
    )
    fig.suptitle(title, wrap=True)
    plt.xlabel("Summary Sentiment Score")
    plt.ylabel("Box Office Revenue")
    plt.savefig(filename + ".png")
    # plt.show()

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
        positiveSentimentScore = []
        negativeSentimentScore = []
        revenues = []
        positiveSentimentScoreRevenue = []
        negativeSentimentScoreRevenue = []
        movies = genresToConsider[genre]
        numMovies = len(movies)
        for movie in movies:
            compoundScore = movie["CompoundScore"]
            revenue = movie["Revenue"]
            sentimentScore.append(compoundScore)
            revenues.append(revenue)
            if compoundScore >= 0:
                positiveSentimentScore.append(compoundScore)
                positiveSentimentScoreRevenue.append(revenue)
            if compoundScore <= 0:
                negativeSentimentScore.append(compoundScore)
                negativeSentimentScoreRevenue.append(revenue)
        print(
            "Finished processing {numMovies} {genre} movies".format(
                numMovies=numMovies, genre=genre
            )
        )
        presentResults(sentimentScore, revenues, genre, "both")
        presentResults(
            positiveSentimentScore, positiveSentimentScoreRevenue, genre, "positive"
        )
        presentResults(
            negativeSentimentScore, negativeSentimentScoreRevenue, genre, "negative"
        )


def processSentimentRevenueRelationshipAllGenres():
    sentimentScore = []
    positiveSentimentScore = []
    negativeSentimentScore = []
    revenues = []
    positiveSentimentScoreRevenue = []
    negativeSentimentScoreRevenue = []
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
            revenue = float(sub(r"[^\d.]", "", boxOffice))
            # if revenue < float(50000000):
            #     continue
            numMovies += 1
            movieGenres = movie["Genre"].split(",")
            compoundScore = sia.polarity_scores(plot)["compound"]
            posScore = sia.polarity_scores(plot)["pos"]
            negScore = sia.polarity_scores(plot)["neg"]
            sentimentScore.append(compoundScore)
            revenues.append(revenue)
            if compoundScore >= 0:
                positiveSentimentScore.append(compoundScore)
                positiveSentimentScoreRevenue.append(revenue)
            if compoundScore <= 0:
                negativeSentimentScore.append(compoundScore)
                negativeSentimentScoreRevenue.append(revenue)
            addMoviesToGenreLists(plot, compoundScore, revenue, movieGenres)
        print("Finished processing {numMovies} movies".format(numMovies=numMovies))

        presentResults(sentimentScore, revenues, "All", "both")
        presentResults(
            positiveSentimentScore, positiveSentimentScoreRevenue, "All", "positive"
        )
        presentResults(
            negativeSentimentScore, negativeSentimentScoreRevenue, "All", "negative"
        )


def main():
    processSentimentRevenueRelationshipAllGenres()
    processGenres()


if __name__ == "__main__":
    main()
