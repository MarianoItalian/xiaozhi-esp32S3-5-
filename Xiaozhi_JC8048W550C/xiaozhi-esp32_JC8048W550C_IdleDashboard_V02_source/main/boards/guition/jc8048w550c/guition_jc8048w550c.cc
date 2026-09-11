#include "application.h"
#include "codecs/no_audio_codec.h"
#include "config.h"
#include "display/lcd_display.h"
#include "wifi_board.h"

#include <driver/i2c_master.h>
#include <esp_lcd_panel_io.h>
#include <esp_lcd_panel_ops.h>
#include <esp_lcd_panel_rgb.h>
#include <esp_lcd_touch_gt911.h>
#include <esp_log.h>
#include <esp_lvgl_port.h>
#include <esp_timer.h>
#include <lvgl.h>

#include <ctime>

#define TAG "GuitionJC8048W550C"

LV_FONT_DECLARE(BUILTIN_TEXT_FONT);
LV_FONT_DECLARE(BUILTIN_ICON_FONT);

namespace {
constexpr int64_t kStandbyDashboardDelayUs = 30LL * 1000 * 1000;
constexpr int64_t kEarliestValidYear = 2025 - 1900;
const lv_color_t kDashboardBackground = LV_COLOR_MAKE(0x06, 0x17, 0x24);
const lv_color_t kDashboardPanel = LV_COLOR_MAKE(0x0A, 0x26, 0x38);
const lv_color_t kDashboardCyan = LV_COLOR_MAKE(0x00, 0xD9, 0xFF);
const lv_color_t kDashboardMutedCyan = LV_COLOR_MAKE(0x71, 0xBF, 0xD2);
}  // namespace

class GuitionTouchDisplay : public RgbLcdDisplay {
private:
    lv_obj_t* touch_target_ = nullptr;
    lv_obj_t* standby_dashboard_ = nullptr;
    lv_obj_t* dashboard_clock_label_ = nullptr;
    lv_obj_t* dashboard_date_label_ = nullptr;
    lv_obj_t* dashboard_network_label_ = nullptr;
    lv_obj_t* dashboard_hint_label_ = nullptr;
    bool dashboard_visible_ = false;
    int64_t idle_started_us_ = -1;

    void UpdateDashboardTextLocked() {
        if (dashboard_clock_label_ == nullptr || dashboard_date_label_ == nullptr ||
            dashboard_network_label_ == nullptr) {
            return;
        }

        time_t now = time(nullptr);
        struct tm local_time = {};
        localtime_r(&now, &local_time);

        if (local_time.tm_year >= kEarliestValidYear) {
            char clock_text[16];
            char date_text[40];
            strftime(clock_text, sizeof(clock_text), "%H:%M", &local_time);
            strftime(date_text, sizeof(date_text), "%A, %d/%m/%Y", &local_time);
            lv_label_set_text(dashboard_clock_label_, clock_text);
            lv_label_set_text(dashboard_date_label_, date_text);
        } else {
            lv_label_set_text(dashboard_clock_label_, "--:--");
            lv_label_set_text(dashboard_date_label_, "Oczekiwanie na synchronizacje czasu");
        }

        const char* network_icon = Board::GetInstance().GetNetworkStateIcon();
        lv_label_set_text(dashboard_network_label_, network_icon != nullptr ? network_icon : "");

        // The clock label is intentionally enlarged without introducing a second font asset.
        // Its transform origin must be recalculated after every text update.
        lv_obj_update_layout(dashboard_clock_label_);
        lv_obj_set_style_transform_pivot_x(dashboard_clock_label_,
                                           lv_obj_get_width(dashboard_clock_label_) / 2, 0);
        lv_obj_set_style_transform_pivot_y(dashboard_clock_label_,
                                           lv_obj_get_height(dashboard_clock_label_) / 2, 0);
    }

    void ShowDashboard() {
        if (standby_dashboard_ == nullptr || dashboard_visible_) {
            return;
        }

        DisplayLockGuard lock(this);
        UpdateDashboardTextLocked();
        lv_obj_remove_flag(standby_dashboard_, LV_OBJ_FLAG_HIDDEN);
        lv_obj_move_foreground(standby_dashboard_);
        dashboard_visible_ = true;
        ESP_LOGI(TAG, "Standby dashboard shown after 30 seconds of inactivity");
    }

