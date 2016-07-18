-- 8a 
-- All posts created by account 1, sorted by highest rating
SELECT id, title, text_content, url, created, last_modified, created_by, subsaiddit, SUM(VOTES) AS RATING FROM
    (SELECT *, COUNT(UpVotes.account_id) AS VOTES FROM Posts
         LEFT JOIN Votes AS UpVotes on UpVotes.post_id = Posts.id
         WHERE Posts.created_by = 1
         AND (UpVotes.comment_id = -1 OR UpVotes.up_down IS NULL)
         AND (UpVotes.up_down = 1 OR UpVotes.up_down IS NULL)
         GROUP BY id
    UNION
    SELECT *, -COUNT(DownVotes.account_id) AS VOTES FROM Posts
         LEFT JOIN Votes AS DownVotes on DownVotes.post_id = Posts.id
         WHERE Posts.created_by=1
         AND (DownVotes.comment_id = -1 OR DownVotes.up_down IS NULL)
         AND (DownVotes.up_down = 0 OR DownVotes.up_down IS NULL)
         GROUP BY id) A
GROUP BY id
ORDER BY RATING DESC;



-- 8b
-- All posts from account 1's Friends, sorted by highest rating
SELECT id, title, text_content, url, created, last_modified, created_by, subsaiddit, SUM(VOTES) AS RATING FROM
    (SELECT *, COUNT(UpVotes.account_id) AS VOTES FROM Posts
         LEFT JOIN Votes AS UpVotes on UpVotes.post_id = Posts.id
         JOIN Friends ON 1 = Friends.account_1_id OR 1 = Friends.account_2_id
         WHERE (Posts.created_by = Friends.account_1_id OR Posts.created_by = Friends.account_2_id) AND Posts.created_by <> 1
         AND (UpVotes.comment_id = -1 OR UpVotes.up_down IS NULL)
         AND (UpVotes.up_down = 1 OR UpVotes.up_down IS NULL)
         GROUP BY id
    UNION
    SELECT *, -COUNT(DownVotes.account_id) AS VOTES FROM Posts
         LEFT JOIN Votes AS DownVotes on DownVotes.post_id = Posts.id
         JOIN Friends ON 1 = Friends.account_1_id OR 1 = Friends.account_2_id
         WHERE (Posts.created_by = Friends.account_1_id OR Posts.created_by = Friends.account_2_id) AND Posts.created_by <> 1
         AND (DownVotes.comment_id = -1 OR DownVotes.up_down IS NULL)
         AND (DownVotes.up_down = 0 OR DownVotes.up_down IS NULL)
         GROUP BY id) A
GROUP BY id
ORDER BY RATING DESC;



-- 8c
-- Account "A"'s subscribed subsaiddits and default ones
SELECT Subsaiddits.* FROM Accounts
    JOIN Subscribes on Accounts.id = Subscribes.account_id
    JOIN Subsaiddits on Subscribes.subsaiddit_id = Subsaiddits.id
    Where Accounts.username = "A";



-- 8d
-- Account "A"'s favorite posts
SELECT Posts.* FROM Posts
    JOIN Favourites on Favourites.post_id = Posts.id
    JOIN Accounts on Accounts.id = Favourites.account_id
    Where Accounts.username = "A";




-- 8e
-- Account "A"'s friend's favorite posts
SELECT Posts.* FROM Accounts A1
    JOIN Friends ON A1.id = Friends.account_1_id OR A1.id = Friends.account_2_id
    JOIN Accounts A2 ON (Friends.account_1_id = A2.id OR Friends.account_2_id = A2.id) AND A2.username <> "A"
    JOIN Posts ON A2.id = Posts.created_by
    Where A1.username = "A";



-- 8f
-- Account "A"'s friend's subscribed subsaiddits
SELECT DISTINCT Subsaiddits.* FROM Accounts A1
    JOIN Friends ON A1.id = Friends.account_1_id OR A1.id = Friends.account_2_id
    JOIN Accounts A2 ON (Friends.account_1_id = A2.id OR Friends.account_2_id = A2.id) AND A2.username <> "A"
    JOIN Subscribes on A2.id = Subscribes.account_id
    JOIN Subsaiddits on Subsaiddits.id = Subscribes.subsaiddit_id
    Where A1.username = "A";



-- 8g
-- Subsaiddit "S"'s creator's posts
SELECT Posts.* FROM Posts
    JOIN Subsaiddits on Posts.created_by = Subsaiddits.created_by
    WHERE Subsaiddits.subsaiddit_title = "S";



-- 8h
-- Subsaiddit "S"'s posts that contain 'anyone'
SELECT Posts.* FROM Posts
    JOIN Subsaiddits on Subsaiddits.id = Posts.subsaiddit
    WHERE Subsaiddits.subsaiddit_title = "S"
    AND (Subsaiddits.text_content LIKE '%anyone%'
    OR Posts.text_content LIKE '%anyone%');
