import json
import statistics
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer
from constants import *


sia = SentimentIntensityAnalyzer()


def addMoviesToGenreLists(plot, movieGenres):
    for genre in movieGenres:
        if genre in genresToConsider.keys():
            compoundScore = sia.polarity_scores(plot)["compound"]
            genresToConsider[genre].append(compoundScore)


def presentResults():
    genres = []
    averageScores = []
    for genre, scoreList in genresToConsider.items():
        avg = statistics.mean(scoreList)
        genres.append(genre)
        averageScores.append(avg)

    # graph results
    fig = plt.figure()
    plt.bar(genres, averageScores, color="black", width=0.4)
    title = "Average Movie Summary Sentiment Score by Genre"
    filename = "genre_vs_average_sentiment_score"
    fig.suptitle(title, wrap=True)
    plt.xlabel("Genre")
    plt.ylabel("Average Summary Sentiment Score")
    BlockColours()
    plt.savefig(filename + ".png")
    plt.show()


def BlockColours():
    plt.axhspan(-0.5, -0.4, facecolor="blue", alpha=0.4, zorder=0)
    plt.axhspan(-0.4, -0.3, facecolor="blue", alpha=0.3, zorder=0)
    plt.axhspan(-0.3, -0.2, facecolor="blue", alpha=0.2, zorder=0)
    plt.axhspan(-0.2, -0.1, facecolor="blue", alpha=0.1, zorder=0)
    plt.axhspan(-0.1, 0, facecolor="blue", alpha=0.05, zorder=0)
    plt.axhspan(0, 0.1, facecolor="red", alpha=0.1, zorder=0)
    plt.axhspan(0.1, 0.2, facecolor="red", alpha=0.2, zorder=0)
    plt.axhspan(0.2, 0.3, facecolor="red", alpha=0.3, zorder=0)


def processSentimentRevenueRelationshipAllGenres():
    numMovies = 0
    with open("imdb.omdb_rated_movies_1960_2019.json") as f:
        for line in f:
            movie = json.loads(line)
            if "Plot" not in movie or "Type" not in movie or "Country" not in movie:
                continue
            plot = movie["Plot"]
            if plot == "N/A":
                continue
            if movie["Type"] != "movie":
                continue
            countries = movie["Country"].split(",")
            if not releasedInCountryOfInterest(countries):
                continue
            movieGenres = movie["Genre"].split(",")
            addMoviesToGenreLists(plot, movieGenres)
            numMovies += 1

        print("Finished processing {numMovies} movies".format(numMovies=numMovies))
        presentResults()


def main():
    processSentimentRevenueRelationshipAllGenres()


if __name__ == "__main__":
    main()
