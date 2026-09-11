# Ustalenia sprzętowe V02 — Xiaozhi na JC8048W550C

## Stan identyfikacji

Płytka została potwierdzona jako **Guition JC8048W550C / JC8048W550C_I** z ESP32-S3, 16 MB Flash, 8 MB OPI PSRAM, ekranem IPS 800×480 i pojemnościowym kontrolerem dotyku GT911.

Zgodnie z decyzją użytkownika mapa z repozytorium `MarianoItalian/AVI-Player-for-JC8048W550C` jest bazą. Repozytorium zawiera jednak tabelę peryferiów i gotowy plik BIN, ale nie zawiera głównego szkicu z pełną mapą 16-bitowej magistrali RGB. Brakujące sygnały RGB zostały uzupełnione na podstawie oficjalnego pakietu producenta i publicznej definicji `JC8048W550C.json`.

## Zweryfikowana mapa wyświetlacza RGB565

| Funkcja | GPIO |
| --- | ---: |
| HSYNC | 39 |
| VSYNC | 41 |
| DE | 40 |
| PCLK | 42 |
| B0 | 8 |
| B1 | 3 |
| B2 | 46 |
| B3 | 9 |
| B4 | 1 |
| G0 | 5 |
| G1 | 6 |
| G2 | 7 |
| G3 | 15 |
| G4 | 16 |
| G5 | 4 |
| R0 | 45 |
| R1 | 48 |
| R2 | 47 |
| R3 | 21 |
| R4 | 14 |
| Podświetlenie | 2 |

Parametry startowe panelu: **ST7262, RGB565, PCLK 16 MHz**, impulsy synchronizacji 4 px/linie oraz porches 8/8 według definicji płytki. W razie migotania PCLK będzie dostrojony dopiero podczas testu fizycznego.

## Dotyk GT911

| Funkcja | GPIO |
| --- | ---: |
| SDA | 19 |
| SCL | 20 |
| RESET | 38 |
| INT | nieużywany / `GPIO_NUM_NC` |

Oficjalny przykład producenta używa GT911 w trybie odpytywania, z `INT = -1`. To usuwa potencjalną kolizję GPIO18 z audio. Rozdzielczość kontrolera: 800×480. W bazowym przykładzie współrzędne są odwrócone w obu osiach przez mapowanie 800→0 i 480→0; finalną orientację trzeba potwierdzić dotykiem na sprzęcie.

## Audio wbudowane

| Funkcja | GPIO |
| --- | ---: |
| I2S BCLK | 0 |
| I2S LRCLK/WS | 18 |
| I2S DOUT do wzmacniacza | 17 |
| Złącze głośnika | JST 1.25, 2-pin |

Schemat pokazuje cyfrowy wzmacniacz I2S klasy D z wyjściem na złącze `Speak`. Tor ten zapewnia **wyłącznie odtwarzanie dźwięku**. Dokumentacja i schemat nie pokazują wbudowanego mikrofonu ani wejściowego kodeka/ADC audio.

Pełny chatbot Xiaozhi wymaga zatem zewnętrznego mikrofonu cyfrowego I2S lub innego wejścia audio. Najbezpieczniejsza architektura to pozostawienie wbudowanego wzmacniacza na GPIO0/18/17 i dołączenie mikrofonu I2S z osobnym `DIN`, współdzielącego BCLK i WS, o ile wybrany mikrofon obsługuje te częstotliwości. Wolny GPIO dla `DIN` trzeba wybrać z dostępnych wyprowadzeń płytki i potwierdzić elektrycznie.

## Karta microSD

| Funkcja | GPIO |
| --- | ---: |
| CS | 10 |
| MISO | 11 |
| SCK | 12 |
| MOSI | 13 |

Ta mapa jest przyjęta zgodnie z repozytorium użytkownika. Publiczna definicja PlatformIO podaje zamienione role GPIO11/13, dlatego SD nie będzie traktowana jako krytyczna dla pierwszego uruchomienia Xiaozhi; zostanie zweryfikowana oddzielnym testem dopiero po uruchomieniu ekranu, dotyku i audio.

## Źródła

1. https://github.com/MarianoItalian/AVI-Player-for-JC8048W550C
2. https://github.com/78/xiaozhi-esp32
3. https://github.com/rzeldent/platformio-espressif32-sunton/blob/main/JC8048W550C.json
4. Oficjalny pakiet producenta `JC8048W550.zip`, w tym `JC8048W550-1.png`, `5.0 inches IO pin distribution.xlsx`, specyfikacja oraz przykłady GT911 i audio.
