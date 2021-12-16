import json
import statistics
import matplotlib.pyplot as plt
from re import sub
import adjust_revenue_for_inflation as arfi

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


def addMoviesToGenreLists(revenue, movieGenres):
    for genre in movieGenres:
        if genre in genresToConsider.keys():
            genresToConsider[genre].append(revenue)


def presentResults():
    genres = []
    averageRevenue = []
    for genre, revenue in genresToConsider.items():
        avg = statistics.mean(revenue)
        genres.append(genre)
        averageRevenue.append(avg)

    # graph results
    fig = plt.figure()
    plt.bar(genres, averageRevenue, color="maroon", width=0.4)
    title = "The Effect of Movie Genre on Box Office Revenue"
    filename = "genre_vs_average_revenue"
    fig.suptitle(title, wrap=True)
    plt.xlabel("Genre")
    plt.ylabel("Average Box Office Revenue")
    plt.savefig(filename + ".png")
    plt.show()


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
            if not releasedInEnglishSpeakingCountry(countries):
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
