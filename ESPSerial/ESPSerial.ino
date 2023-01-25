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

int stageDir = 18;
int stageMove = 19;

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

  pinMode(stageDir, OUTPUT);
  pinMode(stageMove, OUTPUT);
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

int steps;
char nums[4];
void showNewData() {

  char prefix[2];

  if (newData == true) {
    Serial.print("This just in ... ");
    Serial.println(receivedChars);
    newData = false;

    // Laser controls
    if (strcmp(receivedChars, "L1ON") == 0) {
      digitalWrite(r, HIGH);
    } else if (strcmp(receivedChars, "L1OF") == 0) {
      digitalWrite(r, LOW);
    }

    if (strcmp(receivedChars, "L2ON") == 0) {
      digitalWrite(b, HIGH);
    } else if (strcmp(receivedChars, "L2OF") == 0) {
      digitalWrite(b, LOW);
    }

    // Stage controls
    /* Steps:
        1. Check which stage to command
        2. Check which direction
        3. Get steps amount

        eg. S1P1000 - Stage 1, positive direction, 1000 steps
        eg. S2N1000 - Stage 2, negative direction, 1000 steps
    */

    memcpy(prefix, receivedChars, 2);
    char dir = receivedChars[2];

    Serial.println(prefix);
    Serial.println(dir);

    if (strcmp(prefix, "S1") == 0) {
      switch (dir) {
        case 'P':
          steps = getStep();
          Serial.print("Moving Positive: ");
          Serial.print(steps);
          
          digitalWrite(stageDir, HIGH);
          for(int i=0;i<steps;i++) {
            digitalWrite(stageMove, HIGH);
            delay(500);
            digitalWrite(stageMove, LOW);
            delay(500);
          }
          break;
        case 'N':
          steps = getStep();
          Serial.print("Moving Negative: ");
          Serial.print(steps);

          digitalWrite(stageDir, LOW);
          for(int i=0;i<steps;i++) {
            digitalWrite(stageMove, HIGH);
            delay(500);
            digitalWrite(stageMove, LOW);
            delay(500);
          }
          break;
        default:
          Serial.println("Nothing goes here!");
      }
    }
  }
}

int getStep() {
  for (int i = 0; i <= 4; i++) {
    nums[i] = receivedChars[i + 1];
  }

  return atoi(nums);
}
