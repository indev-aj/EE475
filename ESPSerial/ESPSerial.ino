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
int btn = 23; // interrupt button

int stageDir = 18; // controls direction of stage
int stageMove = 19; // controls how many steps does stage move

const byte numChars = 32;
char receivedChars[numChars];

char tempChars[numChars];
char instructions[numChars] = {0};

char startMarker = '<';
char endMarker = '>';

boolean newData = false;
volatile bool interrupted = false;

void IRAM_ATTR isr()
{
  interrupted = true;
  digitalWrite(r, LOW);
  digitalWrite(b, LOW);

  digitalWrite(stageDir, LOW);
  digitalWrite(stageMove, LOW);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(r, OUTPUT);
  pinMode(b, OUTPUT);

  pinMode(stageDir, OUTPUT);
  pinMode(stageMove, OUTPUT);

  pinMode(btn, INPUT_PULLUP);
  attachInterrupt(btn, isr, RISING);


  digitalWrite(b, HIGH);
  digitalWrite(r, HIGH);
  digitalWrite(stageDir, HIGH);
  digitalWrite(stageMove, HIGH);
  delay(500);
  digitalWrite(b, LOW);
  digitalWrite(r, LOW);
  digitalWrite(stageDir, LOW);
  digitalWrite(stageMove, LOW);
  delay(500);
}

char* sep;

void loop() {
  // put your main code here, to run repeatedly:
  interrupted = false;

  recvWithStartEndMarkers();
  if (newData) {
    strcpy(tempChars, receivedChars);
    sep = strtok(tempChars, ",");
    while (sep != NULL) {
      showNewData(sep);
      Serial.println(sep);
      sep = strtok(NULL, ",");
    }

  }

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

void showNewData(char* instruction) {

  char prefix[3];

  Serial.print("This just in ... ");
  Serial.println(instruction);
  newData = false;

  // Laser controls
  if (strcmp(instruction, "L1ON") == 0) {
    digitalWrite(r, HIGH);
  } else if (strcmp(instruction, "L1OF") == 0) {
    digitalWrite(r, LOW);
  }

  if (strcmp(instruction, "L2ON") == 0) {
    digitalWrite(b, HIGH);
  } else if (strcmp(instruction, "L2OF") == 0) {
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

  memcpy(prefix, instruction, 2);
  prefix[2] = '\0';
  char dir = instruction[2];

  Serial.println(prefix);
  Serial.println(dir);

  if (strcmp(prefix, "S1") == 0) {
    switch (dir) {
      case 'P':
        steps = getStep(instruction);
        Serial.print("Moving Positive: ");
        Serial.print(steps);

        digitalWrite(stageDir, HIGH);
        for (int i = 0; i < steps; i++) {
          if (interrupted)
            break;
          digitalWrite(stageMove, HIGH);
          delay(500);
          digitalWrite(stageMove, LOW);
          delay(500);
        }
        break;
      case 'N':
        steps = getStep(instruction);
        Serial.print("Moving Negative: ");
        Serial.print(steps);

        digitalWrite(stageDir, LOW);
        for (int i = 0; i < steps; i++) {
          if (interrupted)
            break;
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

int getStep(char* instruction) {
  for (int i = 0; i <= 4; i++) {
    nums[i] = instruction[i + 3];
  }

  return atoi(nums);
}
