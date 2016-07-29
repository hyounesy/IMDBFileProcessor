# IMDBFileProcessor

A python module to parse the IMDB plain text data files into a python dict and writing them out as a text data table.

## Data
Data files should be downloaded from the [IMDB ftp site] (http://www.imdb.com/interfaces).

A processed output in tab delimited format can be dowloaded from [output](output/).

## Example Usage
```python
data_path = "~/imdb/ftp.fu-berlin.de/pub/misc/movies/database/"
output_path = "data/"

file_processor = IMDBFileProcessor(data_path)
file_processor.read_movies()    # requires "movies.list"
file_processor.read_genres()    # requires "genres.list"
file_processor.read_ratings()   # requires "ratings.list"
file_processor.read_business()  # requires "business.list"
file_processor.read_director()  # requires "directors.list"
file_processor.read_length()    # requires "running-times.list"
file_processor.read_country()   # requires "countries.list"
file_processor.read_language()  # requires "language.list"
file_processor.read_mpaa()      # requires "mpaa-ratings-reasons.list"

file_processor.save_to_table(
     output_path + "imdb_movies.txt",
     # to save space, exclude the director info and mpaa_reason from the output columns
     save_properties = [key for key in IMDBFileProcessor.all_keys if key not in
                        [IMDBFileProcessor.key_director, IMDBFileProcessor.key_mpaa_reason]],
     # exclude Adult movies
     ignore_movie_genres=['Adult'],
     # exclude output column for genres that have less than 1000 movies, and Adult genre
     save_genres_keys = [genre for genre, count in file_processor.genre_count.items()
                         if genre not in ['Adult'] and count > 1000]
)
```
## Example Analysis

![Correlation](analysis/imdb_corr_heatmap.png)