    void HideDashboard() {
        if (standby_dashboard_ == nullptr || !dashboard_visible_) {
            return;
        }

        DisplayLockGuard lock(this);
        lv_obj_add_flag(standby_dashboard_, LV_OBJ_FLAG_HIDDEN);
        dashboard_visible_ = false;
        ESP_LOGI(TAG, "Standby dashboard hidden");
    }

    void MarkActivity() {
        idle_started_us_ = -1;
        HideDashboard();
    }

    void CreateStandbyDashboard() {
        auto screen = lv_screen_active();
        standby_dashboard_ = lv_obj_create(screen);
        lv_obj_set_size(standby_dashboard_, LV_HOR_RES, LV_VER_RES);
        lv_obj_set_style_radius(standby_dashboard_, 0, 0);
        lv_obj_set_style_bg_color(standby_dashboard_, kDashboardBackground, 0);
        lv_obj_set_style_bg_opa(standby_dashboard_, LV_OPA_COVER, 0);
        lv_obj_set_style_border_width(standby_dashboard_, 0, 0);
        lv_obj_set_style_pad_all(standby_dashboard_, 0, 0);
        lv_obj_remove_flag(standby_dashboard_, LV_OBJ_FLAG_SCROLLABLE);
        lv_obj_add_flag(standby_dashboard_, LV_OBJ_FLAG_CLICKABLE);
        lv_obj_add_flag(standby_dashboard_, LV_OBJ_FLAG_HIDDEN);

        // Top status line: it deliberately uses the existing Xiaozhi network icon.
        auto title_label = lv_label_create(standby_dashboard_);
        lv_label_set_text(title_label, "XIAOZHI");
        lv_obj_set_style_text_font(title_label, &BUILTIN_TEXT_FONT, 0);
        lv_obj_set_style_text_color(title_label, kDashboardCyan, 0);
        lv_obj_align(title_label, LV_ALIGN_TOP_MID, 0, 32);

        dashboard_network_label_ = lv_label_create(standby_dashboard_);
        lv_label_set_text(dashboard_network_label_, "");
        lv_obj_set_style_text_font(dashboard_network_label_, &BUILTIN_ICON_FONT, 0);
        lv_obj_set_style_text_color(dashboard_network_label_, kDashboardCyan, 0);
        lv_obj_align(dashboard_network_label_, LV_ALIGN_TOP_MID, -112, 32);

        auto state_label = lv_label_create(standby_dashboard_);
        lv_label_set_text(state_label, "CZUWANIE");
        lv_obj_set_style_text_font(state_label, &BUILTIN_TEXT_FONT, 0);
        lv_obj_set_style_text_color(state_label, kDashboardMutedCyan, 0);
        lv_obj_align(state_label, LV_ALIGN_TOP_MID, 0, 76);

        // A framed clock area keeps the layout close to the requested clock dashboard.
        auto clock_panel = lv_obj_create(standby_dashboard_);
        lv_obj_set_size(clock_panel, 630, 212);
        lv_obj_set_style_radius(clock_panel, 18, 0);
        lv_obj_set_style_bg_color(clock_panel, kDashboardPanel, 0);
        lv_obj_set_style_bg_opa(clock_panel, LV_OPA_COVER, 0);
        lv_obj_set_style_border_width(clock_panel, 2, 0);
        lv_obj_set_style_border_color(clock_panel, kDashboardMutedCyan, 0);
        lv_obj_set_style_pad_all(clock_panel, 0, 0);
        lv_obj_remove_flag(clock_panel, LV_OBJ_FLAG_SCROLLABLE);
        lv_obj_align(clock_panel, LV_ALIGN_CENTER, 0, 8);

        dashboard_clock_label_ = lv_label_create(clock_panel);
        lv_label_set_text(dashboard_clock_label_, "--:--");
        lv_obj_set_style_text_font(dashboard_clock_label_, &BUILTIN_TEXT_FONT, 0);
        lv_obj_set_style_text_color(dashboard_clock_label_, kDashboardCyan, 0);
        lv_obj_set_style_text_letter_space(dashboard_clock_label_, 4, 0);
        lv_obj_set_style_transform_scale(dashboard_clock_label_, 720, 0);
        lv_obj_align(dashboard_clock_label_, LV_ALIGN_CENTER, 0, 0);

        dashboard_date_label_ = lv_label_create(standby_dashboard_);
        lv_label_set_text(dashboard_date_label_, "Oczekiwanie na synchronizacje czasu");
        lv_obj_set_style_text_font(dashboard_date_label_, &BUILTIN_TEXT_FONT, 0);
        lv_obj_set_style_text_color(dashboard_date_label_, kDashboardMutedCyan, 0);
        lv_obj_set_width(dashboard_date_label_, 720);
        lv_obj_set_style_text_align(dashboard_date_label_, LV_TEXT_ALIGN_CENTER, 0);
        lv_obj_align(dashboard_date_label_, LV_ALIGN_BOTTOM_MID, 0, -94);

        dashboard_hint_label_ = lv_label_create(standby_dashboard_);
        lv_label_set_text(dashboard_hint_label_, "Dotknij ekranu, aby rozpoczac rozmowe");
        lv_obj_set_style_text_font(dashboard_hint_label_, &BUILTIN_TEXT_FONT, 0);
        lv_obj_set_style_text_color(dashboard_hint_label_, kDashboardCyan, 0);
        lv_obj_set_width(dashboard_hint_label_, 720);
        lv_obj_set_style_text_align(dashboard_hint_label_, LV_TEXT_ALIGN_CENTER, 0);
        lv_obj_align(dashboard_hint_label_, LV_ALIGN_BOTTOM_MID, 0, -42);

        lv_obj_add_event_cb(
            standby_dashboard_,
            [](lv_event_t* event) {
                if (lv_event_get_code(event) != LV_EVENT_CLICKED) {
                    return;
                }

                auto* display = static_cast<GuitionTouchDisplay*>(lv_event_get_user_data(event));
                if (display == nullptr || !display->dashboard_visible_) {
                    return;
                }

                // This callback is already executing in the LVGL task; do not lock recursively.
                lv_obj_add_flag(display->standby_dashboard_, LV_OBJ_FLAG_HIDDEN);
                display->dashboard_visible_ = false;
                display->idle_started_us_ = -1;
                Application::GetInstance().ToggleChatState();
            },
            LV_EVENT_CLICKED, this);
    }

public:
    GuitionTouchDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel, int width,
                        int height, int offset_x, int offset_y, bool mirror_x, bool mirror_y,
                        bool swap_xy)
        : RgbLcdDisplay(panel_io, panel, width, height, offset_x, offset_y, mirror_x, mirror_y,
                        swap_xy) {}

    void SetupUI() override {
        RgbLcdDisplay::SetupUI();
        if (touch_target_ != nullptr) {
            return;
        }

        DisplayLockGuard lock(this);
        touch_target_ = lv_obj_create(lv_screen_active());
        lv_obj_set_size(touch_target_, 320, 320);
        lv_obj_align(touch_target_, LV_ALIGN_CENTER, 0, 0);
        lv_obj_set_style_bg_opa(touch_target_, LV_OPA_TRANSP, 0);
        lv_obj_set_style_border_width(touch_target_, 0, 0);
        lv_obj_set_style_pad_all(touch_target_, 0, 0);
        lv_obj_remove_flag(touch_target_, LV_OBJ_FLAG_SCROLLABLE);
        lv_obj_add_flag(touch_target_, LV_OBJ_FLAG_CLICKABLE);
        lv_obj_add_event_cb(
            touch_target_,
            [](lv_event_t* event) {
                if (lv_event_get_code(event) == LV_EVENT_CLICKED) {
                    Application::GetInstance().ToggleChatState();
                }
            },
            LV_EVENT_CLICKED, nullptr);

        CreateStandbyDashboard();
    }

    void SetStatus(const char* status) override {
        if (Application::GetInstance().GetDeviceState() != kDeviceStateIdle) {
            MarkActivity();
        }
        RgbLcdDisplay::SetStatus(status);
    }

    void ShowNotification(const char* notification, int duration_ms = 3000) override {
        MarkActivity();
        RgbLcdDisplay::ShowNotification(notification, duration_ms);
    }

    void SetChatMessage(const char* role, const char* content) override {
        if ((content != nullptr && content[0] != '\0') ||
            Application::GetInstance().GetDeviceState() != kDeviceStateIdle) {
            MarkActivity();
        }
        RgbLcdDisplay::SetChatMessage(role, content);
    }

    void SetEmotion(const char* emotion) override {
        if (Application::GetInstance().GetDeviceState() != kDeviceStateIdle) {
            MarkActivity();
        }
        RgbLcdDisplay::SetEmotion(emotion);
    }

    void UpdateStatusBar(bool update_all = false) override {
        RgbLcdDisplay::UpdateStatusBar(update_all);

        if (Application::GetInstance().GetDeviceState() != kDeviceStateIdle) {
            MarkActivity();
            return;
        }

        const int64_t now_us = esp_timer_get_time();
        if (idle_started_us_ < 0) {
            idle_started_us_ = now_us;
            return;
        }

        if (now_us - idle_started_us_ >= kStandbyDashboardDelayUs) {
            ShowDashboard();
        }

        if (dashboard_visible_) {
            DisplayLockGuard lock(this);
            UpdateDashboardTextLocked();
        }
    }
};

