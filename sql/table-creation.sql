CREATE TABLE Posts
(
    id int AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    text_content TEXT,
    url VARCHAR(511),
    published TIMESTAMP NOT NULL,
    last_modified TIMESTAMP,
    author_id int REFERENCES Accounts(id) NOT NULL,
    subsaiddit_title VARCHAR(255) REFERENCES Subsaiddits(title) NOT NULL
);

CREATE TABLE Votes
(
    up_down BOOLEAN NOT NULL,
    account_id REFERENCES Accounts(id) NOT NULL,
    post_id REFERENCES Posts(id),
    comment_id REFERENCES Comments(id)
);

CREATE TABLE Comments
(
    id int AUTO_INCREMENT PRIMARY KEY,
    text_content TEXT NOT NULL,
    published TIMESTAMP NOT NULL
);
