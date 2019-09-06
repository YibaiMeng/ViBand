#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "driver/i2c.h"
#include "esp_err.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/portmacro.h"
#include "freertos/task.h"
#include "sdkconfig.h"

#include "MPU.hpp"
#include "mpu/math.hpp"
#include "mpu/types.hpp"

/* Bus configuration */

// This MACROS are defined in "skdconfig.h" and set through 'menuconfig'.
// Can use to check which protocol has been selected.

#include "I2Cbus.hpp"
static I2C_t& i2c                     = i2c0;  // i2c0 or i2c1
static constexpr gpio_num_t SDA       = GPIO_NUM_21;
static constexpr gpio_num_t SCL       = GPIO_NUM_22;
static constexpr uint32_t CLOCK_SPEED = 400000;  // 400 KHz

/* MPU configuration */
static constexpr uint16_t kSampleRate      = 1000;  // Hz
static constexpr mpud::accel_fs_t kAccelFS = mpud::ACCEL_FS_4G;


static const char* TAG = "MPU acc";

static void mpuTask(void*);

// Main
extern "C" void app_main()
{
    i2c.begin(SDA, SCL, CLOCK_SPEED);
    // Create a task to setup mpu and read sensor data
    xTaskCreate(mpuTask, "mpuTask", 4 * 1024, nullptr, 6, nullptr);
}

/* Tasks */

static MPU_t MPU;
int16_t accel[4];
//const char sync_byte[] = {0x0d, 0x0d, 0x0a, 0x0a,0x0a, 0x0a, 0x0d};
static void mpuTask(void*) {
    // Let MPU know which bus and address to use
    MPU.setBus(i2c);
    MPU.setAddr(mpud::MPU_I2CADDRESS_AD0_LOW);

    // Verify connection
    while (esp_err_t err = MPU.testConnection()) {
        ESP_LOGE(TAG, "Failed to connect to the MPU, error=%#X", err);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
    ESP_LOGI(TAG, "MPU connection successful!");

    // Initialize
    ESP_ERROR_CHECK(MPU.initialize());

    // Self-Test
    mpud::selftest_t retSelfTest;
    while (esp_err_t err = MPU.selfTest(&retSelfTest)) {
        ESP_LOGE(TAG, "Failed to perform MPU Self-Test, error=%#X", err);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
    ESP_LOGI(TAG, "MPU Self-Test result: Accel=%s",  //
             (retSelfTest & mpud::SELF_TEST_ACCEL_FAIL ? "FAIL" : "OK"));

    // Calibrate
    mpud::raw_axes_t accelBias, gyroBias;
    ESP_ERROR_CHECK(MPU.computeOffsets(&accelBias, &gyroBias));
    ESP_ERROR_CHECK(MPU.setAccelOffset(accelBias));

    // Configure
    ESP_ERROR_CHECK(MPU.setAccelFullScale(kAccelFS));
    ESP_ERROR_CHECK(MPU.setSampleRate(kSampleRate));

    // Setup FIFO
    ESP_ERROR_CHECK(MPU.setFIFOConfig(mpud::FIFO_CFG_ACCEL));
    ESP_ERROR_CHECK(MPU.setFIFOEnabled(true));
    constexpr uint16_t kFIFOPacketSize = 6;

    // Ready to start reading
    ESP_ERROR_CHECK(MPU.resetFIFO());  // start clean
    
    // esp_log_level_set("*", ESP_LOG_NONE); 
    // Reading Loop
    //int count = 0;
    while (true) {
        // Check FIFO count
        uint16_t fifocount = MPU.getFIFOCount();
        if (fifocount == 0) {
            continue;
        }
        if (esp_err_t err = MPU.lastError()) {
            ESP_LOGE(TAG, "Error reading fifo count, %#X", err);
            MPU.resetFIFO();
            continue;
        }
        if (fifocount > kFIFOPacketSize * 2) {
            if (!(fifocount % kFIFOPacketSize)) {
                ESP_LOGE(TAG, "Sample Rate too high!, not keeping up the pace!, count: %d", fifocount);
            }
            else {
                ESP_LOGE(TAG, "FIFO Count misaligned! Expected: %d, Actual: %d", kFIFOPacketSize, fifocount);
            }
            MPU.resetFIFO();
            continue;
        }
        // Burst read data from FIFO
        uint8_t buffer[kFIFOPacketSize];
        if (esp_err_t err = MPU.readFIFO(kFIFOPacketSize, buffer)) {
            ESP_LOGE(TAG, "Error reading sensor data, %#X", err);
            MPU.resetFIFO();
            continue;
        }
        accel[0] = buffer[0] << 8 | buffer[1];
        accel[1] = buffer[2] << 8 | buffer[3];
        accel[2] = buffer[4] << 8 | buffer[5];
        accel[3] = 0xffff;
        //fwrite(sync_byte, 1, sizeof(sync_byte), stdout);
        fwrite((char*)&accel, 1, sizeof(accel), stdout); 
        //printf("X: %f \t Y: %f \t Z: %f \n", accel[0] / 8192.0, accel[1] / 8192.0, accel[2] / 8192.0);
    }
    vTaskDelete(nullptr);
}
