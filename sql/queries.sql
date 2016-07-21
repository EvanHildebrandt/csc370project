-- 8a
-- All posts created by account 1, sorted by highest rating
SELECT Posts.*, diff FROM Posts
    LEFT OUTER JOIN
        (SELECT post_id, CAST(SUM(votes.up_down) as SIGNED) as diff FROM votes WHERE votes.comment_id = 0 GROUP BY votes.post_id) V ON V.post_id = posts.id
    WHERE Posts.created_by=1
    ORDER BY diff DESC;



-- 8b
-- All posts from account 1's Friends, sorted by highest rating
SELECT Posts.*, diff FROM Posts
    LEFT OUTER JOIN
        (SELECT post_id, CAST(SUM(votes.up_down) as SIGNED) as diff FROM votes WHERE votes.comment_id = 0 GROUP BY votes.post_id) V ON V.post_id = posts.id
    JOIN Friends ON 1 = Friends.account_1_id OR 1 = Friends.account_2_id
    WHERE (Posts.created_by = Friends.account_1_id OR Posts.created_by = Friends.account_2_id) AND Posts.created_by <> 1
    ORDER BY diff DESC;



-- 8c
-- Account "A"'s subscribed subsaiddits and default ones
SELECT DISTINCT Subsaiddits.* FROM Accounts
    JOIN Subscribes on Accounts.id = Subscribes.account_id
    JOIN Subsaiddits on Subscribes.subsaiddit_id = Subsaiddits.id OR Subsaiddits.is_default = 1
    Where Accounts.username = "Evan";



-- 8d
-- Account "A"'s favorite posts
SELECT Posts.* FROM Posts
    JOIN Favourites on Favourites.post_id = Posts.id
    JOIN Accounts on Accounts.id = Favourites.account_id
    Where Accounts.username = "Evan";




-- 8e
-- Account "A"'s friend's favorite posts
SELECT Posts.* FROM Accounts A1
    JOIN Friends ON A1.id = Friends.account_1_id OR A1.id = Friends.account_2_id
    JOIN Accounts A2 ON (Friends.account_1_id = A2.id OR Friends.account_2_id = A2.id) AND A2.username <> "Evan"
    JOIN Posts ON A2.id = Posts.created_by
    Where A1.username = "Evan";



-- 8f
-- Account "A"'s friend's subscribed subsaiddits
SELECT DISTINCT Subsaiddits.* FROM Accounts A1
    JOIN Friends ON A1.id = Friends.account_1_id OR A1.id = Friends.account_2_id
    JOIN Accounts A2 ON (Friends.account_1_id = A2.id OR Friends.account_2_id = A2.id) AND A2.username <> "Evan"
    JOIN Subscribes on A2.id = Subscribes.account_id
    JOIN Subsaiddits on Subsaiddits.id = Subscribes.subsaiddit_id
    Where A1.username = "Evan";



-- 8g
-- Subsaiddit "S"'s creator's posts
SELECT Posts.* FROM Posts
    JOIN Subsaiddits on Posts.created_by = Subsaiddits.created_by
    WHERE Subsaiddits.subsaiddit_title = "Jokes";



-- 8h
-- Subsaiddit "S"'s posts that contain 'anyone'
SELECT Posts.* FROM Posts
    JOIN Subsaiddits on Subsaiddits.id = Posts.subsaiddit
    WHERE Subsaiddits.subsaiddit_title = "Jokes"
    AND (Posts.title LIKE '%type%'
    OR Posts.text_content LIKE '%type%');
