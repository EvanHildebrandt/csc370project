-- 8a (I didn't sum the votes of the same posts)
SELECT title FROM Posts
    JOIN Votes on Votes.post_id = Posts.id
    JOIN Accounts on Posts.created_by = Accounts.id
    WHERE Posts.created_by="1"
    ORDER BY up_down DESC;

-- 8d
SELECT title FROM Posts
    JOIN Favourites on Favourites.account_id = Posts.id
    JOIN Accounts on Accounts.id = Favourites.account_id
    Where Accounts.username = "A";

-- 8h
SELECT title FROM Posts
    JOIN Subsaiddits on Subsaiddits.id = Posts.subsaiddit
    WHERE Subsaiddits.subsaiddit_title = "hello"
    AND Posts.text_content LIKE '%anyone%';
