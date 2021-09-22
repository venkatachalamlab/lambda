int InputPin = 23;
int OutputPin = 14;

elapsedMicros t;
unsigned int delta_t = 0;
unsigned int init_t = 0;
bool period_init = true;

bool value_now = false;
bool value_old = false;

void setup() {
    pinMode(InputPin, INPUT);
    pinMode(OutputPin, OUTPUT);
}

void loop() {
    value_now = digitalRead(InputPin);
    if (value_now != value_old && delta_t < 250){
        digitalWrite(OutputPin, HIGH);
        if (period_init){
            init_t = t;
            period_init = false;
        }
        delta_t = t - init_t;
    }
    else if (value_now != value_old && delta_t < 2500){
        digitalWrite(OutputPin, LOW);
        delta_t = t - init_t;
    }
    else if (value_now != value_old && delta_t < 2750){
        digitalWrite(OutputPin, HIGH);
        delta_t = t - init_t;
    }
    else{
        digitalWrite(OutputPin, LOW);
        value_old = value_now;
        period_init = true;
        delta_t = 0;
        t = 0;
    }
}