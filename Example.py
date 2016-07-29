#!/usr/bin/env python

"""
Example usage of IMDBFileProcessor
data files should be downloaded from http://www.imdb.com/interfaces
and extracted to the data_directory
"""

from IMDBFileProcessor import IMDBFileProcessor

__author__ = "Hamid Younesy"
__copyright__ = "Copyright 2016"
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Hamid Younesy"


data_path = "/Users/hyounesy/Downloads/imdb/ftp.fu-berlin.de/pub/misc/movies/database/"
output_path = "/Users/hyounesy/Downloads/"

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

file_processor.save_to_table(
    output_path + "imdb_animations.txt",
    # exclude the director info and mp_aa reason from the output columns
    save_properties=[key for key in IMDBFileProcessor.all_keys if key not in
                     [IMDBFileProcessor.key_director, IMDBFileProcessor.key_mpaa_reason]],
    # only animation movies
    only_movie_genres=['Animation'],
    # exclude output column for genres that have less than 1000 movies
    save_genres_keys=[genre for genre, count in file_processor.genre_count.items() if count > 1000]
)
