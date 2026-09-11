# Architektura portu Xiaozhi dla Guition JC8048W550C

**Autor:** Manus AI  
**Status:** analiza przed implementacją

## Podstawa portu

Xiaozhi wybiera dokładnie jedną implementację płytki podczas kompilacji. Nowy model powinien otrzymać własny katalog, unikalny typ firmware i kompletny łańcuch `config.json → Kconfig → CMake → kod płytki`, aby aktualizacja OTA nie pomyliła go z innym wariantem sprzętowym.[1] Najbliższym wzorcem jest implementacja Waveshare ESP32-S3 Touch LCD 4.3C, ponieważ korzysta z ESP32-S3, panelu RGB 800×480, sterownika `RgbLcdDisplay`, kontrolera GT911 i portu LVGL.[2]

| Warstwa | Rozwiązanie dla JC8048W550C |
| --- | --- |
| Tożsamość | Nowy typ `guition-jc8048w550c`, producent `guition` |
| Mikrokontroler | `esp32s3`, 16 MB Flash, 8 MB OPI PSRAM |
| LCD | ST7262 przez równoległe RGB565, 800×480, dwa bufory w PSRAM |
| UI | Standardowy interfejs Xiaozhi na `RgbLcdDisplay` |
| Dotyk | GT911 na I2C0, SDA GPIO19, SCL GPIO20, RESET GPIO38, bez linii INT |
| Sterowanie rozmową | Zdarzenia dotykowe mapowane na bezpieczne, zdarzeniowe API `ToggleChatState`, `StartListening` i `StopListening` |
| Głośnik | Wbudowany wzmacniacz I2S: BCLK GPIO0, WS GPIO18, DOUT GPIO17 |
| Mikrofon | Zewnętrzny mikrofon cyfrowy I2S; wejście danych na wolnym GPIO37 albo alternatywnym pinie po teście |
| Audio | `NoAudioCodecDuplex`, wspólne BCLK/WS dla wzmacniacza i mikrofonu, osobne DOUT/DIN |
| Sieć | Wi-Fi 2,4 GHz przez `WifiBoard` |
| Pamięć | Domyślna partycja projektu dla 16 MB; kod i zasoby LVGL w PSRAM, gdy obsługiwane |

## Interfejs dotykowy

Samo zarejestrowanie GT911 w LVGL zapewnia kursor dotyku, lecz standardowy ekran Xiaozhi nie zawiera przycisku rozmowy. Port powinien więc dodać lekką, płytkową warstwę interakcji bez modyfikowania wspólnego kodu wyświetlacza. Najbezpieczniejszym wariantem jest podklasa `RgbLcdDisplay`, która po standardowym `SetupUI()` tworzy widoczny przycisk mikrofonu albo rejestruje gest na głównym ekranie. Callback dotykowy musi używać zdarzeniowych metod aplikacji i nie może blokować zadania LVGL.[1]

| Gest | Proponowane zachowanie |
| --- | --- |
| Krótkie dotknięcie | Rozpoczęcie rozmowy, przerwanie odpowiedzi albo zakończenie aktywnej sesji przez `ToggleChatState()` |
| Przytrzymanie przycisku | `StartListening()` podczas nacisku i `StopListening()` po puszczeniu, czyli tryb push-to-talk |
| Długie przytrzymanie podczas startu | Wejście do konfiguracji Wi-Fi, jeżeli użytkownik zatwierdzi takie zachowanie |

Pierwsza wersja powinna ograniczyć się do pojedynczego, dużego przycisku rozmowy, aby spełnić wymaganie reakcji na dotyk bez dodawania niezamówionych ekranów i menu.

## Audio i ograniczenie sprzętowe

Schemat JC8048W550C pokazuje cyfrowy wzmacniacz I2S oraz złącze głośnika, ale nie pokazuje mikrofonu ani wejściowego kodeka audio.[3] Pełny asystent głosowy wymaga zatem dołączenia mikrofonu I2S. `NoAudioCodecDuplex` w Xiaozhi obsługuje wspólne BCLK i WS oraz oddzielne linie DOUT i DIN, więc wbudowany wzmacniacz może pozostać na istniejących pinach, a zewnętrzny mikrofon dostarczać dane na wolny GPIO.[4]

| Wariant mikrofonu | Zalety | Ograniczenia | Złożoność |
| --- | --- | --- | --- |
| Mikrofon I2S współdzielący GPIO0/GPIO18, DIN na GPIO37 | Najmniej przewodów i jeden kontroler I2S; zgodny z `NoAudioCodecDuplex` | Wymaga modułu obsługującego standard I2S, właściwego kanału L/R oraz krótkich przewodów | Niska |
| Mikrofon I2S z osobnymi zegarami na wolnych pinach | Oddziela tor wejściowy od wzmacniacza i ułatwia diagnostykę | Wymaga trzech wolnych GPIO oraz `NoAudioCodecSimplex`; na tej płytce liczba wygodnie wyprowadzonych pinów jest ograniczona | Średnia |

Dla pierwszego portu preferowany technicznie jest mikrofon **INMP441, ICS-43434 lub zgodny standardowy mikrofon I2S**, zasilany 3,3 V. Konkretny moduł i kanał L/R muszą zostać potwierdzone przed finalnym przypisaniem `DIN`.

## Sposób korzystania z serwera Xiaozhi

Firmware może zostać najpierw uruchomiony z domyślną usługą Xiaozhi albo skierowany do własnego backendu. Ta decyzja nie blokuje przygotowania sterowników sprzętowych, ponieważ endpoint można skonfigurować później.

| Podejście | Kompromisy | Koszt | Złożoność konfiguracji |
| --- | --- | --- | --- |
| Domyślna usługa Xiaozhi | Najszybszy test całego toru głosowego; zależność od zewnętrznej usługi i jej zasad | Zależny od usługi | Niska |
| Własny serwer zgodny z protokołem Xiaozhi | Pełna kontrola nad modelami, głosem, prywatnością i integracjami; wymaga hosta działającego stale | Koszt hostingu i używanych modeli | Wysoka |

Na etapie pierwszego uruchomienia należy zachować możliwość obu wariantów. Wybór docelowego backendu powinien nastąpić po potwierdzeniu LCD, dotyku, odtwarzania i wejścia mikrofonowego.

## Kryteria ukończenia portu

Port będzie uznany za gotowy dopiero po poprawnej kompilacji dla ESP32-S3 oraz teście fizycznym obejmującym start systemu, obraz bez migotania, prawidłową orientację dotyku, konfigurację Wi-Fi, rejestrację dźwięku, odtwarzanie na głośniku, rozpoczęcie rozmowy dotykiem, przerwanie odpowiedzi i ponowne połączenie z serwerem. Sama kompilacja nie będzie przedstawiona jako walidacja sprzętowa.[1]

## References

[1]: https://github.com/78/xiaozhi-esp32/blob/main/AGENTS.md "Xiaozhi ESP32 — zasady architektury i walidacji"
[2]: https://github.com/78/xiaozhi-esp32/tree/main/main/boards/waveshare/esp32-s3-touch-lcd-4.3c "Waveshare ESP32-S3 Touch LCD 4.3C implementation"
[3]: http://pan.jczn1688.com/directlink/1/HMI%20display/JC8048W550.zip "Oficjalny pakiet JC8048W550 — schemat, specyfikacja i przykłady"
[4]: https://github.com/78/xiaozhi-esp32/blob/main/main/audio/codecs/no_audio_codec.cc "Xiaozhi NoAudioCodec implementation"
