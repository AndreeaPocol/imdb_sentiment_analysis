import matplotlib.pyplot as plt
import pandas as pd
from constants import *

fleschKincaid = False
gunningFog = True
cobf = True


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
    plt.ylabel("Box Office Revenue")
    if fleschKincaid:
        plt.xlabel("Summary Complexity (Flesch-Kincaid Index)")
        plt.savefig("summary_flesch_kincaid_complexity_vs_revenue.png")
    elif gunningFog:
        plt.xlabel("Summary Complexity (Gunning Fox Index)")
        plt.savefig("summary_gunning_fog_complexity_vs_revenue.png")
    plt.show()


def processSummaryComplexityRevenueRelationshipAllGenres():
    if fleschKincaid:
        data = pd.read_csv("summary_flesch_kincaid_complexity_vs_revenue.csv", ",")
    elif gunningFog:
        data = pd.read_csv("summary_gunning_fog_complexity_vs_revenue.csv", ",")

    presentResults(data.ComplexityScore, data.BoxOfficeRevenue)


def main():
    processSummaryComplexityRevenueRelationshipAllGenres()


if __name__ == "__main__":
    main()
