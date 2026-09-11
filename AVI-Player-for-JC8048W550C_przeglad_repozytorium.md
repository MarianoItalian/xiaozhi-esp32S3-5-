# Przegląd techniczny — AVI Player for JC8048W550C

**Repozytorium:** `MarianoItalian/AVI-Player-for-JC8048W550C`  
**Przegląd wykonany:** 7 września 2026 r.  
**Zakres:** odczyt publicznego repozytorium i binarnego obrazu firmware; bez zmian, kompilacji, flashowania ani uruchamiania na sprzęcie.

## Wniosek wykonawczy

Repozytorium jest adaptacją odtwarzacza AVI dla płytki **JC8048W550C** z ESP32-S3 i ekranem 800×480. Projekt jest zaprojektowany do odczytu plików AVI z karty SD, dekodowania obrazu **Cinepak**, dekodowania ścieżki **MP3** oraz wypuszczania audio przez I2S. Dokumentacja określa docelową konfigurację Arduino IDE i mapę użytych GPIO.[1]

Najważniejszy fakt: aktualna gałąź `main` **nie jest kompletnym projektem źródłowym**. Zawiera moduły odtwarzania, dekodera i audio, ale nie zawiera żadnego pliku `.ino`, `setup()`, `loop()`, `sketch.yaml` ani konfiguracji PlatformIO. Pełne drzewo GitHub potwierdza brak punktu wejścia aplikacji.[2] Z tego powodu nie można obecnie skompilować ani sensownie zmodyfikować projektu wyłącznie na podstawie zawartości tego repozytorium.

| Obszar | Ocena | Konsekwencja praktyczna |
|---|---|---|
| Odtworzenie gotowego firmware | **Częściowo możliwe** | W repozytorium jest 16‑MB obraz flash, jednak jego działanie na fizycznej płytce nie było weryfikowane. |
| Kompilacja ze źródeł | **Zablokowana** | Brakuje głównego szkicu oraz deklaracji konfiguracji projektu. |
| Zmiana UI, pinów panelu lub obsługi dotyku | **Zablokowana** | Te elementy powinny znajdować się w brakującym punkcie wejścia. |
| Analiza silnika AVI i audio | **Możliwa** | Dostępne są moduły `AviFunc.h`, `cinepak.h` i `esp32_audio.h`. |
| Konfiguracja karty SD oraz kodowanie materiału | **Udokumentowana** | README podaje strukturę folderu i komendę FFmpeg.[1] |

## Stan i struktura repozytorium

Historia gałęzi `main` zawiera dwa commity z 23 marca 2026 r. Pierwszy dodał pliki, a drugi zmodyfikował README; nie ma późniejszego commitu, w którym szkic mógłby zostać usunięty.[3] Katalog `na github/` zawiera trzy moduły źródłowe, font, dwa archiwa bibliotek, dwa przykładowe pliki AVI oraz plik binarny. Katalog `avi/` ma wyłącznie materiały demonstracyjne; nie ukrywa kodu aplikacji.[2]

| Element | Rola | Stan |
|---|---|---|
| `AviFunc.h` | Otwieranie AVI, odczyt klatek/audio, synchronizacja i statystyki. | Dostępny. |
| `cinepak.h` | Dekoder Cinepak zapisujący obraz w RGB565. | Dostępny. |
| `esp32_audio.h` | I2S oraz zadanie dekodera MP3 Helix. | Dostępny. |
| `FreeSansBold12pt7b.h` | Font interfejsu użytkownika. | Dostępny. |
| `avilib-master.zip` | Biblioteka obsługi kontenera AVI. | Dostępna. |
| `arduino-libhelix-main.zip` | Biblioteka dekodera MP3. | Dostępna. |
| `JC8048W550C_avi_player.bin` | Binarna zawartość pamięci flash. | Dostępna, lecz nieuruchamiana w ramach przeglądu. |
| Główny szkic Arduino | Inicjalizacja ekranu, SD, dotyku, UI i pętli odtwarzania. | **Brak.** |

## Jak działa dostępny silnik odtwarzania

