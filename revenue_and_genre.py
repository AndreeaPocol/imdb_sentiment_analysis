import json
import statistics
import matplotlib.pyplot as plt
from re import sub
import adjust_revenue_for_inflation as arfi
from constants import *
import numpy as np


def addMoviesToGenreLists(revenue, movieGenres):
    for genre in movieGenres:
        if genre in genresToConsider.keys():
            genresToConsider[genre].append(revenue)


def mean(arr):
    avg = 0
    t = 1
    for x in arr:
        avg += (x - avg) / t
        t = t + 1
    return avg


def presentResults():
    genres = []
    averageRevenue = []
    for genre, revenue in genresToConsider.items():
        avg = statistics.mean(revenue)
        genres.append(genre)
        averageRevenue.append(avg)

    mins = []
    maxes = []
    means = []
    stds = []

    title = "The Effect of Movie Genre on Box Office Revenue"

    # graph results in a box plot
    fig = plt.figure()
    fig.suptitle(title, wrap=True)
    filename = "genre_vs_revenue_boxplot"
    plt.xlabel("Genre")
    plt.ylabel("Box Office Revenue")
    idx = 0
    for genre, revenue in genresToConsider.items():
        plt.boxplot(revenue, positions=[idx], showfliers=False)
        mins.append(min(revenue))
        maxes.append(max(revenue))
        means.append(np.mean(revenue))
        stds.append(np.std(revenue))
        idx = idx + 1
    plt.xticks(list(range(len(genres))), genres)
    plt.savefig(filename + ".png")
    plt.show()

    # graph results in a stacked errorbar plot
    fig = plt.figure()
    fig.suptitle(title, wrap=True)
    filename = "genre_vs_revenue_errorbar_plot"
    plt.xlabel("Genre")
    plt.ylabel("Box Office Revenue")
    minsToMeans = [a_i - b_i for a_i, b_i in zip(means, mins)]
    meansToMaxes = [a_i - b_i for a_i, b_i in zip(maxes, means)]
    plt.errorbar(np.arange(len(genres)), means, stds, fmt="ok", lw=3)
    plt.errorbar(
        np.arange(len(genres)),
        means,
        [minsToMeans, meansToMaxes],
        fmt=".k",
        ecolor="gray",
        lw=5,
    )
    plt.yscale("log")
    plt.xticks(list(range(len(genres))), genres)
    plt.savefig(filename + ".png")
    plt.show()

    # graph results in a bar plot
    fig = plt.figure()
    plt.bar(genres, averageRevenue, color="black", width=0.4)
    title = "Average Box Office by Genre"
    filename = "genre_vs_average_revenue"
    fig.suptitle(title, wrap=True)
    plt.xlabel("Genre")
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(["${:1,.0f}".format(x) for x in current_values])
    idx = 0
    for genre, revenue in genresToConsider.items():
        idx = idx + 1
    BlockColours()
    plt.tight_layout()
    plt.savefig(filename + ".png")
    plt.show()

    # average revenue across all films
    revenues = []
    for genre, revenue in genresToConsider.items():
        revenues += revenue
    print("Average revenue for all films: {}".format(mean(revenues)))


def BlockColours():
    plt.axhspan(0, 10000000, facecolor="red", alpha=0.3, zorder=0)
    plt.axhspan(10000000, 25000000, facecolor="orange", alpha=0.3, zorder=0)
    plt.axhspan(25000000, 50000000, facecolor="yellow", alpha=0.3, zorder=0)
    plt.axhspan(50000000, 100000000, facecolor="green", alpha=0.3, zorder=0)
    plt.axhspan(100000000, 150000000, facecolor="blue", alpha=0.3, zorder=0)


def processSentimentRevenueRelationshipAllGenres():
    numMovies = 0
    with open("imdb.omdb_rated_movies_1960_2019.json") as f:
        for line in f:
            movie = json.loads(line)
            if (
                "BoxOffice" not in movie
                or "Type" not in movie
                or "Country" not in movie
                or "Year" not in movie
            ):
                continue
            if movie["Type"] != "movie":
                continue
            countries = movie["Country"].split(",")
            if not releasedInCountryOfInterest(countries):
                continue
            if movie["BoxOffice"] == "N/A":
                continue
            revenue = float(sub(r"[^\d.]", "", movie["BoxOffice"]))
            releaseYear = movie["Year"]
            revenue = arfi.adjustRevenueForInflation(revenue, releaseYear)
            # if revenue < 1000000:
            #     continue
            movieGenres = movie["Genre"].split(",")
            addMoviesToGenreLists(revenue, movieGenres)
            numMovies += 1

        print("Finished processing {numMovies} movies".format(numMovies=numMovies))
        presentResults()


def main():
    processSentimentRevenueRelationshipAllGenres()


if __name__ == "__main__":
    main()
