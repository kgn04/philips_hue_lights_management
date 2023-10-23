CREATE TABLE Huby (
    AdresMAC varchar(255) NOT NULL,
    AdresIP varchar(255) NOT NULL,
    LoginH varchar(255) NOT NULL,
    PRIMARY KEY(AdresMAC)
);

CREATE TABLE Uzytkownicy (
    Email varchar(255) NOT NULL,
    LoginU varchar(255) NOT NULL,
    Haslo varchar(255) NOT NULL,
    AdresMAC varchar(255),
    PRIMARY KEY(Email),
    FOREIGN KEY(AdresMAC) REFERENCES Huby(AdresMAC)
    --ON DELETE SET NULL
);

CREATE TABLE Kasetony (
    IdK int NOT NULL,
    Rzad varchar(255) NOT NULL,
    Kolumna varchar(255) NOT NULL,
    Jasnosc varchar(255) NOT NULL,
    Czerwony int NOT NULL,
    Zielony int NOT NULL,
    Niebieski int NOT NULL,
    AdresMAC varchar(255) NOT NULL,
    PRIMARY KEY(IdK),
    FOREIGN KEY(AdresMAC) REFERENCES Huby(AdresMAC)
    --ON DELETE CASCADE
);

CREATE TABLE Grupy (
    IdGr int NOT NULL,
    NazwaGr varchar(255) NOT NULL,
    PRIMARY KEY(IdGr)
);

CREATE TABLE Przypisania (
    IdGr int NOT NULL,
    IdK int NOT NULL,
    PRIMARY KEY(IdGr, IdK)
    --ON DELETE CASCADE
);
