Download files from https://datasets.imdbws.com/

Schema description at https://www.imdb.com/interfaces/

Update title_basics table to be able do search
```sh
psql 'dbname=imdb user=imdb options=--search-path=imdb' -f patch-0.1.sql
```