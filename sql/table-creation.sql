CREATE TABLE Accounts
(
    id int AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE,
    password CHAR(128) NOT NULL,
    rep int
);

CREATE TABLE Subsaiddits
(
    subsaiddit_title VARCHAR(255) PRIMARY KEY,
    is_default BOOLEAN NOT NULL
        DEFAULT 0,
    description text,
    created TIMESTAMP NOT NULL,
    created_by int REFERENCES Accounts(id) ON DELETE SET NULL
);

CREATE TABLE Posts
(
    id int AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    text_content TEXT,
    url VARCHAR(511),
    created TIMESTAMP NOT NULL,
    last_modified TIMESTAMP,
    created_by int REFERENCES Accounts(id) ON SET NULL,
    subsaiddit_title VARCHAR(255) REFERENCES Subsaiddits(title) ON DELETE SET NULL
);

CREATE TABLE Votes
(
    up_down BOOLEAN NOT NULL DEFAULT 1,
    account_id int REFERENCES Accounts(id) ON DELETE SET NULL,
    post_id int REFERENCES Posts(id),
    comment_id int REFERENCES Comments(id)
);

CREATE TABLE Comments
(
    id int AUTO_INCREMENT PRIMARY KEY,
    text_content TEXT NOT NULL,
    created TIMESTAMP NOT NULL,
    reply_to int REFERENCES Accounts(id)
        ON DELETE SET NULL,
    created_by int REFERENCES Accounts(id) ON DELETE SET NULL
);

CREATE TABLE Friends
(
    account_1_id int REFERENCES Accounts(id) ON DELETE CASCADE,
    account_2_id int REFERENCES Accounts(id) ON DELETE CASCADE
);

CREATE TABLE Subscribes
(
    account_id int REFERENCES Accounts(id) ON DELETE CASCADE,
    subsaiddit_title VARCHAR(255) REFERENCES Subsaiddits(title) ON DELETE CASCADE
);
