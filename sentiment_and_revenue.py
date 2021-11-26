import json
import csv
import curve_of_best_fit as cobf
import numpy as np
import scipy.stats as sts
from scipy.optimize import curve_fit
from re import sub
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()
englishSpeakingCountries = ["Australia", "New Zealand", "UK", "USA", "Canada"]
genresToConsider = {
    "Horror": [],
    "Romance": [],
    "Comedy": [],
    "Action": [],
    "Adventure": [],
    "Animation": [],
    "Crime": [],
    "Drama": [],
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


def func(x, a, b, c):
    return a * np.exp(-b * np.array(x)) + c


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
        "Pearson correlation coefficient for {num} {genre} summaries: {pearsonCorCoef}, p-value: {pValue}".format(
            num=len(sentimentScore),
            pearsonCorCoef=pearsonCorCoef,
            pValue=pValue,
            genre=genre,
        )
    )

    plotTitle = "The Effect of {genre} Movie Summary Sentiment Score on Box Office Revenue".format(
        genre=genre
    )
    xLabel = "Summary Sentiment Score"
    yLabel = "Box Office Revenue"
    filename = "sentiment_score_vs_box_office_revenue_{genre}_genre_sentiments".format(
        genre=genre.lower()
    )

    # graph results
    fig = plt.figure()
    plt.plot(sentimentScore, boxOfficeRevenue, ".", color="black")

    # # Plot line of best fit
    # plt.plot(
    #     np.unique(sentimentScore),
    #     np.poly1d(np.polyfit(sentimentScore, boxOfficeRevenue, 1))(
    #         np.unique(sentimentScore)
    #     ),
    # )

    # # Plot curve of best fit (1)
    # try:
    #     popt, pcov = curve_fit(func, sentimentScore, boxOfficeRevenue)
    #     plt.plot(
    #         sentimentScore,
    #         func(sentimentScore, *popt),
    #         "r-",
    #         label="fit: a=%5.3f, b=%5.3f, c=%5.3f" % tuple(popt),
    #     )
    # except:
    #     print("Couldn't fit {genre} data".format(genre=genre))
    #     pass

    # # Plot curve of best fit (2)
    # cobf.plotCurveOfBestFit(
    #     sentimentScore, boxOfficeRevenue, plotTitle, xLabel, yLabel, filename
    # )

    # # Log plot
    # plt.yscale("log")

    if genre == "All":
        title = "The Effect of Movie Summary Sentiment Score on Box Office Revenue"
    else:
        title = plotTitle

    fig.suptitle(title, wrap=True)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
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
        revenues = []
        movies = genresToConsider[genre]
        numMovies = len(movies)
        for movie in movies:
            compoundScore = movie["CompoundScore"]
            revenue = movie["Revenue"]
            sentimentScore.append(compoundScore)
            revenues.append(revenue)
        print(
            "Finished processing {numMovies} {genre} movies".format(
                numMovies=numMovies, genre=genre
            )
        )
        presentResults(sentimentScore, revenues, genre)


def processSentimentRevenueRelationshipAllGenres():
    sentimentScore = []
    revenues = []
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
                # or "Runtime" not in movie
            ):
                continue
            countries = movie["Country"].split(",")
            plot = movie["Plot"]
            boxOffice = movie["BoxOffice"]
            runTime = movie["Runtime"]
            type = movie["Type"]
            if (
                # runTime == "N/A" or
                boxOffice == "N/A"
                or plot == "N/A"
            ):
                continue
            if type != "movie":
                continue
            # if int(runTime.split(" ")[0]) < 75.0:
            #     continue
            if not releasedInEnglishSpeakingCountry(countries):
                continue
            revenue = float(sub(r"[^\d.]", "", boxOffice))
            # if revenue < 1000000:
            #     continue
            numMovies += 1
            movieGenres = movie["Genre"].split(",")
            compoundScore = sia.polarity_scores(plot)["compound"]
            sentimentScore.append(compoundScore)
            revenues.append(revenue)
            addMoviesToGenreLists(plot, compoundScore, revenue, movieGenres)
        print("Finished processing {numMovies} movies".format(numMovies=numMovies))

        presentResults(sentimentScore, revenues, "All")


def main():
    processSentimentRevenueRelationshipAllGenres()
    processGenres()


if __name__ == "__main__":
    main()
