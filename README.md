# IMDBFileProcessor

A python module to parse the public IMDB plain text data files into a python dict. Also functionality to write them out as a text data table.

## Requirements
python 2.x or 3.x (recommended)

## Getting the Data
Data files should be downloaded from the IMDB [FTP servers] (http://www.imdb.com/interfaces). For example 
```bash
wget -r -np -l 1 ftp://ftp.fu-berlin.de/pub/misc/movies/database/
```

(The entire files will take about 7GB after extracted).

## Example Usage

```python
from IMDBFileProcessor import IMDBFileProcessor

data_path = "~/imdb/ftp.fu-berlin.de/pub/misc/movies/database/"
output_path = "output/"

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

A processed output in tab delimited format can be dowloaded from [output](output/).

## Example Analysis

![Correlation](analysis/imdb_corr_heatmap.png)
Some preliminary insights:

  - Clusters of (Mystery, Thriller), (Family, Animation, Short), (Sci_Fi, Fantasy), (History, Biograpgy, Documentary), (Action, Adventure), (Drama, Romance), (History, War), (History, Drama)
  - "rating" is positively correlated with the "length", and negatively correlated with "Short" movies genres.
  - Movies with high revenues get more votes. Short movies tend to get less votes than other genres.
  - but no significant correlation between revenue and rating.
