#define NUM_LED 6  //sets the maximum numbers of LEDs
#define MAX 150     //maximum posible reading. TWEAK THIS VALUE!!

//EMG1
int reading[10];
int finalReading;

//EMG2
int reading2[10];
int finalReading2;

byte litLeds = 0;
byte multiplier = 1;
byte leds[] = {8, 9, 10, 11, 12, 13};

void setup(){
  Serial.begin(9600); //begin serial communications
  for(int i = 0; i < NUM_LED; i++){ //initialize LEDs as outputs
    pinMode(leds[i], OUTPUT);
  }
}

void loop(){
  //EMG1, A0
  for(int i = 0; i < 10; i++){    //take ten readings in ~0.02 seconds
    reading[i] = analogRead(A0) * multiplier;
    delay(2);
  }
  for(int i = 0; i < 10; i++){   //average the ten readings
    finalReading += reading[i];
  }
  finalReading /= 10;
  
  //EMG2, A1
  for(int i = 0; i < 10; i++){    //take ten readings in ~0.02 seconds
    reading2[i] = analogRead(A1) * multiplier;
    delay(2);
  }
  for(int i = 0; i < 10; i++){   //average the ten readings
    finalReading2 += reading2[i];
  }
  finalReading2 /= 10;
  
  for(int j = 0; j < NUM_LED; j++){  //write all LEDs low
    digitalWrite(leds[j], LOW);
  }
  Serial.print(finalReading);
  Serial.print("\t");
  Serial.print(finalReading2);
  Serial.print("\t");
  finalReading = constrain(finalReading, 0, MAX);
  finalReading2 = constrain(finalReading2, 0, MAX);
  litLeds = map(finalReading, 0, MAX, 0, NUM_LED);
  Serial.println(litLeds);
  for(int k = 0; k < litLeds; k++){
    digitalWrite(leds[k], HIGH);
  }
  //for serial debugging, uncomment the next two lines.
  //Serial.println(finalReading);
  //delay(100);
}
    
