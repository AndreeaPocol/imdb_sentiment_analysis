englishSpeakingCountries = ["Australia", "New Zealand", "UK", "USA", "Canada"]
china = ["China"]
india = ["India"]
europeanCountries = [
    "France",
    "Spain",
    "Italy",
    "West Germany",
    "East Germany",
    "Poland",
    "Switzerland",
    "Portugal",
    "Austria",
    "Denmark",
]
countriesOfInterest = englishSpeakingCountries
# countriesOfInterest = china
# countriesOfInterest = india
# countriesOfInterest = europeanCountries

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

numericGenresToConsider = {
    "Horror": 1,
    "Romance": 2,
    "Comedy": 3,
    "Action": 4,
    "Adventure": 5,
    "Animation": 6,
    "Crime": 7,
    "Drama": 8,
}


def releasedInCountryOfInterest(countries):
    for country in countries:
        if country in countriesOfInterest:
            return True
    return False
