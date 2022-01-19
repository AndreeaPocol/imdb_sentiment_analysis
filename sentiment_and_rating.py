import json
import csv
import curve_of_best_fit as cobf
import numpy as np
import scipy.stats as sts
from scipy.optimize import curve_fit
from re import sub
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer
import adjust_revenue_for_inflation as arfi
from constants import *


filter = True  # filter based on runtime and revenue
write = True  # write resuls to CSV file
save = True  # save results as PNG
# curve / line of best fit
lobf = False  # polyfit, degree 1
cobf1 = False  # curve_fit
cobf2 = False  # https://stackoverflow.com/a/51975675
cobf3 = False  # polyfit, degree 3

minNumVotes = 100  # [100, 500, 1000]
sia = SentimentIntensityAnalyzer()


def releasedInCountryOfInterest(countries):
    for country in countries:
        if country in countriesOfInterest:
            return True
    return False


def addMoviesToGenreLists(compoundScore, rating, movieGenres):
    for genre in movieGenres:
        if genre in genresToConsider.keys():
            movie = {"Rating": rating, "CompoundScore": compoundScore}
            genresToConsider[genre].append(movie)


def func(x, a, b, c):
    return a * np.exp(-b * np.array(x)) + c


def presentResults(sentimentScores, ratings, genre):
    # compute Pearson correlation coefficient
    if (len(sentimentScores) < 2) or (len(ratings) < 2):
        print("Not enough movies to present {genre} results".format(genre=genre))
        return
    if len(sentimentScores) != len(ratings):
        print("Number of sentiment score points doesn't equal number of rating points")
        return
    pearsonCorCoef, pValue = sts.pearsonr(sentimentScores, ratings)
    print(
        "Pearson correlation coefficient for {num} {genre} summaries: {pearsonCorCoef}, p-value: {pValue}".format(
            num=len(sentimentScores),
            pearsonCorCoef=pearsonCorCoef,
            pValue=pValue,
            genre=genre,
        )
    )

    plotTitle = (
        "The Effect of {genre} Movie Summary Sentiment Score on IMDb Rating".format(
            genre=genre
        )
    )
    xLabel = "Summary Sentiment Score"
    yLabel = "IMDb Rating"

    suffix = "other"
    if countriesOfInterest == englishSpeakingCountries:
        suffix = "english"
    elif countriesOfInterest == india:
        suffix = "india"
    elif countriesOfInterest == china:
        suffix = "china"
    elif countriesOfInterest == europeanCountries:
        suffix = "european"

    if filter:
        filename = "sentiment_score_vs_imdb_rating_{genre}_genre_sentiments_filtered_{countries}".format(
            genre=genre.lower(), countries=suffix
        )
    else:
        filename = "sentiment_score_vs_imdb_rating_{genre}_genre_sentiments_{countries}".format(
            genre=genre.lower(), countries=suffix
        )

    # graph results
    fig = plt.figure()
    plt.plot(sentimentScores, ratings, ".", color="black")

    if lobf:
        # Plot line of best fit
        plt.plot(
            sentimentScores,
            np.poly1d(np.polyfit(sentimentScores, ratings, 1))(sentimentScores),
        )
    elif cobf1:
        # Plot curve of best fit (1)
        try:
            popt, pcov = curve_fit(func, sentimentScores, ratings)
            plt.plot(
                sentimentScores,
                func(sentimentScores, *popt),
                "r-",
                label="fit: a=%5.3f, b=%5.3f, c=%5.3f" % tuple(popt),
            )
        except:
            print("Couldn't fit {genre} data".format(genre=genre))
            pass
    elif cobf2:
        # Plot curve of best fit (2)
        cobf.plotCurveOfBestFit(
            sentimentScores, ratings, plotTitle, xLabel, yLabel, filename
        )
    elif cobf3:
        # Plot curve of best fit
        plt.plot(
            np.unique(sentimentScores),
            np.poly1d(np.polyfit(sentimentScores, ratings, 3))(
                np.unique(sentimentScores)
            ),
        )

    if genre == "All":
        title = "The Effect of Movie Summary Sentiment Score on IMDb Rating"
    else:
        title = plotTitle

    fig.suptitle(title, wrap=True)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    if save:
        plt.savefig(filename + ".png")
    plt.show()

    # write results
    if write:
        points = zip(sentimentScores, ratings)
        header = ["Sentiment Score", "IMDbRating"]
        with open(filename + ".csv", "w+") as csvfile:
            filewriter = csv.writer(csvfile, delimiter=",")
            filewriter.writerow(header)
            filewriter.writerows(points)


def processGenres():
    for genre in genresToConsider.keys():
        sentimentScores = []
        ratings = []
        movies = genresToConsider[genre]
        numMovies = len(movies)
        for movie in movies:
            compoundScore = movie["CompoundScore"]
            rating = movie["Rating"]
            sentimentScores.append(compoundScore)
            ratings.append(rating)
        print(
            "Finished processing {numMovies} {genre} movies".format(
                numMovies=numMovies, genre=genre
            )
        )
        presentResults(sentimentScores, ratings, genre)


def processSentimentRevenueRelationshipAllGenres():
    sentimentScores = []
    ratings = []
    numMovies = 0

    with open("imdb.omdb_rated_movies_1960_2019.json") as f:
        for line in f:
            movie = json.loads(line)
            if (
                "imdbRating" not in movie
                or "imdbVotes" not in movie
                or "Plot" not in movie
                or "Title" not in movie
                or "Type" not in movie
                or "Country" not in movie
            ):
                continue
            if filter:
                if "Runtime" not in movie:
                    continue
            countries = movie["Country"].split(",")
            plot = movie["Plot"]
            votes = movie["imdbVotes"]
            rating = movie["imdbRating"]
            if filter:
                runTime = movie["Runtime"]
            type = movie["Type"]
            if plot == "N/A" or rating == "N/A" or votes == "N/A":
                continue
            if filter:
                if runTime == "N/A":
                    continue
            if type != "movie":
                continue
            if not releasedInCountryOfInterest(countries):
                continue
            if filter:
                if int(runTime.split(" ")[0].replace(",", "")) < 75.0:
                    continue
            numVotes = float(sub(r"[^\d.]", "", votes))
            if filter:
                if "BoxOffice" not in movie:
                    continue
                boxOffice = movie["BoxOffice"]
                if boxOffice == "N/A":
                    continue
                revenue = float(sub(r"[^\d.]", "", boxOffice))
                if revenue < 1000000:
                    continue
            if numVotes < minNumVotes:
                continue
            rating = float(sub(r"[^\d.]", "", rating))
            numMovies += 1
            movieGenres = movie["Genre"].split(",")
            compoundScore = sia.polarity_scores(plot)["compound"]
            sentimentScores.append(compoundScore)
            ratings.append(rating)
            addMoviesToGenreLists(compoundScore, rating, movieGenres)
        print("Finished processing {numMovies} movies".format(numMovies=numMovies))

        presentResults(sentimentScores, ratings, "All")


def main():
    processSentimentRevenueRelationshipAllGenres()
    processGenres()


if __name__ == "__main__":
    main()