`AviFunc.h` włącza dekoder Cinepak oraz audio, natomiast obsługa MJPEG pozostaje zakomentowana. Po otwarciu pliku odczytywany jest kontener AVI: liczba klatek, rozdzielczość, FPS, identyfikator kodeka oraz parametry audio. Dla identyfikatora `cvid` aktywowana jest ścieżka Cinepak.[4]

Dla każdej klatki moduł najpierw sprawdza, czy jej rozmiar mieści się w buforze wideo. Bufor ma rozmiar równy dwóm trzecim pełnej powierzchni ekranu RGB565, czyli dla 800×480 około **512 000 B**. Klatka przekraczająca limit jest pomijana, co chroni pamięć przed nadpisaniem, ale może powodować widoczne skoki w materiale o dużych klatkach kluczowych.[4]

Dekoder Cinepak przetwarza strumień na bufor `RGB565`; w wersji przeznaczonej dla panelu SPI używany jest wariant big-endian, a późniejsze wyświetlenie następuje przez `draw16bitBeRGBBitmap()`. Implementacja mierzy osobno czas odczytu, dekodowania i rysowania, a po zakończeniu wypisuje rzeczywisty FPS oraz liczbę pominiętych klatek przez port szeregowy.[4]

Audio jest buforowane porcjami do 3072 B i odtwarzane przez I2S0. Moduł używa `MP3DecoderHelix`, automatycznie przełącza częstotliwość I2S na tę wykrytą w ramce MP3 i uruchamia zadanie odtwarzacza przypięte do rdzenia 0 z wysokim priorytetem.[5] Moduł deklaruje zewnętrzną zmienną `volumeLevel`; jej definicja musiała znajdować się w brakującym szkicu lub innym komponencie aplikacji.[5]

## Docelowy sprzęt i konfiguracja

README wymaga płytki **ESP32S3 Dev Module**, 16 MB Flash, OPI PSRAM, QIO 80 MHz, CPU 240 MHz oraz rdzenia Arduino‑ESP32 3.2.0 lub nowszego. Wskazuje też biblioteki GFX Library for Arduino 1.5.6 oraz TAMC_GT911 1.0.2, a dwie pozostałe zależności dostarcza jako ZIP.[1]

| Funkcja | GPIO | Potwierdzenie |
|---|---:|---|
| Podświetlenie | 2 | README.[1] |
| Dotyk SDA / SCL | 19 / 20 | README.[1] |
| SD: CS / MISO / SCK / MOSI | 10 / 11 / 12 / 13 | README.[1] |
| I2S: BCLK / LRCK / DOUT | 0 / 18 / 17 | README i `esp32_audio.h`.[1] [5] |

Dostępne pliki nie zawierają inicjalizacji kontrolera LCD, GT911 ani magistrali SD. Można jedynie stwierdzić, że oczekują one istniejącego obiektu `gfx`, pełnego bufora wyjściowego `output_buf` i konfiguracji panelu wykonanej poza modułami.[4] Z tego względu poprawności mapy pinów dla ekranu i dotyku nie można potwierdzić na podstawie aktualnego drzewa.

## Format materiałów AVI

Odtwarzacz oczekuje plików w folderze `/avi` na karcie SD. Dokumentacja zaleca Cinepak, 24 fps, skalowanie do 800×480 oraz MP3 mono 22 050 Hz. Rozdzielczość musi być wielokrotnością czterech, co wynika z blokowego sposobu dekodowania Cinepak.[1] Zalecenie jest zgodne z aktywną obsługą kodeka `cvid` w `AviFunc.h`.[4]

> `ffmpeg -i input.mp4 -c:v cinepak -q:v 10 -vf "fps=24,scale=800:480" -c:a mp3 -ac 1 -ar 22050 output.avi`  
> — komenda konwersji podana w README repozytorium.[1]

## Binarne firmware

Plik `JC8048W550C_avi_player.bin` ma dokładnie **16 777 216 B**, czyli pełne 16 MiB pamięci flash.[2] Odczyt nagłówka wykazał obraz ESP, a wpis w adresie `0x8000` zawiera tablicę partycji. To wskazuje, że plik jest pełnym, surowym obrazem flash, a nie samym binarnym artefaktem aplikacji.