class GuitionJC8048W550C : public WifiBoard {
private:
    i2c_master_bus_handle_t touch_i2c_bus_ = nullptr;
    GuitionTouchDisplay* display_ = nullptr;

    void InitializeTouchI2c() {
        const i2c_master_bus_config_t bus_config = {
            .i2c_port = TOUCH_I2C_PORT,
            .sda_io_num = TOUCH_I2C_SDA_PIN,
            .scl_io_num = TOUCH_I2C_SCL_PIN,
            .clk_source = I2C_CLK_SRC_DEFAULT,
            .glitch_ignore_cnt = 7,
            .intr_priority = 0,
            .trans_queue_depth = 0,
            .flags =
                {
                    .enable_internal_pullup = 0,
                },
        };
        ESP_ERROR_CHECK(i2c_new_master_bus(&bus_config, &touch_i2c_bus_));
    }

    void InitializeDisplay() {
        esp_lcd_panel_handle_t panel = nullptr;

        const esp_lcd_rgb_panel_config_t panel_config = {
            .clk_src = LCD_CLK_SRC_DEFAULT,
            .timings =
                {
                    .pclk_hz = 16 * 1000 * 1000,
                    .h_res = DISPLAY_WIDTH,
                    .v_res = DISPLAY_HEIGHT,
                    .hsync_pulse_width = 4,
                    .hsync_back_porch = 8,
                    .hsync_front_porch = 8,
                    .vsync_pulse_width = 4,
                    .vsync_back_porch = 8,
                    .vsync_front_porch = 8,
                    .flags =
                        {
                            .pclk_active_neg = true,
                        },
                },
            .data_width = 16,
            .in_color_format = LCD_COLOR_FMT_RGB565,
            .out_color_format = LCD_COLOR_FMT_RGB565,
            .num_fbs = 2,
            .bounce_buffer_size_px = DISPLAY_WIDTH * 10,
            .dma_burst_size = 64,
            .hsync_gpio_num = DISPLAY_HSYNC_PIN,
            .vsync_gpio_num = DISPLAY_VSYNC_PIN,
            .de_gpio_num = DISPLAY_DE_PIN,
            .pclk_gpio_num = DISPLAY_PCLK_PIN,
            .disp_gpio_num = GPIO_NUM_NC,
            .data_gpio_nums =
                {
                    DISPLAY_DATA_B0_PIN,
                    DISPLAY_DATA_B1_PIN,
                    DISPLAY_DATA_B2_PIN,
                    DISPLAY_DATA_B3_PIN,
                    DISPLAY_DATA_B4_PIN,
                    DISPLAY_DATA_G0_PIN,
                    DISPLAY_DATA_G1_PIN,
                    DISPLAY_DATA_G2_PIN,
                    DISPLAY_DATA_G3_PIN,
                    DISPLAY_DATA_G4_PIN,
                    DISPLAY_DATA_G5_PIN,
                    DISPLAY_DATA_R0_PIN,
                    DISPLAY_DATA_R1_PIN,
                    DISPLAY_DATA_R2_PIN,
                    DISPLAY_DATA_R3_PIN,
                    DISPLAY_DATA_R4_PIN,
                },
            .flags =
                {
                    .fb_in_psram = 1,
                },
        };

        ESP_LOGI(TAG, "Install 800x480 RGB panel");
        ESP_ERROR_CHECK(esp_lcd_new_rgb_panel(&panel_config, &panel));
        ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
        ESP_ERROR_CHECK(esp_lcd_panel_init(panel));

        display_ = new GuitionTouchDisplay(nullptr, panel, DISPLAY_WIDTH, DISPLAY_HEIGHT,
                                           DISPLAY_OFFSET_X, DISPLAY_OFFSET_Y, DISPLAY_MIRROR_X,
                                           DISPLAY_MIRROR_Y, DISPLAY_SWAP_XY);
    }

