CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS PictureTags CASCADE;
DROP TABLE IF EXISTS Album CASCADE;
DROP TABLE IF EXISTS AlbumTags CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;

CREATE TABLE Users (
    user_id int4 AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    user_password varchar(255),
    first_name varchar(255),
    last_name varchar(255),
    DOB DATE
    gender varchar(255)
    hometown varchar(255)
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Friends (
    pair_id int4 AUTO_INCREMENT,
    user_id 
    friend_id
    user_id1 int4
    user_id2 int4 
    PRIMARY KEY (user_id1, user_id2),
    FOREIGN KEY (user_id1) REFERENCES Users(user_id),
    FOREIGN KEY (user_id2) REFERENCES Users(user_id)
);

CREATE TABLE Pictures
(
  picture_id int4 AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);
INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');

CREATE TABLE PictureTags
(
  picture_id,
  tag_description VARCHAR(255),
  FOREIGN KEY picture_id REFERENCES Pictures(picture_id)
);

CREATE TABLE Album
(
  album_id int4 AUTO_INCREMENT,
  album_name VARCHAR(255),
  user_id VARCHAR(255),
  create_date VARCHAR(255),
  CONSTRAINT album_pk PRIMARY KEY (album_id) 
);

CREATE TABLE AlbumTags(
  album_id,
  tag_description VARCHAR(255),
  FOREIGN KEY album_id REFERENCES Album(album_id)
);

CREATE TABLE Comments(
  comment_id,
  comment_description VARCHAR(255),
  comment_timestamp TIME,
  user_id VARCHAR(255),
  CONSTRAINT comment_pk PRIMARY KEY (comment_id)
);