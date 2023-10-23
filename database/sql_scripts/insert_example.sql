INSERT INTO Huby (AdresMAC, AdresIP, LoginH) VALUES
    ('00:11:22:33:44:55', '192.168.1.1', 'HubyUser1'),
    ('AA:BB:CC:DD:EE:FF', '192.168.1.2', 'HubyUser2'),
    ('12:34:56:78:90:AB', '192.168.1.3', 'HubyUser3');

INSERT INTO Uzytkownicy (Email, LoginU, Haslo, AdresMAC) VALUES
    ('user1@example.com', 'User1', 'password1', '00:11:22:33:44:55'),
    ('user2@example.com', 'User2', 'password2', 'AA:BB:CC:DD:EE:FF'),
    ('user3@example.com', 'User3', 'password3', '12:34:56:78:90:AB');

INSERT INTO Kasetony (IdK, Rzad, Kolumna, Jasnosc, Czerwony, Zielony, Niebieski, AdresMAC) VALUES
    (1, 'A', '1', '50%', 255, 0, 0, '00:11:22:33:44:55'),
    (2, 'B', '2', '75%', 0, 128, 255, 'AA:BB:CC:DD:EE:FF'),
    (3, 'C', '3', '100%', 255, 255, 255, '12:34:56:78:90:AB');

INSERT INTO Grupy (IdGr, NazwaGr) VALUES
    (1, 'Grupa1'),
    (2, 'Grupa2'),
    (3, 'Grupa3');

INSERT INTO Przypisania (IdGr, IdK) VALUES
    (1, 1),
    (1, 2),
    (2, 2),
    (3, 3);