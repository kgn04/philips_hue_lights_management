INSERT INTO Huby (AdresMAC, AdresIP, LoginH, Rzedy, Kolumny) VALUES
    ('00:11:22:33:44:55', '192.168.1.1', 'HubyUser1',4, 4),
    ('AA:BB:CC:DD:EE:FF', '192.168.1.2', 'HubyUser2', 1, 6),
    ('12:34:56:78:90:AB', '192.168.1.3', 'HubyUser3', 0, 0);

INSERT INTO Uzytkownicy (Email, Username, Haslo) VALUES
    ('user1@example.com', 'User1', 'password1'),
    ('user2@example.com', 'User2', 'password2'),
    ('user3@example.com', 'User3', 'password3');

INSERT INTO Przydzielenia (Email, AdresMAC) VALUES
    ('user1@example.com', '00:11:22:33:44:55'),
    ('user1@example.com', 'AA:BB:CC:DD:EE:FF'),
    ('user2@example.com', '00:11:22:33:44:55'),
    ('user3@example.com', '00:11:22:33:44:55');

INSERT INTO Kasetony (IdK, Rzad, Kolumna, CzyWlaczony, Jasnosc, Czerwony, Zielony, Niebieski, AdresMAC) VALUES
    (1, 1, 1, 1, 128, 255, 0, 0, '00:11:22:33:44:55'),
    (2, 1, 2, 0, 196, 0, 128, 255, 'AA:BB:CC:DD:EE:FF'),
    (3, 2, 1, 1, 255, 255, 255, 255, '12:34:56:78:90:AB');

INSERT INTO Grupy (IdGr, NazwaGr) VALUES
    (1, 'Grupa1'),
    (2, 'Grupa2'),
    (3, 'Grupa3');

INSERT INTO Przypisania (IdGr, IdK) VALUES
    (1, 1),
    (1, 2),
    (2, 2),
    (3, 3);