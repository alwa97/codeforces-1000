#!/usr/bin/env python3
"""
Annual Codeforces Short Problems Update
Run this once per year to get all the latest short problems.

This script:
1. Fetches new problems from Codeforces API
2. Scrapes only NEW problems that need statement lengths
3. Generates updated README with all short problems
4. Uses incremental approach - very fast after first run
"""
import requests
import sqlite3
import time
from urllib.request import urlopen, Request
from pyquery import PyQuery as pq
from datetime import datetime

# Try to import local credentials first, then fall back to template
try:
    import creds.credentials_local as secret
except ImportError:
    import creds.credentials as secret

def get_current_status():
    """Check what we currently have"""
    conn = sqlite3.connect('codeforces.db')
    db = conn.cursor()
    
    # Create tables if they don't exist
    db.execute('''CREATE TABLE IF NOT EXISTS problems (
        problem_id TEXT PRIMARY KEY,
        contest_id INTEGER,
        contest_index TEXT,
        problem_name TEXT,
        problem_type TEXT,
        problem_url TEXT,
        problem_statement_length INTEGER,
        difficulty_rating INTEGER,
        solved_by INTEGER
    )''')
    
    db.execute('''CREATE TABLE IF NOT EXISTS tags (
        tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_key TEXT UNIQUE
    )''')
    
    db.execute('''CREATE TABLE IF NOT EXISTS problems_tags (
        problem_id TEXT,
        tag_id INTEGER,
        FOREIGN KEY (problem_id) REFERENCES problems(problem_id),
        FOREIGN KEY (tag_id) REFERENCES tags(tag_id),
        PRIMARY KEY (problem_id, tag_id)
    )''')
    conn.commit()
    
    db.execute("SELECT COUNT(*) FROM problems")
    total = db.fetchone()[0]
    
    db.execute("SELECT COUNT(*) FROM problems WHERE problem_statement_length <= 1000 AND difficulty_rating IS NOT NULL")
    short = db.fetchone()[0]
    
    db.execute("SELECT MAX(contest_id) FROM problems")
    max_contest = db.fetchone()[0] or 0
    
    conn.close()
    return total, short, max_contest

def fetch_new_problems():
    """Fetch new problems from Codeforces API"""
    print("1. Fetching new problems from Codeforces API...")
    
    total, short, max_contest = get_current_status()
    print(f"   Current: {total:,} problems, {short} short, highest contest: {max_contest}")
    
    conn = sqlite3.connect('codeforces.db')
    db = conn.cursor()
    
    # Fetch from API
    url = "https://codeforces.com/api/problemset.problems"
    response = requests.get(url)
    data = response.json()
    
    problems = data['result']['problems']
    problemStatistics = data['result']['problemStatistics']
    
    print(f"   API has {len(problems)} total problems")
    
    # Create stats map
    stats_map = {}
    for stat in problemStatistics:
        if 'contestId' in stat and 'index' in stat:
            key = str(stat['contestId']) + stat['index']
            stats_map[key] = stat.get('solvedCount', 0)
    
    # Insert/update problems
    new_count = 0
    updated_count = 0
    
    for problem in problems:
        if 'contestId' not in problem:
            continue
        
        problem_id = str(problem['contestId']) + problem['index']
        rating = problem.get('rating', None)
        solved_by = stats_map.get(problem_id, 0)
        
        # Check if exists
        db.execute("SELECT problem_id, solved_by FROM problems WHERE problem_id = ?", (problem_id,))
        existing = db.fetchone()
        
        if not existing:
            # New problem
            new_count += 1
            db.execute(
                "INSERT INTO problems (problem_id, contest_id, contest_index, problem_name, problem_type, problem_url, difficulty_rating, solved_by) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (problem_id, 
                 int(problem['contestId']), 
                 problem['index'], 
                 problem['name'],
                 problem.get('type', 'PROGRAMMING'),
                 f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}",
                 rating,
                 solved_by))
        else:
            # Update solved count if changed
            if existing[1] != solved_by:
                db.execute("UPDATE problems SET solved_by = ? WHERE problem_id = ?", (solved_by, problem_id))
                updated_count += 1
        
        # Add tags for new problems
        if not existing and 'tags' in problem:
            for tag in problem['tags']:
                db.execute("INSERT OR IGNORE INTO tags (tag_key) VALUES (?)", (tag,))
                
                db.execute("SELECT tag_id FROM tags WHERE tag_key = ?", (tag,))
                tag_row = db.fetchone()
                if tag_row:
                    db.execute("INSERT OR IGNORE INTO problems_tags (problem_id, tag_id) VALUES (?,?)", 
                             (problem_id, tag_row[0]))
    
    conn.commit()
    conn.close()
    
    print(f"   Added {new_count} new problems, updated {updated_count} existing")
    return new_count

