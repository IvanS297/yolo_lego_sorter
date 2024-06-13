#define MOTOR_MOSFET_PIN 10
#define BUZZ_PIN 13
#define PHOTO_PIN A0

#define STEPPER_SORTER_IN1 2
#define STEPPER_SORTER_IN2 3
#define STEPPER_SORTER_IN3 4
#define STEPPER_SORTER_IN4 5

#define STEPPER_MOVER_IN1 6
#define STEPPER_MOVER_IN2 7
#define STEPPER_MOVER_IN3 8
#define STEPPER_MOVER_IN4 9

#define STEPPER_SORTER_RUN_MODE FOLLOW_POS
#define STEPPER_MOVER_RUN_MODE FOLLOW_POS

#define STEPS_PER_TURNOVER 2048
#define DRIVER_TYPE STEPPER4WIRE

#define SERIAL_SPEED 9600
#define SERIAL_TERMINATOR ';'
#define SERIAL_SEPARATOR ','
#define SERIAL_TIMEOUT 5
#define SERIAL_BUFFER 10

#define START_DELAY_SEC 6
#define DETECT_SIGNAL 936
#define DETECT_BUZZ_SIGNAL 3000
#define DETECT_DELAY 2000
#define DETECT_MESS "detected"

uint32_t tmr = 0;
int degs[7] = {0, 45, 90, 135, 180, 225, 270,};
String names[7] = {"brick", "plate", "technic_pin_connector", "technic_pin", "vehicle_mudguard", "gear", "(no_detections)",};

#include <GyverStepper.h>
GStepper<DRIVER_TYPE> stepper_sorter(STEPS_PER_TURNOVER, STEPPER_SORTER_IN4, STEPPER_SORTER_IN2, STEPPER_SORTER_IN3, STEPPER_SORTER_IN1);
GStepper<DRIVER_TYPE> stepper_mover(STEPS_PER_TURNOVER, STEPPER_MOVER_IN4, STEPPER_MOVER_IN2, STEPPER_MOVER_IN3, STEPPER_MOVER_IN1);

#include <GyverOLED.h>
GyverOLED<SSD1306_128x64, OLED_NO_BUFFER> oled;

#include "Parser.h" // Библиотека для удобного парсинга.
#include "AsyncStream.h"  // Асинхронное чтение Serial (его просто удобнее использовать с Parser.h).
AsyncStream<50> serial(&Serial, SERIAL_TERMINATOR); // Создание асинхронного чтения Serial на 50 байт.

void setup() {
  Serial.begin(SERIAL_SPEED);
  Serial.setTimeout(SERIAL_TIMEOUT);

  pinMode(PHOTO_PIN, INPUT);
  pinMode(MOTOR_MOSFET_PIN, OUTPUT);
  pinMode(BUZZ_PIN, OUTPUT);

  stepper_sorter.setRunMode(STEPPER_SORTER_RUN_MODE);
  stepper_sorter.setTargetDeg(0);

  delay(START_DELAY_SEC);
  digitalWrite(MOTOR_MOSFET_PIN, HIGH);

  oled.init();
  oled.clear();
  oled.setScale(1);
  oled.home();
}

void loop() {
  stepper_sorter.tick();
  stepper_mover.tick();

  if (analogRead(PHOTO_PIN) < DETECT_SIGNAL) {
    delay(DETECT_DELAY);
    digitalWrite(MOTOR_MOSFET_PIN, LOW);
    send_message(0, DETECT_MESS);
  }
  parsing();
}

void parsing() { // Функция парсинга данных из COM порта
  if (serial.available()) {
    Parser data(serial.buf, SERIAL_SEPARATOR);
    int ints[SERIAL_BUFFER];
    data.parseInts(ints);

    switch (ints[0]) {
      case 0:
        tone(BUZZ_PIN, DETECT_BUZZ_SIGNAL);
        delay(ints[1]);
        noTone(BUZZ_PIN);
        stepper_sorter.setCurrentDeg(0);
        stepper_sorter.setTargetDeg(ints[2]);
        break;
      case 1:
        stepper_mover.setCurrentDeg(0);
        stepper_mover.setTargetDeg(ints[1]);
        break;
      case 2:
        digitalWrite(MOTOR_MOSFET_PIN, ints[1]);
        break;
      case 3:
        oled.clear();
        oled.setCursor(0, 0);
        oled.print(names[degs[ints[1]]]);
        oled.setCursor(0, 1);
        oled.print("Rotate on " + (String)ints[2] + " degrees");
        break;
    }
  }
}

void send_message(int key, String message_data) {
  String message = key + (String)SERIAL_SEPARATOR + message_data;
  Serial.println(message);
}
