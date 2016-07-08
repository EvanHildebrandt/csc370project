CREATE TABLE Accounts
(
    id int AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE,
    password CHAR(128) NOT NULL,
    salt CHAR(128) NOT NULL,
    rep int
);

CREATE TABLE Subsaiddits
(
    id int AUTO_INCREMENT PRIMARY KEY,
    subsaiddit_title VARCHAR(255) NOT NULL UNIQUE,
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
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by int REFERENCES Accounts(id) ON DELETE SET NULL,
    subsaiddit INT REFERENCES Subsaiddits(id) ON DELETE SET NULL
);

CREATE TABLE Votes
(
    up_down BOOLEAN NOT NULL DEFAULT 1,
    account_id int REFERENCES Accounts(id) ON DELETE SET NULL,
    post_id int REFERENCES Posts(id),
    comment_id int REFERENCES Comments(id),
    UNIQUE KEY vote (account_id, post_id, comment_id)
);

CREATE TABLE Comments
(
    id int AUTO_INCREMENT PRIMARY KEY,
    text_content TEXT NOT NULL,
    created TIMESTAMP NOT NULL,
    post int NOT NULL,
    FOREIGN KEY (post) REFERENCES Posts(id) ON DELETE CASCADE,
    reply_to int REFERENCES Comments(id),
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
    subsaiddit_id int REFERENCES Subsaiddits(id) ON DELETE CASCADE
);
