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
#     "SELECT problem_problem_url from problems"
# )
#
# problemSet = db.fetchall()
# for (problem_problem_url) in problemSet:
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
# for num in range(1, 70):
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
#                     db.execute(
#                         "INSERT INTO problems_tags (problem_id, tag_id) VALUES (?,?)", (problem_id, tagMap[tag])
#                     )
#                 rating = int(row.find("span", attrs={"class": "ProblemRating"}).text.strip())
#                 solved_by = int(row.find("a", attrs={"title": "Participants solved the problem"}).text[2:])
#                 db.execute(
#                     "UPDATE problems SET difficulty_rating = ?, solved_by = ? where problem_id = ?", (rating,
#                                                                                                       solved_by,
#                                                                                                       problem_id)
#                 )
#             print('#%d done' % num)
#         except Exception as e:
#             print(f"Error: {e}")
#             continue
##########################################################################################################

##########################################################################################################
# Print to Markdown table
##########################################################################################################
f = open('problem_table.txt', 'w')

for x in range(800, 5000, 100):
    db.execute("SELECT problem_id, problem_name, problem_url, problem_statement_length, "
               "difficulty_rating, solved_by FROM problems WHERE difficulty_rating = " + str(x) + " AND "
                                                                                                  "problem_statement_length <= 1000 ORDER BY "
                                                                                                  "problem_statement_length")
    problems = db.fetchall()
    if len(problems) >= 1:
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
        f.write("\n\n")
