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
import statistics as stats

# sns.set_theme()
filter = False  # filter based on runtime and revenue
write = False  # write resuls to CSV file
save = False  # save results as PNG
# curve / line of best fit
lobf = False  # polyfit, degree 1
cobf1 = False  # curve_fit
cobf2 = False  # https://stackoverflow.com/a/51975675
cobf3 = False  # polyfit, degree 3
sia = SentimentIntensityAnalyzer()


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
    avg = np.mean(boxOfficeRevenue)
    stdev = np.std(boxOfficeRevenue)
    print("Average revenue for all movies: {}, stdev: {}".format(avg, stdev))
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
    if filter:
        filename = "sentiment_score_vs_box_office_revenue_{genre}_genre_sentiments_filtered".format(
            genre=genre.lower()
        )
    else:
        filename = (
            "sentiment_score_vs_box_office_revenue_{genre}_genre_sentiments".format(
                genre=genre.lower()
            )
        )
    # Colourmap
    from matplotlib.colors import ListedColormap

    N = len(np.arange(255, 0, -5))
    vals = np.ones((N, 4))
    vals[:, 0] = np.arange(255, 0, -5) / 256
    # np.ones(np.arange(  np.linspace(100/256,1,N)
    vals[:, 1] = (np.arange(255, 0, -5)) / 256  # np.linspace(100/256,1,N)
    vals[:, 2] = np.ones(N)  # np.linspace(100/256,1,N)
    newcmp = ListedColormap(vals)
    # heat map with matplotlib
    fig = plt.figure()
    if genre == "All":
        title = "The Effect of Movie Summary Sentiment Score on Box Office Revenue"
    else:
        title = plotTitle
    fig.suptitle(title, wrap=True)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel + " $10^y")
    x = np.array(sentimentScore)
    y = np.array(boxOfficeRevenue)
    yLog = np.log10(np.array(boxOfficeRevenue))
    avgbox = np.log10(stats.mean(y)) * np.ones(len(y))
    avgsent = stats.mean(x) * np.ones(len(x))
    hm = plt.hist2d(x, yLog, cmap=newcmp, bins=15)
    plt.plot(x, avgbox, "r")
    plt.plot(avgsent, yLog, "k")
    plt.xticks(np.arange(-1, 1.25, 0.25))
    plt.colorbar()
    plt.tight_layout()
    if save:
        plt.savefig(filename + "_heatmap.png")
    # plt.show()

    # scatter plots
    fig = plt.figure()
    plt.plot(sentimentScore, boxOfficeRevenue, ".", color="black")
    if lobf:
        # Plot line of best fit
        plt.plot(
            np.unique(sentimentScore),
            np.poly1d(np.polyfit(sentimentScore, boxOfficeRevenue, 1))(
                np.unique(sentimentScore)
            ),
        )
    elif cobf1:
        # Plot curve of best fit (1)
        try:
            popt, pcov = curve_fit(func, sentimentScore, boxOfficeRevenue)
            plt.plot(
                sentimentScore,
                func(sentimentScore, *popt),
                "r-",
                label="fit: a=%5.3f, b=%5.3f, c=%5.3f" % tuple(popt),
            )
        except:
            print("Couldn't fit {genre} data".format(genre=genre))
            pass
    elif cobf2:
        # Plot curve of best fit (2)
        cobf.plotCurveOfBestFit(
            sentimentScore, boxOfficeRevenue, plotTitle, xLabel, yLabel, filename
        )
    elif cobf3:
        # Plot curve of best fit
        plt.plot(
            np.unique(sentimentScore),
            np.poly1d(np.polyfit(sentimentScore, boxOfficeRevenue, 3))(
                np.unique(sentimentScore)
            ),
        )
    if genre == "All":
        title = "The Effect of Movie Summary Sentiment Score on Box Office Revenue"
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
                or "Year" not in movie
            ):
                continue
            if filter:
                if "Runtime" not in movie:
                    continue
            countries = movie["Country"].split(",")
            plot = movie["Plot"]
            boxOffice = movie["BoxOffice"]
            if filter:
                runTime = movie["Runtime"]
            type = movie["Type"]
            if boxOffice == "N/A" or plot == "N/A":
                continue
            if filter:
                if runTime == "N/A":
                    continue
            if type != "movie":
                continue
            if filter:
                if int(runTime.split(" ")[0]) < 75.0:
                    continue
            if not releasedInCountryOfInterest(countries):
                continue
            revenue = float(sub(r"[^\d.]", "", boxOffice))
            releaseYear = movie["Year"]
            revenue = arfi.adjustRevenueForInflation(revenue, releaseYear)
            if filter:
                if revenue < 1000000:
                    continue
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
