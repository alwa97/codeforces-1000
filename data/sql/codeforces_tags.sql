create table tags
(
    tag_id   int         not null
        primary key,
    tag_name varchar(50) not null,
    constraint `UNIQUE`
        unique (tag_name)
);

INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (37, '*special problem');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (1, '2-sat');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (2, 'binary search');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (3, 'bitmasks');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (4, 'brute force');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (5, 'chinese remainder theorem');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (6, 'combinatorics');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (7, 'constructive algorithms');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (8, 'data structures');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (9, 'dfs and similar');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (10, 'divide and conquer');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (11, 'dp');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (12, 'dsu');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (13, 'expression parsing');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (14, 'fft');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (15, 'flows');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (16, 'games');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (17, 'geometry');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (18, 'graph matchings');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (19, 'graphs');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (20, 'greedy');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (21, 'hashing');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (22, 'implementation');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (23, 'interactive');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (24, 'math');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (25, 'matrices');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (26, 'meet-in-the-middle');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (27, 'number theory');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (28, 'probabilities');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (29, 'schedules');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (30, 'shortest paths');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (31, 'sortings');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (32, 'string suffix structures');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (33, 'strings');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (34, 'ternary search');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (35, 'trees');
INSERT INTO codeforces.tags (tag_id, tag_name) VALUES (36, 'two pointers');