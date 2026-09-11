# Guition JC8048W550C + INMP441

This board definition targets the Guition JC8048W550C / JC8048W550C_I with an ESP32-S3, 16 MB flash, 8 MB OPI PSRAM, an 800x480 ST7262-compatible RGB display, and GT911 capacitive touch.

## Audio

The onboard I2S amplifier is used for speaker output. An external INMP441 provides microphone input on a separate I2S controller.

| INMP441 pin | JC8048W550C signal | GPIO |
| --- | --- | ---: |
| VDD | 3.3 V | — |
| GND | GND | — |
| SCK | microSD SCK | 12 |
| WS | microSD MOSI | 13 |
| SD | microSD MISO | 11 |
| L/R | GND (left channel) | — |

The INMP441 must be powered from **3.3 V**, not 5 V.

## microSD limitation

GPIO11, GPIO12, and GPIO13 are reassigned to the INMP441. The microSD socket is therefore intentionally unavailable in this firmware variant.

## Touch behavior

GT911 is connected through I2C on GPIO19/GPIO20 with reset on GPIO38. Its interrupt line is not used because GPIO18 is reserved for the onboard I2S amplifier. The center 320x320 area of the standard Xiaozhi screen is touch-enabled; a tap toggles the current conversation state.

## Build

Use the canonical Xiaozhi build script:

```sh
python3 scripts/build.py guition/jc8048w550c --name guition-jc8048w550c-inmp441
```

Language and wake-word settings remain user build options and are not hard-coded into the board definition.

## Hardware validation

A successful build validates only the software configuration. Physical testing is still required for display timing, touch orientation, microphone channel alignment, speaker playback, and interaction with the selected Xiaozhi server.
