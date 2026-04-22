#include <WiFi.h>
#include <HTTPClient.h>
#include <driver/i2s.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

#define SDA_PIN 8
#define SCL_PIN 9

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

#define BUTTON_PIN 42

// I2S pins
#define I2S_WS 5
#define I2S_SD 6
#define I2S_SCK 4
#define I2S_DOUT 7

//onst char* ssid = "TurkTelekom_ZTE3SY";
//const char* password = "f7KzePzEK7dP";

const char* ssid = "ModemName";
const char* password = "Password";

const char* server = "http://192.168.1.110:5000/audio";

#define SAMPLE_RATE 16000
#define RECORD_TIME 4

#define BUFFER_SIZE (SAMPLE_RATE * RECORD_TIME)

int16_t audio_buffer[BUFFER_SIZE];

void oled(String text)
{
  display.clearDisplay();
  display.setCursor(0,0);
  display.println(text);
  display.display();
}

void setup_i2s_mic()
{
  i2s_config_t config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .dma_buf_count = 8,
    .dma_buf_len = 64
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = -1,
    .data_in_num = I2S_SD
  };

  i2s_driver_install(I2S_NUM_0, &config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
}

void setup_i2s_speaker()
{
  i2s_config_t config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .dma_buf_count = 8,
    .dma_buf_len = 64
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_DOUT,
    .data_in_num = -1
  };

  i2s_driver_install(I2S_NUM_1, &config, 0, NULL);
  i2s_set_pin(I2S_NUM_1, &pin_config);
}

void record_audio()
{
  size_t bytes_read;

  // ilk buffer'ı çöpe at (gürültü temizleme)
  int16_t dummy[256];
  i2s_read(I2S_NUM_0, dummy, sizeof(dummy), &bytes_read, portMAX_DELAY);

  // gerçek kayıt
  for(int i=0;i<BUFFER_SIZE;i+=256)
  {
    i2s_read(I2S_NUM_0, &audio_buffer[i], 256*sizeof(int16_t), &bytes_read, portMAX_DELAY);
  }
}

void send_audio()
{
  HTTPClient http;

  http.begin(server);
  http.addHeader("Content-Type","application/octet-stream");

  oled("Sending to AI...");

  int httpResponseCode = http.POST((uint8_t*)audio_buffer, BUFFER_SIZE*2);

  if(httpResponseCode > 0)
  {
    oled("Playing reply...");

    WiFiClient * stream = http.getStreamPtr();

    while(stream->available() == 0)
    {
      delay(1);
    }

    // WAV header skip
    uint8_t wav_header[44];
    stream->readBytes(wav_header,44);

    size_t bytes_read;
    int16_t play_buffer[256];

    while(stream->available())
    {
      bytes_read = stream->readBytes((uint8_t*)play_buffer, sizeof(play_buffer));

      size_t bytes_written;
      i2s_write(I2S_NUM_1, play_buffer, bytes_read, &bytes_written, portMAX_DELAY);
    }
  }

  http.end();
}

void setup()
{
  Serial.begin(115200);

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  Wire.begin(SDA_PIN,SCL_PIN);

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  oled("Voice Node Boot");

  WiFi.begin(ssid,password);

  oled("Connecting WiFi...");

  while(WiFi.status()!=WL_CONNECTED)
  {
    delay(500);
  }

  oled("WiFi OK\nIP:\n"+WiFi.localIP().toString());

  setup_i2s_mic();
  delay(1000);
  setup_i2s_speaker();
}

void loop()
{
  if(digitalRead(BUTTON_PIN)==LOW)
  {
    oled("Recording 4 sec...");

    record_audio();

    send_audio();

    delay(1500);

    oled("Ready");
  }
}