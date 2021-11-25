import json
from re import sub
import csv
import matplotlib.pyplot as plt
from readability import Readability

englishSpeakingCountries = ["Australia", "New Zealand", "UK", "USA"]


def releasedInEnglishSpeakingCountry(countries):
    for country in countries:
        if country in englishSpeakingCountries:
            return True
    return False


def presentResults(summaryComplexity, revenue):
    # write results
    points = zip(summaryComplexity, revenue)
    header = ["ComplexityScore", "BoxOfficeRevenue"]
    # with open("summary_gunning_fog_complexity_vs_revenue.csv", "w+") as csvfile:
    with open("summary_flesch_kincaid_complexity_vs_revenue.csv", "w+") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=",")
        filewriter.writerow(header)
        filewriter.writerows(points)


def processSummaryComplexityRevenueRelationshipAllGenres():
    numMovies = 0
    summaryComplexity = []
    revenue = []
    with open("imdb.omdb_rated_movies_1960_2019.json") as f:
        for line in f:
            movie = json.loads(line)
            if (
                "Plot" not in movie
                or "Type" not in movie
                or "Country" not in movie
                or "BoxOffice" not in movie
            ):
                continue
            if movie["Type"] != "movie":
                continue
            countries = movie["Country"].split(",")
            if not releasedInEnglishSpeakingCountry(countries):
                continue
            if movie["BoxOffice"] == "N/A" or movie["Plot"] == "N/A":
                continue
            boxOffice = float(sub(r"[^\d.]", "", movie["BoxOffice"]))

            plot = movie["Plot"] * 100
            r = Readability(plot)
            # summaryComplexity.append(r.gunning_fog())
            summaryComplexity.append(r.flesch_kincaid())
            revenue.append(boxOffice)
            numMovies += 1
            print("Finished processing {title}".format(title=movie["Title"]))

        print("Finished processing {numMovies} movies".format(numMovies=numMovies))
        presentResults(summaryComplexity, revenue)


def main():
    processSummaryComplexityRevenueRelationshipAllGenres()


if __name__ == "__main__":
    main()
