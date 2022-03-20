
CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS Tag CASCADE;
DROP TABLE IF EXISTS CreatePictureTag CASCADE;
DROP TABLE IF EXISTS Album CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Likes CASCADE; 

CREATE TABLE Users (
    user_id int4 AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    user_password varchar(255),
    first_name varchar(255),
    last_name varchar(255),
    DOB DATE,
    gender varchar(255),
    hometown varchar(255),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Friends (
    user_id1 int4,
    user_id2 int4,
    FOREIGN KEY (user_id1) REFERENCES Users(user_id),
    FOREIGN KEY (user_id2) REFERENCES Users(user_id),
    PRIMARY KEY (user_id1, user_id2)
);

CREATE TABLE Pictures
(
  picture_id int4 AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  album_id int4 ON DELETE CASCADE
  INDEX upid_idx (user_id),
  FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE,
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Tag
(
  tag_description VARCHAR(255),
  tag_counter int4, 
  CONSTRAINT tag_descPK PRIMARY KEY (tag_description)
);

CREATE TABLE CreatePictureTag 
(
  tag_description VARCHAR(255),
  picture_id int4,
  PRIMARY KEY (tag_description, picture_id),
  FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
  FOREIGN KEY (tag_description) REFERENCES Tag(tag_description) 
);

CREATE TABLE Album
(
  album_id int4 AUTO_INCREMENT,
  album_name VARCHAR(255),
  user_id VARCHAR(255),
  create_date VARCHAR(255),
  CONSTRAINT album_pk PRIMARY KEY (album_id) 
);

CREATE TABLE Comments(
  comment_id int4 AUTO_INCREMENT,
  comment_description VARCHAR(255),
  comment_timestamp TIME,
  user_id VARCHAR(255),
  picture_id int4,
  CONSTRAINT comment_pk PRIMARY KEY (comment_id),
  FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id) 
);

CREATE TABLE Likes(
  like_counter int4,
  picture_id int4,
  user_id int4,
  FOREIGN KEY (picture_id) REFERENCES Pictures(picture_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id)
) 