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

int laser1 = 2;
int laser2 = 4;
int btn = 21; // interrupt button

int stage1Dir = 18; // controls direction of stage
int stage1Move = 19; // controls how many steps does stage move
int stage2Dir = 22; // controls direction of stage
int stage2Move = 23; // controls how many steps does stage move
int stage3Dir = 12; // controls direction of stage
int stage3Move = 13; // controls how many steps does stage move

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
  digitalWrite(laser1, LOW);
  digitalWrite(laser2, LOW);

  digitalWrite(stage1Dir, LOW);
  digitalWrite(stage1Move, LOW);
  digitalWrite(stage2Dir, LOW);
  digitalWrite(stage2Move, LOW);
  digitalWrite(stage3Dir, LOW);
  digitalWrite(stage3Move, LOW);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(laser1, OUTPUT);
  pinMode(laser2, OUTPUT);

  pinMode(stage1Dir, OUTPUT);
  pinMode(stage1Move, OUTPUT);
  pinMode(stage2Dir, OUTPUT);
  pinMode(stage2Move, OUTPUT);
  pinMode(stage3Dir, OUTPUT);
  pinMode(stage3Move, OUTPUT);

  pinMode(btn, INPUT_PULLUP);
  attachInterrupt(btn, isr, RISING);


  digitalWrite(laser2, HIGH);
  digitalWrite(laser1, HIGH);
  digitalWrite(stage1Dir, HIGH);
  digitalWrite(stage1Move, HIGH);
  digitalWrite(stage2Dir, HIGH);
  digitalWrite(stage2Move, HIGH);
  digitalWrite(stage3Dir, HIGH);
  digitalWrite(stage3Move, HIGH);
  delay(500);
  digitalWrite(laser2, LOW);
  digitalWrite(laser1, LOW);
  digitalWrite(stage1Dir, LOW);
  digitalWrite(stage1Move, LOW);
  digitalWrite(stage2Dir, LOW);
  digitalWrite(stage2Move, LOW);
  digitalWrite(stage3Dir, LOW);
  digitalWrite(stage3Move, LOW);
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
    digitalWrite(laser1, HIGH);
  } else if (strcmp(instruction, "L1OF") == 0) {
    digitalWrite(laser1, LOW);
  }

  if (strcmp(instruction, "L2ON") == 0) {
    digitalWrite(laser2, HIGH);
  } else if (strcmp(instruction, "L2OF") == 0) {
    digitalWrite(laser2, LOW);
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

        digitalWrite(stage1Dir, HIGH);
        for (int i = 0; i < steps; i++) {
          if (interrupted)
            break;
          digitalWrite(stage1Move, HIGH);
          delay(10);
          digitalWrite(stage1Move, LOW);
          delay(10);
        }
        break;
      case 'N':
        steps = getStep(instruction);
        Serial.print("Moving Negative: ");
        Serial.print(steps);

        digitalWrite(stage1Dir, LOW);
        for (int i = 0; i < steps; i++) {
          if (interrupted)
            break;
          digitalWrite(stage1Move, HIGH);
          delay(10);
          digitalWrite(stage1Move, LOW);
          delay(10);
        }
        break;
      default:
        Serial.println("Nothing goes here!");
    }
  }

  if (strcmp(prefix, "S2") == 0) {
    switch (dir) {
      case 'P':
        steps = getStep(instruction);
        Serial.print("Moving Positive: ");
        Serial.print(steps);

        digitalWrite(stage2Dir, HIGH);
        for (int i = 0; i < steps; i++) {
          if (interrupted)
            break;
          digitalWrite(stage2Move, HIGH);
          delay(10);
          digitalWrite(stage2Move, LOW);
          delay(10);
        }
        break;
      case 'N':
        steps = getStep(instruction);
        Serial.print("Moving Negative: ");
        Serial.print(steps);

        digitalWrite(stage2Dir, LOW);
        for (int i = 0; i < steps; i++) {
          if (interrupted)
            break;
          digitalWrite(stage2Move, HIGH);
          delay(10);
          digitalWrite(stage2Move, LOW);
          delay(10);
        }
        break;
      default:
        Serial.println("Nothing goes here!");
    }
  }

  if (strcmp(prefix, "S3") == 0) {
    switch (dir) {
      case 'P':
        steps = getStep(instruction);
        Serial.print("Moving Positive: ");
        Serial.print(steps);

        digitalWrite(stage3Dir, HIGH);
        for (int i = 0; i < steps; i++) {
          if (interrupted)
            break;
          digitalWrite(stage3Move, HIGH);
          delay(10);
          digitalWrite(stage3Move, LOW);
          delay(10);
        }
        break;
      case 'N':
        steps = getStep(instruction);
        Serial.print("Moving Negative: ");
        Serial.print(steps);

        digitalWrite(stage3Dir, LOW);
        for (int i = 0; i < steps; i++) {
          if (interrupted)
            break;
          digitalWrite(stage3Move, HIGH);
          delay(10);
          digitalWrite(stage3Move, LOW);
          delay(10);
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