| Partycja wykryta w obrazie | Offset | Rozmiar | Znaczenie |
|---|---:|---:|---|
| `nvs` | `0x9000` | `0x5000` | Konfiguracja NVS. |
| `otadata` | `0xE000` | `0x2000` | Metadane OTA. |
| `app0` | `0x10000` | `0x300000` | Pierwszy slot aplikacji, 3 MiB. |
| `app1` | `0x310000` | `0x300000` | Drugi slot OTA aplikacji, 3 MiB. |
| `fat` | `0x610000` | `0x9E0000` | Partycja FATFS, około 9,9 MiB. |
| `coredump` | `0xFF0000` | `0x10000` | Zrzuty awaryjne. |

Układ jest spójny z deklaracją README o 16 MB Flash i około 9,9 MB FATFS, ale dodatkowo pokazuje dwa 3‑MiB sloty aplikacji przeznaczone dla OTA.[1] **Nie flashowałem tego obrazu ani nie potwierdzam jego zgodności z konkretną wersją sprzętową.**

## Porównanie z projektem bazowym

README wskazuje projekt `thelastoutpostworkshop/JC4827W543_avi_player` jako podstawę.[1] W upstreamie istnieje plik `JC4827W543_avi_player.ino` oraz `sketch.yaml`. Szkic inicjalizuje ekran, dotyk, I2S i SD, skanuje maksymalnie 10 plików AVI, pokazuje prosty selektor dotykowy oraz wywołuje funkcje `avi_open()`, `avi_feed_audio()`, `avi_decode()` i `avi_draw()`.[6] To potwierdza, że właśnie odpowiednik tego szkicu powinien być głównym brakującym elementem aktualnego repozytorium.

Nie należy jednak kopiować upstreamu bez adaptacji. JC4827W543 ma ekran 480×272 i inną mapę pinów niż JC8048W550C, dlatego właściwy plik dla Twojej płytki powinien zachować logikę odtwarzania, ale jawnie ustawić sterownik 800×480, piny SD, I2S i GT911 z aktualnego README.[1] [6]

## Ocena i następny logiczny krok

Repozytorium jest dobrą **paczką runtime**: ma demonstracyjne AVI, moduły dekodera, biblioteki oraz pełny obraz flash. Nie jest jednak dobrą **bazą rozwojową**, ponieważ brakuje najważniejszego pliku źródłowego, który spina wszystkie elementy. Nie ma też automatycznej kompilacji, schematu konfiguracji ani instrukcji flashowania binarnego obrazu.

Najbardziej racjonalna kolejność prac jest następująca: najpierw odzyskać lub odtworzyć dedykowany szkic `.ino` dla JC8048W550C; następnie dodać powtarzalną konfigurację kompilacji; dopiero później kompilować i testować na płytce. Bez tego każda zmiana w UI, pinach, audio albo odtwarzaniu będzie oparta na domysłach.

## Referencje

[1]: https://github.com/MarianoItalian/AVI-Player-for-JC8048W550C/blob/main/README.md "README — AVI Player for JC8048W550C"
[2]: https://api.github.com/repos/MarianoItalian/AVI-Player-for-JC8048W550C/git/trees/main?recursive=1 "Pełne drzewo plików gałęzi main"
[3]: https://api.github.com/repos/MarianoItalian/AVI-Player-for-JC8048W550C/commits?sha=main&per_page=100 "Historia commitów repozytorium"
[4]: https://raw.githubusercontent.com/MarianoItalian/AVI-Player-for-JC8048W550C/main/na%20github/AviFunc.h "AviFunc.h"
[5]: https://raw.githubusercontent.com/MarianoItalian/AVI-Player-for-JC8048W550C/main/na%20github/esp32_audio.h "esp32_audio.h"
[6]: https://github.com/thelastoutpostworkshop/JC4827W543_avi_player/blob/main/JC4827W543_avi_player.ino "Szkic projektu bazowego JC4827W543"
