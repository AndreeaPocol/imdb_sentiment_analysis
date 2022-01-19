import json
import scipy.stats as sts
from re import sub
import matplotlib.pyplot as plt
import adjust_revenue_for_inflation as arfi
from constants import *


def presentResults(summaryLength, revenue):
    # compute Pearson correlation coefficient
    if (len(summaryLength) < 2) or (len(revenue) < 2):
        print("Not enough movies to present results")
        return
    if len(summaryLength) != len(revenue):
        print("Number of sentiment score points doesn't equal number of revenue points")
        return
    pearsonCorCoef, pValue = sts.pearsonr(summaryLength, revenue)
    print(
        "Pearson correlation coefficient for {num} summaries: {pearsonCorCoef}, p-value: {pValue}".format(
            num=len(summaryLength),
            pearsonCorCoef=pearsonCorCoef,
            pValue=pValue,
        )
    )
    # graph results
    fig = plt.figure()
    plt.plot(summaryLength, revenue, ".", color="black")

    title = "The Effect of Movie Summary Length on Movie Revenue"
    fig.suptitle(title, wrap=True)
    plt.xlabel("Summary Length (Number of Words)")
    plt.ylabel("Box Office Revenue")
    plt.savefig("summary_length_vs_revenue.png")
    plt.show()


def processSummaryLengthRevenueRelationshipAllGenres():
    numMovies = 0
    summaryLength = []
    revenue = []
    with open("imdb.omdb_rated_movies_1960_2019.json") as f:
        for line in f:
            movie = json.loads(line)
            if (
                "Plot" not in movie
                or "Type" not in movie
                or "Country" not in movie
                or "BoxOffice" not in movie
                or "Year" not in movie
            ):
                continue
            if movie["Type"] != "movie":
                continue
            countries = movie["Country"].split(",")
            if not releasedInCountryOfInterest(countries):
                continue
            if (
                # runTime == "N/A" or
                movie["BoxOffice"] == "N/A"
                or movie["Plot"] == "N/A"
            ):
                continue
            boxOffice = float(sub(r"[^\d.]", "", movie["BoxOffice"]))
            releaseYear = movie["Year"]
            boxOffice = arfi.adjustRevenueForInflation(boxOffice, releaseYear)
            plot = movie["Plot"]
            numWords = len(plot.split())
            summaryLength.append(numWords)
            revenue.append(boxOffice)
            numMovies += 1

        print("Finished processing {numMovies} movies".format(numMovies=numMovies))
        presentResults(summaryLength, revenue)


def main():
    processSummaryLengthRevenueRelationshipAllGenres()


if __name__ == "__main__":
    main()
