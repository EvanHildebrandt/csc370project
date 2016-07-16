-- 8a (I didn't sum the votes of the same posts)
SELECT Posts.*, COUNT(UpVotes.account_id) - COUNT(DownVotes.account_id) AS DIFF FROM Posts
     JOIN Votes AS UpVotes on UpVotes.post_id = Posts.id
     JOIN Votes AS DownVotes on DownVotes.post_id = Posts.id
     WHERE Posts.created_by="1"
     AND UpVotes.comment_id = 0
     AND UpVotes.up_down = 1
     AND DownVotes.up_down = 0
     AND DownVotes.comment_id = 0
	ORDER BY DIFF DESC

-- 8b
SELECT Posts.*, COUNT(UpVotes.account_id) - COUNT(DownVotes.account_id) AS DIFF FROM Posts
     JOIN Votes AS UpVotes on UpVotes.post_id = Posts.id
     JOIN Votes AS DownVotes on DownVotes.post_id = Posts.id
     JOIN Friends ON 1 = Friends.account_1_id OR 1 = Friends.account_2_id
     WHERE Posts.created_by = Friends.account_1_id OR Posts.created_by = Friends.account_2_id
     AND UpVotes.comment_id = 0
     AND UpVotes.up_down = 1
     AND DownVotes.up_down = 0
     AND DownVotes.comment_id = 0
     ORDER BY DIFF DESC

-- 8c
SELECT Subsaiddits.* FROM Accounts
    JOIN Subscribes on Accounts.id = Subscribes.account_id
    JOIN Subsaiddits on Subscribes.subsaiddit_id = Subsaiddits.id
    Where Accounts.username = "A";

-- 8d
SELECT Posts.* FROM Posts
    JOIN Favourites on Favourites.post_id = Posts.id
    JOIN Accounts on Accounts.id = Favourites.account_id
    Where Accounts.username = "A";

-- 8e
SELECT Posts.* FROM Accounts A1
    JOIN Friends ON A1.id = Friends.account_1_id OR A1.id = Friends.account_2_id
    JOIN Accounts A2 ON (Friends.account_1_id = A2.id OR Friends.account_2_id = A2.id) AND A2.username <> "bob"
    JOIN Posts ON A2.id = Posts.created_by
    Where A1.username = "bob";

-- 8f
SELECT DISTINCT Subsaiddits.* FROM Accounts A1
    JOIN Friends ON A1.id = Friends.account_1_id OR A1.id = Friends.account_2_id
    JOIN Accounts A2 ON (Friends.account_1_id = A2.id OR Friends.account_2_id = A2.id) AND A2.username <> "bob"
    JOIN Subscribes on A2.id = Subscribes.account_id
    JOIN Subsaiddits on Subsaiddits.id = Subscribes.subsaiddit_id
    Where A1.username = "bob";

-- 8g
SELECT Posts.* FROM Posts
    JOIN Subsaiddits on Posts.created_by = Subsaiddits.created_by
    WHERE Subsaiddits.subsaiddit_title = "hello";

-- 8h
SELECT Posts.* FROM Posts
    JOIN Subsaiddits on Subsaiddits.id = Posts.subsaiddit
    WHERE Subsaiddits.subsaiddit_title = "hello"
    AND (Subsaiddits.text_content LIKE '%anyone%'
    OR Posts.text_content LIKE '%anyone%');
