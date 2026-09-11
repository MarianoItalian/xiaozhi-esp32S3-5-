# Ustalenia sprzętowe — Xiaozhi na JC8048W550C

## Potwierdzony wariant

- Płytka: **Guition JC8048W550C**
- Mikrokontroler: ESP32-S3
- Pamięć: 16 MB Flash, 8 MB OPI PSRAM
- Wyświetlacz: 5 cali, IPS, 800×480
- Dotyk: pojemnościowy, kontroler GT911 (biblioteka TAMC_GT911 w projekcie referencyjnym)

## Zweryfikowane sygnały z projektu referencyjnego użytkownika

| Funkcja | GPIO |
| --- | ---: |
| Podświetlenie | 2 |
| Touch SDA | 19 |
| Touch SCL | 20 |
| SD CS | 10 |
| SD MISO | 11 |
| SD SCK | 12 |
| SD MOSI | 13 |
| I2S BCLK | 0 |
| I2S LRCK/WS | 18 |
| I2S DOUT | 17 |

## Ustawienia znane z działającego projektu Arduino

- Board: ESP32S3 Dev Module
- USB CDC On Boot: Enabled
- Flash Mode: QIO 80 MHz
- Flash Size: 16 MB
- PSRAM: OPI PSRAM
- CPU: 240 MHz (Wi-Fi)
- Arduino-ESP32: 3.2.0 lub nowszy

## Istotna luka do sprawdzenia

Projekt AVI potwierdza tor wyjściowy I2S do głośnika, lecz pełny Xiaozhi wymaga również wejścia mikrofonowego. Należy ustalić, czy JC8048W550C ma wbudowany mikrofon/ADC audio i jakie piny wykorzystuje, czy trzeba dołączyć zewnętrzny mikrofon I2S.

## Źródła

1. https://github.com/MarianoItalian/AVI-Player-for-JC8048W550C
2. https://github.com/78/xiaozhi-esp32
3. https://www.aliexpress.com/item/1005007609869737.html
