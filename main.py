import secrets.credentials as secret
import urllib.request
from bs4 import BeautifulSoup
import requests
import time
import hashlib
from tinydb import TinyDB, Query
from urllib.request import urlopen, Request
from pyquery import PyQuery as pq
import html2text
from time import sleep
import mariadb
import sys
import random

##########################################################################################################
# Connect to MariaDB database
##########################################################################################################
try:
    conn = mariadb.connect(
        user=secret.user,
        password=secret.password,
        host=secret.host,
        port=secret.port,
        database=secret.database,
        autocommit=True
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
db = conn.cursor()
##########################################################################################################


##########################################################################################################
# Enter all problems into external database table 'problems'
##########################################################################################################
# url = "https://codeforces.com/api/problemset.problems"
# requestPrefix = str(random.randrange(100000, 1000000))
# apiSigString = hashlib.sha512(
#     (requestPrefix + "/problemset.problems?apiKey=" + secret.apiKey + "&time=" + int(time.time()).__str__() +
#      "#" + secret.apiSecret).encode("utf-8")).hexdigest()
# apiSig = requestPrefix + apiSigString
# params = {"apiKey": secret.apiKey, "time": int(time.time()), "apiSig": apiSig}
# data = requests.get(url, params=params)
# problems = data.json()['result']['problems']
#
# for problem in problems:
#     try:
#         db.execute(
#             "INSERT INTO problems (problem_contest_contest_index, problem_name, problem_type, problem_url) "
#             "VALUES (?,?,?,?,?,?)",
#             (str(problem['contestId']) + problem['index'], int(problem['contestId']), problem['index'], problem['name'],
#              problem['type'],
#              "https://codeforces.com/problemset/problem/" + str(problem['contestId']) + "/" + problem['index']))
#     except mariadb.Error as e:
#         print(f"Error: {e}")
##########################################################################################################


##########################################################################################################
# Find statement lengths of all problems
##########################################################################################################
# db.execute(
#     "SELECT problem_id, problem_url from problems"
# )
#
# problemSet = db.fetchall()
# for (problem_id, problem_url) in problemSet:
#     try:
#         print("Processing: " + problem_id)
#         req = Request(problem_url, headers={'User-Agent': 'Mozilla/5.0'})
#         webpage = urlopen(req).read()
#         html_code = pq(webpage)
#         statement = html_code.find('.problem-statement').remove('.header').remove('.input-specification').remove(
#             '.output-specification').remove('.sample-tests').html()
#         qq = Query()
#         if statement is not None:
#             db.execute(
#                 "UPDATE problems SET problem_statement_length = ? WHERE problem_id = ?",
#                 (len(statement), problem_id))
#     except mariadb.Error as e:
#         print(f"Error: {e}")
#         continue
##########################################################################################################


##########################################################################################################
# Add tags, problem ratings and solved_by
##########################################################################################################
# db.execute("SELECT * FROM tags")
# tags = db.fetchall()
# tagMap = {}
# for (tag_id, tag_key) in tags:
#     tagMap[tag_key] = tag_id
#
# url = "https://codeforces.com/problemset/page/"
#
# for num in range(1, 71):
#     req = urllib.request.urlopen(url + str(num))
#     data = BeautifulSoup(req, "html.parser")
#     for row in data.find_all('tr'):
#         try:
#             problem_id = row.find('a').text.strip()
#
#             db.execute("SELECT problem_id FROM problems WHERE problem_id = ?", (problem_id,))
#             problem = db.fetchall()
#
#             if len(problem) == 1:
#                 tags = list(map(lambda tag: tag.text.strip(), row.findAll("a", attrs={"class": "notice"})))
#
#                 for tag in tags:
#                     try:
#                         db.execute(
#                             "INSERT INTO problems_tags (problem_id, tag_id) VALUES (?,?)", (problem_id, tagMap[tag])
#                         )
#                     except Exception as e:
#                         print(f"Error: {e}")
#                         continue
#                 rating = int(row.find("span", attrs={"class": "ProblemRating"}).text.strip())
#                 solved_by = int(row.find("a", attrs={"title": "Participants solved the problem"}).text[2:])
#                 try:
#                     db.execute(
#                         "UPDATE problems SET difficulty_rating = ?, solved_by = ? where problem_id = ?", (rating,
#                                                                                                           solved_by,
#                                                                                                           problem_id)
#                     )
#                 except Exception as e:
#                     print(f"Error: {e}")
#                     continue
#             print('#%d done' % num)
#         except Exception as e:
#             print(f"Error: {e}")
#             continue
##########################################################################################################

##########################################################################################################
# Print problems by ratings to Markdown table
##########################################################################################################
f = open('problem_table.txt', 'w')
problem_stats_f = open('problem_stats_table.txt', 'w')
stats = {}

for x in range(800, 4000, 100):
    db.execute("SELECT problem_id, problem_name, problem_url, problem_statement_length, "
               "difficulty_rating, solved_by FROM problems WHERE difficulty_rating = " + str(x) + " AND "
                                                                                                  "problem_statement_length <= 1000 ORDER BY "
                                                                                                  "problem_statement_length")
    problems = db.fetchall()
    if len(problems) >= 1:
        f.write("<details>\n"
                "  <summary><span id=" + str(x) + ">" + str(x) + "</span></summary>\n\n"
                )
        f.write("|# | ID | Problem  | Rating |\n"
                "|--- | ---| ----- | ---------- |\n")
        index = 1
        for (problem_id, problem_name, problem_url, problem_statement_length,
             difficulty_rating, solved_by) in problems:
            try:
                f.write(
                    "|" + str(index) + "|" + problem_id + "|[" + problem_name + "](" + problem_url + ")|"
                    + str(difficulty_rating) + "|\n")
            except Exception as e:
                print(f"Error: {e}")
                continue
            index = index + 1
        f.write("</details>")
        f.write("\n\n")
        stats[str(x)] = str(index - 1)

problem_stats_f.write("| Title | Links |\n"
                      "|:---: | :---:|\n"
                      "| Newbie| [800](#700)(" + stats['800'] + ") [900](#800)(" + stats['900'] + ") [1000](#900)(" +
                      stats['1000'] + ") [1100](#1000)(" + stats['1100'] + ")|\n"
                                                                           "| Pupil |  [1200](#1100)(" + stats[
                          '1200'] + ") [1300](#1200)(" + stats['1300'] + ") |\n"
                                                                         "| Specialist|  [1400](#1300)(" + stats[
                          '1400'] + ") [1500](#1400)(" + stats['1500'] + ") |\n"
                                                                         "| Export |  [1600](#1500)(" + stats[
                          '1600'] + ") [1700](#1600)(" + stats['1700'] + ") [1800](#1700)(" + stats['1800'] + ") |\n"
                                                                                                              "| Candidate Master|  [1900](#1800)(" +
                      stats['1900'] + ") [2000](#1900)(" + stats['2000'] + ") |\n"
                                                                           "| Master | [2100](#2000)(" + stats[
                          '2100'] + ") [2200](#2100)(" + stats['2200'] + ")|\n"
                                                                         "| International Master| [2300](#2200)(" +
                      stats['2300'] + ")|\n"
                                      "| Grandmaster| [2400](#2300)(" + stats['2400'] + ") [2500](#2400)(" + stats[
                          '2500'] + ")|\n"
                                    "| International Grandmaster| [2600](#2500)(" + stats['2600'] + ") [2700](#2600)(" +
                      stats['2700'] + ") [2800](#2700)("
                                      "" + stats['2800'] + ") ["
                                                           "2900](#2800)(" + stats[
                          '2900'] + ") |\n"
                                    "| <span id=700>Legendary Grandmaster</span>| [3000](#2900)(" + stats['3000'] +
                      ") [3100](#3000)(" +
                      stats['3100'] + ") [3200](#3100)(" + stats[
                          '3200'] + ") [3300]("
                                    "#3200)(" + stats['3300'] + ") ["
                                                                "3400]("
                                                                "#3300)(" + stats['3400'] + ") ["
                                                                                            "3500](#3400)(" + stats[
                          '3500'] + ") |\n")

##########################################################################################################


##########################################################################################################
# Print index table to Markdown table
##########################################################################################################
