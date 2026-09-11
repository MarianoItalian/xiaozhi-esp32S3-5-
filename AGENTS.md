# Konfiguracja współpracy — Folder MANUS

Ten folder jest wspólną przestrzenią roboczą dla projektów użytkownika, w tym Bloodwitcher i Bladywiczer oraz przyszłych projektów sprzętowych, programistycznych i kreatywnych.

## Zakres dostępu i organizacja

- Pracuj wyłącznie wewnątrz tego folderu, chyba że użytkownik wyraźnie wskaże inny katalog.
- Każdy nowy, niezależny projekt zapisuj w osobnym katalogu o opisowej nazwie.
- Nie usuwaj, nie przenoś ani nie nadpisuj istniejących plików bez jednoznacznej prośby użytkownika.
- Przed większą zmianą zachowaj poprzednią wersję pliku. Nowe wersje zapisuj pod nową, opisową nazwą.
- Wykorzystuj istniejący katalog projektu dla jego kolejnych wersji i wyników; nie twórz duplikatów katalogów bez potrzeby.

## Kod, firmware i projekty sprzętowe

- Przed zmianą kodu ustalaj z plików lub od użytkownika docelowy sprzęt, płytkę, środowisko, bibliotekę oraz istotne ograniczenia projektu. Nie zakładaj, że każdy projekt używa ESP8266 ani ESP32.
- Dla firmware przed zapisem zmodyfikowanego pliku `.ino` kompiluj go dla właściwej płytki i platformy, gdy środowisko na to pozwala.
- Jeżeli docelowy sprzęt, platforma lub konfiguracja kompilacji nie są pewne, najpierw zadaj jedno konkretne pytanie.
- W pliku wynikowym zachowuj wszystkie wcześniej zaakceptowane poprawki, chyba że użytkownik wyraźnie zażąda inaczej.
- Nie przedstawiaj kodu jako sprawdzonego, jeśli kompilacja, test lub inna wymagana weryfikacja nie powiodły się.
- Gotowe pliki kodu zapisuj pod opisowymi nazwami, np. `NazwaProjektu_V01_opis_zmiany.ino`.
- Tylko Przy większych zmianach dostarczaj kompletny plik gotowy do użycia zamiast wielu ręcznych edycji. Jeżeli sa to tylko male poprawki powiedz to użytkownikowi i jeśli użytkownik da rade sam nanieść te poprawki to podaj mu tylko te linijki kodu które należy zmienić.
- dla tworzenia nowego pliku unikaj zbędnych pobran, przeszukiwan online lub instalacji aplikacji które mogą narazić użytkownika na utrate tokenow lecz staraj się to robic najkrotsza dostepna droga.
- po otrzymaniu zadania unikaj zbędnych kontaktow z użytkownikiem az do pelnego zakończenia zadania chyba ze będzie to absolutnie konieczne.

## Styl współpracy

- Nie zgaduj. Przy istotnej niejasności najpierw zadaj jedno konkretne pytanie.
- Odpowiadaj krótko, rzeczowo i przedstawiaj własną ocenę, gdy ma znaczenie dla decyzji użytkownika.
- Nie dodawaj funkcji, zmian wyglądu ani zmian zachowania, o które użytkownik nie poprosił.
- Przed działaniem ryzykownym, nieodwracalnym lub wymagającym zewnętrznej publikacji wyraźnie poinformuj użytkownika i uzyskaj zgodę.
- Przy instrukcjach technicznych podawaj najwyżej jedną sprawdzoną komendę naraz oraz czekaj na wynik, nie określaj oczekiwanego wyniku.
- Po zapisaniu pliku w tym folderze potwierdź jego nazwę oraz status weryfikacji, np. kompilacji lub testu.
