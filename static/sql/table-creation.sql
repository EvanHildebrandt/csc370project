CREATE TABLE Posts
(
    id int AUTO_INCREMENT,
    subsaiddit_title VARCHAR(255) NOT NULL,
    post_title VARCHAR(255) NOT NULL,
    post_text TEXT,
    post_url VARCHAR(511),
    post_last_modified TIMESTAMP NOT NULL,
    FOREIGN KEY subsaiddit_title
        REFERENCES Subsaiddits(title),
    PRIMARY KEY (id)
)

CREATE TABLE Favorite
(
    FOREIGN KEY account_id
        REFERENCES Accounts(id),
    FOREIGN KEY post_id
        REFERENCES Posts(id)
)

CREATE TABLE Downvote
(
    FOREIGN KEY account_id
        REFERENCES Accounts(id),
    FOREIGN KEY post_id
        REFERENCES Posts(id)
)

CREATE TABLE Upvote
(
    FOREIGN KEY account_id
        REFERENCES Accounts(id),
    FOREIGN KEY post_id
        REFERENCES Posts(id)
)
