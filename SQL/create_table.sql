CREATE TABLE SANATCI (
  	sanatci_id		char(20)		NOT NULL,
  	sanatci_ismi  	varchar(30)		NOT NULL,
	PRIMARY KEY (sanatci_id)
);

CREATE TABLE SOLO (
	sanatci_id		char(20)		NOT NULL,
	solo_id			varchar(30) 	NOT NULL,
  	yas				int,
  	dogum_yili		varchar(4), 
  	cinsiyet 		char,
	PRIMARY KEY (solo_id),
	FOREIGN KEY (sanatci_id) REFERENCES SANATCI(sanatci_id)
);

CREATE TABLE GRUP (
	sanatci_id		char(20)		NOT NULL,
	grup_id			varchar(30)		NOT NULL,
	kurulus_yili	varchar(4), 
	PRIMARY KEY (grup_id),
	FOREIGN KEY (sanatci_id) REFERENCES SANATCI(sanatci_id)
);

CREATE TABLE ALBUM (
	album_id		varchar(30)		NOT NULL,
	album_ismi    	varchar(30)		NOT NULL,
	yili			varchar(4),
	odul  			varchar(30),
	PRIMARY KEY (album_id),
	UNIQUE (album_ismi)
);

CREATE TABLE SARKI (
	sarki_id        varchar(30)		NOT NULL,
	album_id    	varchar(30)		NOT NULL,
	sanatci_id  	varchar(30)		NOT NULL,
	sure			decimal(4,0),
	sarki_ismi      varchar(30)		NOT NULL,
	tur  			varchar(30),
	PRIMARY KEY (sarki_id),
	UNIQUE (sarki_ismi),
	FOREIGN KEY (album_id) REFERENCES ALBUM(album_id),
	FOREIGN KEY (sanatci_id) REFERENCES SANATCI(sanatci_id)
);

CREATE TABLE UYE (
  	solo_id      	varchar(30)		NOT NULL,
  	grup_id      	varchar(30)		NOT NULL,
  	rol 		  	varchar(30),
	FOREIGN KEY (grup_id) REFERENCES GRUP(grup_id),
	FOREIGN KEY (solo_id) REFERENCES SOLO(solo_id)
);

CREATE TABLE KULLANICI (
  	nickname      			varchar(30),
  	kullanici_ismi   		varchar(30),
  	kullanici_soyismi  		varchar(30),
  	mail_adresi				varchar(30),
  	sifre    				varchar(15),
	PRIMARY KEY (nickname),
	UNIQUE (mail_adresi)
);

CREATE TABLE DEGERLENDIRME (
  	degerlendirme_id     	varchar(30)		NOT NULL,
	yorum					varchar(30),
  	puan					int,
  	sarki_id      			varchar(30)		NOT NULL,
  	album_id    			varchar(30)		NOT NULL,
  	nickname 				varchar(30)		NOT NULL,
	PRIMARY KEY (degerlendirme_id),
	FOREIGN KEY (album_id) REFERENCES ALBUM(album_id),
	FOREIGN KEY (sarki_id) REFERENCES SARKI(sarki_id),
	FOREIGN KEY (nickname) REFERENCES KULLANICI(nickname)
);