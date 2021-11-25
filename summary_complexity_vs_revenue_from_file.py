import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as sts

englishSpeakingCountries = ["Australia", "New Zealand", "UK", "USA"]


def releasedInEnglishSpeakingCountry(countries):
    for country in countries:
        if country in englishSpeakingCountries:
            return True
    return False


def presentResults(summaryComplexity, revenue):
    if (len(summaryComplexity) < 2) or (len(revenue) < 2):
        print("Not enough movies to present results")
        return
    if len(summaryComplexity) != len(revenue):
        print("Number of sentiment score points doesn't equal number of revenue points")
        return

    # graph results
    fig = plt.figure()
    plt.plot(summaryComplexity, revenue, ".", color="black")
    title = "The Effect of Movie Summary Complexity on Movie Revenue"
    fig.suptitle(title, wrap=True)
    # plt.xlabel("Summary Complexity (Gunning Fox Index)")
    plt.xlabel("Summary Complexity (Smog Index)")
    plt.ylabel("Box Office Revenue")
    # plt.savefig("summary_gunning_fog_complexity_vs_revenue.png")
    plt.savefig("summary_smog_complexity_vs_revenue.png")
    plt.show()


def processSummaryComplexityRevenueRelationshipAllGenres():
    numMovies = 0
    # data = pd.read_csv("summary_gunning_fog_complexity_vs_revenue.csv", ",")
    data = pd.read_csv("summary_smog_complexity_vs_revenue.csv", ",")

    print("Finished processing {numMovies} movies".format(numMovies=numMovies))
    print(data.columns)
    presentResults(data.ComplexityScore, data.BoxOfficeRevenue)


def main():
    processSummaryComplexityRevenueRelationshipAllGenres()


if __name__ == "__main__":
    main()