    void InitializeTouch() {
        const esp_lcd_touch_config_t touch_config = {
            .x_max = DISPLAY_WIDTH - 1,
            .y_max = DISPLAY_HEIGHT - 1,
            .rst_gpio_num = TOUCH_RESET_PIN,
            .int_gpio_num = TOUCH_INTERRUPT_PIN,
            .levels =
                {
                    .reset = 0,
                    .interrupt = 0,
                },
            .flags =
                {
                    .swap_xy = TOUCH_SWAP_XY,
                    .mirror_x = TOUCH_MIRROR_X,
                    .mirror_y = TOUCH_MIRROR_Y,
                },
        };

        esp_lcd_panel_io_handle_t touch_io = nullptr;
        esp_lcd_panel_io_i2c_config_t touch_io_config = {};
        touch_io_config.scl_speed_hz = 400 * 1000;
        touch_io_config.dev_addr = ESP_LCD_TOUCH_IO_I2C_GT911_ADDRESS;
        touch_io_config.control_phase_bytes = 1;
        touch_io_config.dc_bit_offset = 0;
        touch_io_config.lcd_cmd_bits = 16;
        touch_io_config.flags.disable_control_phase = 1;

        ESP_LOGI(TAG, "Initialize GT911 touch controller");
        ESP_ERROR_CHECK(esp_lcd_new_panel_io_i2c(touch_i2c_bus_, &touch_io_config, &touch_io));

        esp_lcd_touch_handle_t touch = nullptr;
        ESP_ERROR_CHECK(esp_lcd_touch_new_i2c_gt911(touch_io, &touch_config, &touch));

        const lvgl_port_touch_cfg_t lvgl_touch_config = {
            .disp = lv_display_get_default(),
            .handle = touch,
        };
        lvgl_port_add_touch(&lvgl_touch_config);
    }

public:
    GuitionJC8048W550C() {
        InitializeTouchI2c();
        InitializeDisplay();
        InitializeTouch();
        GetBacklight()->SetBrightness(100);
    }

    AudioCodec* GetAudioCodec() override {
        static NoAudioCodecSimplex audio_codec(AUDIO_INPUT_SAMPLE_RATE, AUDIO_OUTPUT_SAMPLE_RATE,
                                               AUDIO_I2S_SPK_GPIO_BCLK, AUDIO_I2S_SPK_GPIO_LRCK,
                                               AUDIO_I2S_SPK_GPIO_DOUT, AUDIO_I2S_MIC_GPIO_SCK,
                                               AUDIO_I2S_MIC_GPIO_WS, AUDIO_I2S_MIC_GPIO_DIN);
        return &audio_codec;
    }

    Display* GetDisplay() override { return display_; }

    Backlight* GetBacklight() override {
        static PwmBacklight backlight(DISPLAY_BACKLIGHT_PIN, DISPLAY_BACKLIGHT_OUTPUT_INVERT);
        return &backlight;
    }
};

DECLARE_BOARD(GuitionJC8048W550C);