def scrape_missing_statements():
    """Scrape statement lengths for problems that don't have them"""
    print("2. Scraping missing problem statement lengths...")
    
    conn = sqlite3.connect('codeforces.db')
    db = conn.cursor()
    
    # Get problems without statement lengths
    db.execute("""
        SELECT problem_id, problem_url FROM problems 
        WHERE problem_statement_length IS NULL 
        AND difficulty_rating IS NOT NULL
        AND contest_id NOT IN (1505, 1331, 1145, 952, 784, 656, 409, 290, 171)
        ORDER BY contest_id DESC
    """)
    
    problems = db.fetchall()
    total = len(problems)
    
    if total == 0:
        print("   All problems already have statement lengths!")
        conn.close()
        return 0
    
    print(f"   Need to scrape {total} problems...")
    
    scraped = 0
    short_found = 0
    
    for i, (problem_id, problem_url) in enumerate(problems):
        try:
            req = Request(problem_url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            html_code = pq(webpage)
            
            statement = html_code.find('.problem-statement').remove('.header').remove('.input-specification').remove(
                '.output-specification').remove('.sample-tests').html()
            
            if statement is not None:
                length = len(statement)
                db.execute("UPDATE problems SET problem_statement_length = ? WHERE problem_id = ?", 
                          (length, problem_id))
                conn.commit()
                scraped += 1
                
                if length <= 1000:
                    short_found += 1
                    if short_found % 10 == 0:
                        print(f"   Found {short_found} short problems so far...")
        
        except Exception as e:
            pass  # Continue on errors
        
        # Progress every 100
        if (i + 1) % 100 == 0:
            progress = (i + 1) / total * 100
            print(f"   Progress: {i+1}/{total} ({progress:.1f}%) - {short_found} short found")
        
        time.sleep(0.5)  # Be nice to servers
    
    conn.close()
    print(f"   Scraped {scraped} problems, found {short_found} new short problems")
    return short_found

def generate_readme():
    """Generate complete README with all short problems"""
    print("3. Generating updated README...")
    
    conn = sqlite3.connect('codeforces.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    
    # Generate problem tables
    f = open('problem_table.txt', 'w', encoding='utf-8')
    problem_stats_f = open('problem_stats_table.txt', 'w', encoding='utf-8')
    stats = {}
    
    april_fool_contests = [1505, 1331, 1145, 952, 784, 656, 409, 290, 171]
    april_fool_str = ','.join(map(str, april_fool_contests))
    
    for x in range(800, 4000, 100):
        db.execute(f"""SELECT problem_id, problem_name, problem_url, problem_statement_length, 
                   difficulty_rating, solved_by FROM problems 
                   WHERE difficulty_rating = {x}
                   AND problem_statement_length <= 1000 
                   AND problem_statement_length IS NOT NULL
                   AND contest_id not in ({april_fool_str})
                   ORDER BY problem_id""")
        problems = db.fetchall()
        
        if len(problems) >= 1:
            f.write("<details open>\n"
                    "  <summary><span id=" + str(x) + ">Rating " + str(x) + "</span></summary>\n\n"
                    )
            f.write("|# | ID | Problem  | Rating |\n"
                    "|--- | ---| ----- | ---------- |\n")
            index = 1
            for row in problems:
                try:
                    f.write(
                        "|" + str(index) + "|" + row['problem_id'] + "|<a href=\"" + row['problem_url'] + "\" target=\"_blank\">" + row['problem_name'] + "</a>|"
                        + str(row['difficulty_rating']) + "|\n")
                except Exception as e:
                    continue
                index = index + 1
            f.write("</details>")
            f.write("\n\n")
            stats[str(x)] = str(index - 1)
    
    # Generate stats table
    if stats:
        problem_stats_f.write("| Skill Level | Problems |\n"
                              "|:---:|:---:|\n")
        
        skill_levels = [
            ("Newbie", ["800", "900", "1000", "1100"]),
            ("Pupil", ["1200", "1300"]),
            ("Specialist", ["1400", "1500"]),
            ("Expert", ["1600", "1700", "1800"]),
            ("Candidate Master", ["1900", "2000"]),
            ("Master", ["2100", "2200"]),
            ("International Master", ["2300"]),
            ("Grandmaster", ["2400", "2500"]),
            ("International GM", ["2600", "2700", "2800", "2900"]),
            ("Legendary GM", ["3000", "3100", "3200", "3300", "3400", "3500"])
        ]
        
        for title, ratings in skill_levels:
            links = []
            for rating in ratings:
                if rating in stats:
                    links.append(f"[{rating}](#{rating}) ({stats[rating]})")
            if links:
                problem_stats_f.write(f"| {title} | {' • '.join(links)} |\n")
    
    f.close()
    problem_stats_f.close()
    
    # Update README
    total_count = sum(int(v) for v in stats.values())
    today = datetime.now().strftime('%Y-%m-%d')
    
    with open('problem_stats_table.txt', 'r', encoding='utf-8') as f:
        stats_content = f.read().strip()
    
    with open('problem_table.txt', 'r', encoding='utf-8') as f:
        problem_content = f.read().strip()
    
    header = f"""# Short Codeforces Problems

**{total_count}+ problems with statements under 1000 characters**

*Updated: {today}*

## Why?

Long problem statements are annoying. Sometimes you spend more time reading than solving. This list has only problems with short, clear descriptions so you can:

- Practice more problems in the same time
- Focus on the actual algorithm, not parsing text
- Build confidence without getting lost in paragraphs
- Great for beginners who find long problems overwhelming

## Problem Lists

"""
    
    readme_content = header + stats_content + "\n\n## Annual Update\n\nTo get new problems:\n```bash\npython annual_update.py\n```\n\nSetup:\n1. Get API keys from [Codeforces API Settings](https://codeforces.com/settings/api)\n2. Create `creds/credentials_local.py` with your keys\n3. Run the script\n\nWhat's included:\n- SQLite database with all problem data\n- Incremental updates (only processes new problems)\n- Your API keys stay private\n\n" + problem_content
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    conn.close()
    
    print(f"   Generated README with {total_count} short problems")
    return total_count

def main():
    print("=== ANNUAL CODEFORCES SHORT PROBLEMS UPDATE ===")
    print(f"Start time: {datetime.now()}")
    
    # Step 1: Fetch new problems
    new_problems = fetch_new_problems()
    
    # Step 2: Scrape missing statements
    new_short = scrape_missing_statements()
    
    # Step 3: Generate README
    total_short = generate_readme()
    
    # Final stats
    conn = sqlite3.connect('codeforces.db')
    db = conn.cursor()
    db.execute("SELECT MAX(contest_id) FROM problems")
    max_contest = db.fetchone()[0]
    conn.close()
    
    print(f"\n=== UPDATE COMPLETE ===")
    print(f"New problems added: {new_problems}")
    print(f"New short problems found: {new_short}")
    print(f"Total short problems: {total_short}")
    print(f"Up to contest: {max_contest}")
    print(f"End time: {datetime.now()}")
    
    # Clean up temp files
    import os
    for temp_file in ['problem_table.txt', 'problem_stats_table.txt']:
        try:
            os.remove(temp_file)
        except:
            pass

if __name__ == "__main__":
    main()