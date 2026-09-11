# Notatki z przeglądu repozytorium

Źródło: <https://github.com/MarianoItalian/AVI-Player-for-JC8048W550C>

## Stan repozytorium

- Repozytorium publiczne, gałąź `main`, 2 commity, bez wydań i tagów.
- Katalog główny zawiera `README.md` oraz folder `na github/` z właściwym projektem.
- Ostatnie aktualizacje: 23 marca 2026 r.

## Zidentyfikowane pliki projektu

Folder `na github/` zawiera m.in.:

- `avi/` — przykładowe materiały AVI;
- `AviFunc.h` — prawdopodobna logika odtwarzania AVI;
- `cinepak.h` — dekoder/obsługa Cinepak;
- `esp32_audio.h` — audio I2S;
- `FreeSansBold12pt7b.h` — font interfejsu;
- `JC8048W550C_avi_player.bin` — skompilowany firmware;
- `arduino-libhelix-main.zip` i `avilib-master.zip` — zależności ZIP;
- `README.md`.

## Wymagania deklarowane przez README

- Wyświetlacz/płytka: JC8048W550C, 800×480, ESP32-S3.
- Arduino IDE: `ESP32S3 Dev Module`, Core ESP32 3.2.0 lub nowszy, 16 MB Flash, `16M Flash (3MB APP/9.9MB FATFS)`, OPI PSRAM, Flash QIO 80 MHz, CPU 240 MHz, USB CDC on Boot włączony.
- Biblioteki z Managera: `GFX Library for Arduino` 1.5.6 i `TAMC_GT911` 1.0.2.
- AVI w folderze `/avi` na karcie SD; rekomendowana konwersja: Cinepak, 24 fps, 800×480, MP3 mono 22 050 Hz.

## Mapa pinów z README

| Funkcja | GPIO |
|---|---:|
| Backlight | 2 |
| Touch SDA | 19 |
| Touch SCL | 20 |
| SD CS | 10 |
| SD MISO | 11 |
| SD SCK | 12 |
| SD MOSI | 13 |
| I2S BCLK | 0 |
| I2S LRCK | 18 |
| I2S DOUT | 17 |

> To są wstępne ustalenia z dokumentacji. Analiza logiki i zgodności konfiguracji wymaga jeszcze odczytu kodu źródłowego.

Status: notatki zebrane; kod nie był kompilowany ani modyfikowany.

## Ustalenia z `AviFunc.h`

- Moduł włącza obsługę **Cinepak** oraz audio (`AVI_SUPPORT_CINEPAK`, `AVI_SUPPORT_AUDIO`); obsługa MJPEG jest obecnie wyłączona komentarzem.
- Bufor wideo jest alokowany z pamięci zdolnej do DMA przez `heap_caps_malloc(..., MALLOC_CAP_8BIT)` i jego szacowany rozmiar wynosi `gfx->width() * gfx->height() * 2 / 3`.
- Przed odczytem klatki kod porównuje jej rozmiar z pojemnością bufora. Zbyt dużą klatkę pomija i raportuje przez port szeregowy, zamiast ryzykować nadpisanie pamięci.
- Odtwarzanie oblicza harmonogram klatek ze zdefiniowanego FPS AVI. Gdy rendering opóźnia się o więcej niż `SKIP_FRAME_TOLERANT_MS` (250 ms), implementacja może pomijać klatki MJPEG; dla Cinepak kod odczytuje i dekoduje aktualną klatkę.
- Po odczycie `AVI_read_frame()` klatki Cinepak są dekodowane przez `cinepak.decodeFrame(...)` do bufora wyjściowego. Kod zbiera czasy odczytu i dekodowania, co pozwala diagnozować wydajność.

> W katalogu `avi/` są wyłącznie dwa pliki demonstracyjne AVI; nie ma tam szkicu Arduino. Wykaz plików katalogu głównego również nie zawiera pliku `.ino`, dlatego dalsza analiza ma ustalić, czy właściwy szkic jest pominięty z repozytorium albo osadzony w innym pliku.

Status: kod odczytany do analizy; nie był uruchamiany, kompilowany ani modyfikowany.

## Weryfikacja kompletności i porównanie z upstreamem

Pełne drzewo gałęzi `main` potwierdza, że obecne repozytorium zawiera dokładnie 12 wpisów: dokumentację, trzy moduły `.h`, font, dwa archiwa zależności, dwa przykładowe AVI, katalog oraz binarny obraz flash. **Nie ma pliku `.ino`, `sketch.yaml`, `platformio.ini` ani innego punktu wejścia aplikacji.** Brak szkicu nie jest więc wyłącznie błędem prezentacji interfejsu GitHub, lecz brakiem w commicie.

Projekt bazowy `thelastoutpostworkshop/JC4827W543_avi_player` zawiera plik `JC4827W543_avi_player.ino` oraz `sketch.yaml`, obok analogicznych plików `AviFunc.h`, `cinepak.h`, `esp32_audio.h` i fontu. Upstream opisuje, że szkic skanuje AVI na SD, pokazuje prosty wybór pliku na ekranie dotykowym i odtwarza wybrane wideo z audio. To wskazuje, że brakujący szkic w obecnym repozytorium byłby właśnie miejscem konfiguracji wyświetlacza, GT911, SD, UI i pętli wywołującej funkcje z `AviFunc.h`.

Historia bieżącego repozytorium to dwa commity z 23 marca 2026 r.: pierwszy dodał pliki, a drugi zmienił README. Nie ma późniejszej historii mogącej zawierać usunięty punkt wejścia.

Status: analiza wykazała brak kompletnego kodu źródłowego; firmware nie może być zrekonstruowany ani skompilowany wyłącznie z bieżącego drzewa bez decyzji o dodaniu/adaptacji szkicu.
