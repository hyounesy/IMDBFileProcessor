"""
Processor for parsing information from the imdb datafiles available from:
http://www.imdb.com/interfaces

Information courtesy of IMDb (http://www.imdb.com).
Used with permission: http://www.imdb.com/help/show_leaf?usedatasoftware
"""

import re
import locale
import textwrap
import os.path
import operator
import sys
from CurrencyEstimator import CurrencyEstimator

is_python_2 = sys.version_info < (3, 0)
if is_python_2:
    import io

__author__ = "Hamid Younesy"
__copyright__ = "Copyright 2016"
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Hamid Younesy"


def open_imdb(filename):
    if is_python_2:
        return io.open(filename, 'r', encoding="ISO-8859-1")
    else:
        return open(filename, 'r', encoding="ISO-8859-1")

# Parses and stores movie info in a dictionary structure
class IMDBFileProcessor(object):
    key_year = 'year'
    key_genre = 'genre'
    key_vote_distribution = 'vote_distribution'
    key_votes = "votes"
    key_rating = "rating"
    key_budget = "budget"
    key_revenue = "revenue"
    key_director = 'director'
    key_length = 'length'
    key_country = 'country'
    key_language = 'language'
    key_mpaa = "mpaa"
    key_mpaa_reason = "mpaa_reason"

    all_keys = [
        key_year,
        key_rating,
        key_length,
        key_votes,
        key_vote_distribution,
        key_budget,
        key_revenue,
        key_country,
        key_language,
        key_mpaa,
        key_mpaa_reason,
        key_genre,
        key_director
    ]

    numerical_keys = [
        key_year,
        key_votes,
        key_rating,
        key_budget,
        key_revenue,
        key_length
    ]

    def __init__(self, input_directory):
        self.movies = {}
        self.currency_not_found = {}
        self.enable_print_progress = True
        self.enable_print_mismatch = False
        self.enable_movies = True # by default, process movies
        self.enable_series = False # by default, skip series
        self.enable_mpaa_reason = False # disabled (to save memory)
        self.genre_count = {}
        self.country_count = {}
        self.language_count = {}
        self.mpaa_count = {}

        self.movies_filename = input_directory + "movies.list"
        self.genres_filename = input_directory + "genres.list"
        self.ratings_filename = input_directory + "ratings.list"
        self.business_filename = input_directory + "business.list"
        self.directors_filename = input_directory + "directors.list"
        self.runningtimes_filename = input_directory + "running-times.list"
        self.countries_filename = input_directory + "countries.list"
        self.languages_filename = input_directory + "language.list"
        self.mpaa_filename = input_directory + "mpaa-ratings-reasons.list"
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    # returns list of tuples: [(title, dict), ...]. case insensitive
    def get_movies_startwith(self, phrase):
        return [(k, v) for k, v in self.movies.items() if k.lower().startswith(phrase.lower())]

    # returns list of tuples: [(title, dict), ...]. case insensitive
    def find_movies_contain(self, phrase):
        return [(k, v) for k, v in self.movies.items() if k.lower().find(phrase.lower()) != -1]

    # remove all values for a key property
    def clear_property(self, key_name):
        for mov in self.movies.values():
            mov.pop(key_name, None)

    def check_file_exists(self, filename):
        if not os.path.isfile(filename):
            print("File not found: " + filename)
            return False
        if self.enable_print_progress:
            print("\nProcessing: " + filename)
        return True


    # reads the movies + year
    def read_movies(self):
        if not self.check_file_exists(self.movies_filename):
            return
        duplicates_count = 0
        series_count = 0
        movies_count = 0
        # read movie info: title and year
        with open_imdb(self.movies_filename) as f:
            regex_movie = re.compile("\t+")
            for line in f:
                tokens = regex_movie.split(line)
                if len(tokens) == 2:
                    movie_name = tokens[0].strip()
                    try:
                        movie_year = int(tokens[1])
                    except:
                        # no valid year information
                        movie_year = -1
                        #continue

                    if movie_name.startswith('"'):
                        series_count += 1
                        if not self.enable_series:
                            continue # skip series / tv name
                    else:
                        movies_count += 1
                        if not self.enable_movies:
                            continue  # skip movie

                    if movie_name not in self.movies:
                        self.movies[movie_name] = {self.key_year: movie_year}
                    else:
                        duplicates_count += 1
                elif self.enable_print_mismatch:
                    print(line.strip())
        if self.enable_print_progress:
            print("[done]\nAdded " + str(len(self.movies)) + " titles.")
            if not self.enable_series and series_count > 0:
                print("Skipped " + str(series_count) + " series/tv shows.")
            if not self.enable_movies and movies_count > 0:
                print("Skipped " + str(movies_count) + " movies.")
            if duplicates_count > 0:
                print("Skipped " + str(duplicates_count) + " duplicate titles.")

    # read movie genres: one [movie]\t[genre] per line. can have multiple genres per movie
    def read_genres(self):
        if not self.check_file_exists(self.genres_filename):
            return
        not_found_count = 0
        with open_imdb(self.genres_filename) as f:
            regex_genre = re.compile("\t+")
            movies_count = 0
            for line in f:
                tokens = regex_genre.split(line)
                if len(tokens) == 2:
                    movie_name = tokens[0]
                    movie_genre = tokens[1]
                    movie = self.movies.get(movie_name)

                    if movie is not None:
                        # movie[key_genre] = movie.get(key_genre, []) + [movie_genre.strip()]
                        genre_list = movie.get(self.key_genre, [])
                        if len(genre_list) == 0:
                            movies_count += 1
                        genre = movie_genre.strip()
                        movie[self.key_genre] = genre_list + [genre]
                        self.genre_count[genre] = self.genre_count.get(genre, 0) + 1
                    else:
                        not_found_count += 1
                elif self.enable_print_mismatch:
                    print(line.strip())

        if self.enable_print_progress:
            print("[done]\nAdded genere to " + str(movies_count) + " movies.")
            if not_found_count > 0:
                print("Skipped " + str(not_found_count) + " records for titles not found")
            print("Genre distribution summary:")
            print(textwrap.TextWrapper().fill(str(sorted(self.genre_count.items(),
                                                         key=operator.itemgetter(1), reverse=True))))

    # read movie rating information: vote distribution, votes, rating
    def read_ratings(self):
        if not self.check_file_exists(self.ratings_filename):
            return

        not_found_count = 0
        with open_imdb(self.ratings_filename) as f:
            # example record: '      0000.00005      69   7.8  Zero Hour (2013)'
            regex_rating_title = re.compile("\s*\S{10}\s+[0-9]+\s+[0-9\.]+\s+")
            regex_rating = re.compile("\s+")
            movies_count = 0
            for line in f:
                title_match = regex_rating_title.match(line)
                if title_match is not None:
                    movie_title = line[title_match.end():].strip()
                    movie = self.movies.get(movie_title)
                    if movie is not None:
                        movie_rating_items = regex_rating.split(line[:title_match.end()].strip())
                        if movie_rating_items is not None:
                            if len(movie_rating_items) == 3:
                                movie[self.key_vote_distribution] = movie_rating_items[0]
                                movie[self.key_votes] = movie_rating_items[1]
                                movie[self.key_rating] = movie_rating_items[2]
                                movies_count += 1
                            else:
                                if self.enable_print_mismatch:
                                    print(line.strip())
                    else:
                        not_found_count += 1
                elif self.enable_print_mismatch:
                    print(line.strip())
            if self.enable_print_progress:
                print("[done]\nAdded ratings to " + str(movies_count) + " movies.")
                if not_found_count > 0:
                    print("Skipped " + str(not_found_count) + " records for titles not found")

    # read movie business information: budget and revenue
    def read_business(self):
        if not self.check_file_exists(self.business_filename):
            return
        movies_count = 0
        not_found_count = 0
        with open_imdb(self.business_filename) as f:
            movie = None
            movie_budget = None
            movie_gross = None
            for line in f:
                """ example:
                -------------------------------------------------------------------------------
                MV: Deadpool (2016)
                BT: USD 58,000,000
                GR: USD 363,024,263 (USA) (5 June 2016)
                GR: USD 754,500,000 (Worldwide) (3 April 2016)
                OW: USD 135,050,000 (USA) (14 February 2016) (3,558 screens)
                -------------------------------------------------------------------------------
                """
                if line.startswith('----------------------------------------------------------'):
                    if movie is not None:
                        if movie_budget is not None:
                            try:
                                movie[self.key_budget] = int(movie_budget)
                            except:
                                pass
                        if movie_gross is not None:
                            try:
                                movie[self.key_revenue] = int(movie_gross)
                            except:
                                pass
                        movies_count += 1
                    movie = None
                    movie_budget = None
                    movie_gross = None
                elif line.startswith('MV: '):
                    movie_title = line[4:].strip()
                    movie = self.movies.get(movie_title)
                    if movie is None:
                        not_found_count += 1
                elif line.startswith('BT:'):
                    try:
                        movie_budget = CurrencyEstimator.exchange(locale.atof(line[8:].split(" ")[0]),
                                                                  line[3:8].strip())
                        #if movie_budget is None:
                        # currency_not_found[line[3:8].strip()] = currency_not_found.get(line[3:8].strip(), 0) + 1
                        # print(movie_title + ": " + line.strip()
                    except:
                        pass
                        # print(movie_title + ": " + line.strip()

                elif line.startswith('GR:'):
                    try:
                        new_gross = CurrencyEstimator.exchange(locale.atof(line[8:].split(" ")[0]),
                                                               line[3:8].strip())
                        if new_gross is not None:
                            if movie_gross is None or new_gross > movie_gross:
                                movie_gross = new_gross  # lazy: assuming max gross is the worldwide revenue
                            # else:
                            # currency_not_found[line[3:8].strip()] = currency_not_found.get(line[3:8].strip(), 0) + 1
                            # print(movie_title + ": " + line.strip()
                    except:
                        pass
                        # print(movie_title + ": " + line
        if self.enable_print_progress:
            print("[done]\nAdded business info to " + str(movies_count) + " movies.")
            if not_found_count > 0:
                print("Skipped " + str(not_found_count) + " records for titles not found")

    # read the movie directors info
    def read_director(self):
        if not self.check_file_exists(self.directors_filename):
            return
        movies_count = 0
        not_found_count = 0
        with open_imdb(self.directors_filename) as f:
            regex_director_movie = re.compile("\t+")
            regex_movie_year = re.compile("\((\d\d\d\d|\?\?\?\?)[^\)]*\)\s*(\(V\)|\(TV\)|\(VG\))*")
            # note: currently ignoring the info at the end of the movie_field enclosed in { }. e.g. the episode number
            current_director = None
            data_started = False

            for line in f:
                line = line.strip()
                tokens = regex_director_movie.split(line)
                movie_field = None
                if len(tokens) == 0:
                    current_director = None
                    continue
                elif len(tokens) == 1:
                    movie_field = tokens[0]
                elif len(tokens) == 2:
                    current_director = tokens[0]
                    movie_field = tokens[1]
                elif self.enable_print_mismatch:
                    print(line)

                if (current_director is not None) and (movie_field is not None):
                    if current_director == "----" and movie_field == "------":
                        # searching for header:
                        """
                        Name			Titles
                        ----			------
                        """
                        data_started = True
                        continue
                    if not data_started:
                        continue
                    movie_title = movie_field
                    if self.movies.get(movie_title) is None:
                        title_match = regex_movie_year.search(movie_field)
                        if title_match is not None:
                            movie_title = movie_field[:title_match.end()].strip()
                    movie = self.movies.get(movie_title)
                    if movie is not None:
                        director_list = movie.get(self.key_director, [])
                        if len(director_list) == 0:
                            movies_count += 1
                        movie[self.key_director] = director_list + [current_director]
                    elif len(movie_title) > 0:
                        not_found_count += 1
        if self.enable_print_progress:
            print("[done]\nAdded director info to " + str(movies_count) + " movies.")
            if not_found_count > 0:
                print("Skipped " + str(not_found_count) + " records for titles not found")

    # read the movie length info
    def read_length(self):
        if not self.check_file_exists(self.runningtimes_filename):
            return
        with open_imdb(self.runningtimes_filename) as f:
            # read movie info: title and length
            regex_time = re.compile("\t+")
            movies_count = 0
            duplicates_count = 0
            not_found_count = 0
            for line in f:
                # examples
                # The Movie (2008)	West Germany:26	(Worldwide Short Film Festival)
                # Werewolf Tales (2003) (V)				USA:80
                line = line.strip()
                tokens = regex_time.split(line)
                if len(tokens) >= 2:
                    try:
                        movie_title = tokens[0].strip()
                        movie = self.movies.get(movie_title)
                        if movie is not None:
                            movie_length = movie.get(self.key_length, -2)
                            if (movie_length != -2):
                                duplicates_count += 1
                            # only if the first length entry for this movie
                            # or if the previous record could not be parsed correctly (-1)
                            if movie_length >= 0:
                                # duplicates  e.g. (uncut, extended, ...) versions (62296 of records)
                                continue
                        else:
                            not_found_count += 1
                            #if self.enable_print_mismatch:
                            #    print("not found movie: " + line
                            continue

                        movie_length = -1
                        try:
                            # simplest case: e.g. 85  (909210 of all records)
                            movie_length =  locale.atof(tokens[1])
                        except:
                            try:
                                # e.g USA:80  (311487 of all records)
                                movie_length = locale.atof(tokens[1][tokens[1].find(":") + 1:])
                            except:
                                try:
                                    # e.g. Canada:10:53  (1039 of all records)
                                    movie_length = (locale.atof(tokens[1].split(":")[1]) +     # minutes
                                                    locale.atof(tokens[1].split(":")[2]) / 60.0) # seconds
                                except:
                                    try:
                                        # all kind of garbage (251 of all records)
                                        # e.g. "USA:10'30", "50 6 episodes", "UK:10x30", "Japan:2 1/2"
                                        # take the first numerical component which works for most cases
                                        movie_length = locale.atof(
                                                            re.split("\s+", re.sub("(\D)", " ", tokens[1]).strip())[0])
                                    except:
                                        pass

                        movie[self.key_length] = movie_length
                        if movie_length >= 0:
                            movies_count += 1

                    except Exception as ex:
                        if self.enable_print_mismatch:
                            print(line)
                            print(ex)
                else:
                    if self.enable_print_mismatch:
                        print(line)
        if self.enable_print_progress:
            print("[done]\nAdded length info to " + str(movies_count) + " movies.")
            print("Skipped " + str(not_found_count) + " records for titles not found")
            print("Skipped " + str(duplicates_count) + " duplicate records.")

    # read country information
    def read_country(self):
        if not self.check_file_exists(self.countries_filename):
            return

        with open_imdb(self.countries_filename) as f:
            # read movie info: title and country
            regex_time = re.compile("\t+")
            movies_count = 0
            duplicates_count = 0
            not_found_count = 0
            for line in f:
                # example: "Jodaeiye Nader az Simin (2011)				Iran"
                line = line.strip()
                tokens = regex_time.split(line)
                if len(tokens) >= 2:
                    try:
                        movie_title = tokens[0].strip()
                        movie = self.movies.get(movie_title)
                        if movie is not None:
                            if self.key_country not in movie:
                                country = tokens[1].strip()
                                self.country_count[country] = self.country_count.get(country, 0) + 1
                                movie[self.key_country] = country
                                movies_count += 1
                            else:
                                duplicates_count += 1
                                continue
                        else:
                            not_found_count += 1
                            # if self.enable_print_mismatch:
                            #    print("not found movie: " + line
                            continue
                    except Exception as ex:
                        if self.enable_print_mismatch:
                            print(line)
                            print(ex)

        if self.enable_print_progress:
            print("[done]\nAdded country info to " + str(movies_count) + " titles.")
            print("Skipped " + str(not_found_count) + " records for titles not found")
            print("Skipped " + str(duplicates_count) + " duplicate titles.")
            print("Country distribution summary:")
            print(textwrap.TextWrapper().fill(str(sorted(self.country_count.items(),
                                                         key=operator.itemgetter(1), reverse=True))))

    # read language information
    def read_language(self):
        if not self.check_file_exists(self.languages_filename):
            return
        with open_imdb(self.languages_filename) as f:
            # read movie info: title and language
            # example: "Jodaeiye Nader az Simin (2011)				Persian"
            regex_time = re.compile("\t+")
            movies_count = 0
            duplicates_count = 0
            not_found_count = 0
            line_count = 0
            for line in f:
                line_count += 1
                line = line.strip()
                tokens = regex_time.split(line)
                if len(tokens) >= 2:
                    try:
                        movie_title = tokens[0].strip()
                        movie = self.movies.get(movie_title)
                        if movie is not None:
                            if self.key_language not in movie:
                                language = tokens[1].strip()
                                self.language_count[language] = self.language_count.get(language, 0) + 1
                                movie[self.key_language] = language
                                movies_count += 1
                            else:
                                duplicates_count += 1
                                continue
                        else:
                            not_found_count += 1
                            # if self.enable_print_mismatch:
                            #    print("not found movie: " + line
                            continue
                    except Exception as ex:
                        if self.enable_print_mismatch:
                            print(line)
                            print(ex)
        if self.enable_print_progress:
            print("\n[done]\nAdded language info to " + str(movies_count) + " titles.")
            print("Skipped " + str(not_found_count) + " records for titles not found")
            print("Skipped " + str(duplicates_count) + " duplicate titles.")
            print("Language distribution summary:")
            print(textwrap.TextWrapper().fill(str(sorted(self.language_count.items(),
                                                         key=operator.itemgetter(1), reverse=True))))

    # read movie mpaa information
    def read_mpaa(self):
        # todo: certificates.list  may contain further rating information
        if not self.check_file_exists(self.mpaa_filename):
            return
        movies_count = 0
        valid_mpaa = {'PG', 'PG-13','R','NV-17'}
        with open_imdb(self.mpaa_filename) as f:
            not_found_count = 0
            duplicates_count = 0
            movie = None
            mpaa_string = ""
            for line in f:
                line = line.strip()
                """ example:
                -------------------------------------------------------------------------------
                MV: The Revenant (2015)
                RE: Rated R for strong frontier combat and violence including gory
                RE: images, a sexual assault, language and brief nudity

                -------------------------------------------------------------------------------
                """
                if line.startswith('---------------------------'):
                    if movie is not None:
                        if self.key_mpaa in movie:
                            duplicates_count += 1
                            continue
                        mpaa_string = mpaa_string.strip()
                        mpaa_reason = mpaa_string
                        idx_rated = mpaa_string.lower().find("rated ")
                        if idx_rated != -1:
                            mpaa_string = mpaa_string[idx_rated+5:].strip()
                        mpaa = mpaa_string.split(" ")[0]
                        if mpaa is not None:
                            if mpaa in valid_mpaa:
                                movie[self.key_mpaa] = mpaa
                            self.mpaa_count[mpaa] = self.mpaa_count.get(mpaa, 0) + 1

                        if self.enable_mpaa_reason and mpaa_reason is not None:
                            movie[self.key_mpaa_reason] = mpaa_reason
                        movies_count += 1
                    movie = None
                    mpaa_string = ""
                elif line.startswith('MV: '):
                    movie_title = line[4:].strip()
                    movie = self.movies.get(movie_title)
                    if movie is None:
                        not_found_count += 1
                elif line.startswith('RE:'):
                    mpaa_string += line[3:].strip() + " "
        if self.enable_print_progress:
            print("[done]\nAdded rating info to " + str(movies_count) + " movies.")
            if not_found_count > 0:
                print("Skipped " + str(not_found_count) + " records for titles not found")
            if duplicates_count > 0:
                print("Skipped " + str(duplicates_count) + " duplicate titles.")
            print("MPAA rating distribution summary:")
            print(textwrap.TextWrapper().fill(str(sorted(self.mpaa_count.items(),
                                                         key=operator.itemgetter(1), reverse=True))))

    # saves the currently processed information into a tab delimited text file
    def save_to_table(self,
                      filename,
                      save_properties=None, # the movie properties (keys) to save
                      save_genres_keys=None, # only include the specified genre information
                      only_movie_genres=None, # only include the movies in the specified genre
                      ignore_movie_genres=None, # ignore if the movie has a genre
                      ignore_when_missing=False, # whether to ignore the movie when any of the specified properties are missing
                      replace_missing_number=-1,
                      replace_missing_text="",
                      output_encoding="utf-8"
                      # todo:
                      # min_year=-1,
                      # max_year=3000,
                      # min_votes=-1,
                      # max_votes=sys.maxint,
                      # min_rating=-1,
                      # max_rating=10,
                      ):

        print("\nSaving table to: " + filename)

        if is_python_2:
            out_file = io.open(filename, "w", encoding=output_encoding)
        else:
            out_file = open(filename, "w", encoding=output_encoding)

        if save_properties is None:
            save_properties = self.all_keys

        if save_genres_keys is None and len(self.genre_count) > 0:
            save_genres_keys = self.genre_count.keys()

        header = "title\t" + re.sub("(\s|\[|\]|')", "", str(save_properties)).replace(",", "\t")
        if self.key_genre in save_properties:
            genres_header = ""
            if len(save_genres_keys) > 0:
                genres_header = re.sub("(\s|\[|\]|')", "", str(save_genres_keys)).replace(",", "\t")
            header = header.replace(self.key_genre, genres_header)

        header += "\n"
        if is_python_2:
            header = unicode(header, encoding=output_encoding, errors='replace')
        out_file.write(header)

        num_rows = 0
        for title, info in self.movies.items():
            line = title
            ignore_movie = False
            for key in save_properties:
                curr_info = info.get(key)
                if key == self.key_genre:
                    curr_info = (curr_info if curr_info is not None else [])
                    for genre in save_genres_keys:
                        line += "\t" + str(1 if genre in curr_info else 0)

                    if only_movie_genres is not None:
                        for genre in curr_info:
                            if genre not in only_movie_genres:
                                ignore_movie = True
                                break

                    if ignore_movie_genres is not None:
                        for genre in curr_info:
                            if genre in ignore_movie_genres:
                                ignore_movie = True
                                break

                    continue
                else:
                    if curr_info is None:
                        if ignore_when_missing:
                            ignore_movie = True
                            break
                        if key in self.numerical_keys:
                            curr_info = replace_missing_number
                        else:
                            curr_info = replace_missing_text

                    if type(curr_info) != str:
                        curr_info = str(curr_info)

                    line += '\t' + curr_info
            if not ignore_movie:
                line += "\n"
                if is_python_2:
                    line = unicode(line, encoding=output_encoding, errors='replace')
                out_file.write(line)
                num_rows += 1

        print("[Done] rows: " + str(num_rows))
        out_file.close()
