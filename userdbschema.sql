DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS CookieStore;

CREATE TABLE IF NOT EXISTS Users(
    userId BIGINT PRIMARY KEY,
    userName TEXT UNIQUE NOT NULL,
    userPass TEXT NOT NULL CHECK (LENGTH(userPass) >= 4),
    userAvatar BLOB DEFAULT NULL,
    loginUser INTEGER NOT NULL CHECK (loginUser in (0,1)) DEFAULT 0

);

CREATE TABLE CookieStore(
    cookieId BIGINT PRIMARY KEY,
    cookieName TEXT NOT NULL,
    cookieValue TEXT NOT NULL,
    cookieCreate TIMESTAMP NOT NULL,
    cookieExpire TIMESTAMP NOT NULL,
    userId BIGINT NOT NULL UNIQUE,
    FOREIGN KEY (userId) REFERENCES Users(userId)
);

