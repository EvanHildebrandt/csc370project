SELECT title FROM Posts
    JOIN Votes on Votes.post_id = Posts.id
    JOIN Accounts on Posts.created_by = Accounts.id
    WHERE Posts.created_by="1"
    ORDER BY up_down DESC;
