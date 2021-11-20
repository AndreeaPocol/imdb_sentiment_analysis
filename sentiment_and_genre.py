import json
import statistics
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
    plt.bar(genres, averageScores, color="maroon", width=0.4)

    title = "The Effect of Genre on Movie Summary Sentiment Score"
    filename = "genre_vs_average_sentiment_score"
    fig.suptitle(title, wrap=True)
    plt.xlabel("Genre")
    plt.ylabel("Average Summary Sentiment Score")
    plt.savefig(filename + ".png")
    plt.show()


def processSentimentRevenueRelationshipAllGenres():
    numMovies = 0
    with open("imdb.omdb_rated_movies_1960_2019.json") as f:
        for line in f:
            movie = json.loads(line)
            if "Plot" not in movie or "Type" not in movie or "Country" not in movie:
                continue
            if movie["Type"] != "movie":
                continue
            countries = movie["Country"].split(",")
            if not releasedInEnglishSpeakingCountry(countries):
                continue
            plot = movie["Plot"]
            movieGenres = movie["Genre"].split(",")
            addMoviesToGenreLists(plot, movieGenres)
            numMovies += 1

        print("Finished processing {numMovies} movies".format(numMovies=numMovies))
        presentResults()


def main():
    processSentimentRevenueRelationshipAllGenres()


if __name__ == "__main__":
    main()
