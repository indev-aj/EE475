/*
   Written by: Amrin Jaffni
   ESP32 receiving serial command from Jetson Nano

   Code for EE475

   Commands:
   [Laser]
    - <L1ON>
    - <L1OF>
    - <L2ON>
    - <L2OF>
*/

int r = 2;
int b = 4;

const byte numChars = 32;
char receivedChars[numChars];

char startMarker = '<';
char endMarker = '>';

boolean newData = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(r, OUTPUT);
  pinMode(b, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  recvWithStartEndMarkers();
  showNewData();
}

void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      }
      else {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }

    else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

void showNewData() {
  if (newData == true) {
    Serial.print("This just in ... ");
    Serial.println(receivedChars);
    newData = false;

    if(strcmp(receivedChars,"L1ON") == 0) {
      digitalWrite(r, HIGH);
    } else if (strcmp(receivedChars,"L1OF") == 0) {
      digitalWrite(r, LOW);
    }

    if(strcmp(receivedChars,"L2ON") == 0) {
      digitalWrite(b, HIGH);
    } else if (strcmp(receivedChars,"L2OF") == 0) {
      digitalWrite(b, LOW);
    }
  }
}
