Setup python env:

```
virtualenv -p python3 .venv
. .venv/bin/activate
pip install poetry
poetry install
```

Install dependencies for opentracing and jaeger:

```
pip install -U opentracing-utils
pip install jaeger-client
```

Set db url (in alchemy format https://docs.sqlalchemy.org/en/14/core/engines.html#postgresql) via env var:

`export ALCHEMY_URL=postgresql://taras@localhost/taras`

For dev run with

`cd imdb_graphql && FLASK_ENV=development flask run`

for prod run with

`cd imdb_graphql && flask run --host=0.0.0.0`

Go to http://127.0.0.1:5000/imdb enter

```
{
  movie(imdbID: "7040874") {
    __typename,
    imdbID,
    titleType,
    primaryTitle,
    genres,
    averageRating,
    numVotes
  }
}
```

Use search
```
{ 
  titleSearch(title: "Show") {
    imdbID
    titleType
    primaryTitle
    originalTitle
    isAdult
    startYear
    endYear
    runtime
    genres
    averageRating
    numVotes
  }
}
```

name query
```
{
  name(imdbID: "98") {
    imdbID,
    primaryName,
    primaryProfession,
    birthYear,
    deathYear,
    knownForTitles {
      imdbID,
      titleType,
      primaryTitle,
      originalTitle,
      isAdult,
      startYear,
      endYear,
      runtime,
      genres,
      averageRating,
      numVotes,
    }
  }
}
```

Example of nested query
```
{ 
  series(imdbID: "7203552") {
    imdbID
    runtime
    titleType
    primaryTitle
    originalTitle
    isAdult
    startYear
    endYear
    genres
    averageRating
    numVotes
    totalSeasons,
    episodes {
      series {
        episodes {
          series {
            episodes {
              imdbID
              runtime
              titleType
              primaryTitle
              originalTitle
              isAdult
              startYear
              endYear
              genres
              averageRating
              numVotes
              seasonNumber
              episodeNumber
            }
          }
        }
      } 
    }
  } 
}
```

nameSearch query
```
{
  nameSearch(name: "Jen", result:20) {
    imdbID,
    primaryName,
    primaryProfession,
    birthYear,
    deathYear,
    knownForTitles {
      imdbID,
      titleType,
      primaryTitle,
      originalTitle,
      isAdult,
      startYear,
      endYear,
      runtime,
      genres,
      averageRating,
      numVotes,
    }
  }
}
```

rating query
```
{
  rating(imdbID: "198078") {
    imdbID,
    averageRating,
    numVotes
  }
}
```
