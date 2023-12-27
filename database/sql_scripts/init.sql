CREATE TABLE Huby (
    AdresMAC varchar(255) NOT NULL,
    AdresIP varchar(255) NOT NULL,
    LoginH varchar(255) NOT NULL,
    Nazwa varchar(255) NOT NULL,
    Rzedy int,
    Kolumny int,
    PRIMARY KEY(AdresMAC)
);

CREATE TABLE Uzytkownicy (
    Email varchar(255) NOT NULL,
    Username varchar(255) NOT NULL,
    Haslo varchar(255) NOT NULL,
    PRIMARY KEY(Email)
);

CREATE TABLE Przydzielenia (
    Email varchar(255) NOT NULL,
    AdresMAC varchar(255) NOT NULL,
    PRIMARY KEY(Email, AdresMAC),
    FOREIGN KEY(Email) REFERENCES Uzytkownicy(Email),
    FOREIGN KEY(AdresMAC) REFERENCES Huby(AdresMAC)
);

CREATE TABLE Kasetony (
    IdK int NOT NULL,
    Rzad int NOT NULL,
    Kolumna int NOT NULL,
    CzyWlaczony bit NOT NULL,
    Jasnosc int NOT NULL,
    KolorR float NOT NULL,
    KolorG float NOT NULL,
    KolorB float NOT NULL,
    AdresMAC varchar(255) NOT NULL,
    PRIMARY KEY(IdK, AdresMAC),
    FOREIGN KEY(AdresMAC) REFERENCES Huby(AdresMAC)
);

CREATE TABLE Grupy (
    IdGr int NOT NULL,
    NazwaGr varchar(255) NOT NULL,
    PRIMARY KEY(IdGr)
);

CREATE TABLE Przypisania (
    IdGr int NOT NULL,
    IdK int NOT NULL,
    PRIMARY KEY(IdGr, IdK),
    FOREIGN KEY(IdGr) REFERENCES Grupy(IdGr),
    FOREIGN KEY(IdK) REFERENCES Kasetony(IdK)
);
