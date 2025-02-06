# virtual-keyboard-mouse

> This project is based on mediapipe and openCV, and all you need is a printed paper keybord, a camera module and a Raspberry Pi (mine is Raspberry Pi 4i)
> At last your system should be able to control by typing on a piece of paper with your hand.


### Basic Ideas
- *frame transform*
  > The initial site from the camera is with color and nonstandard, so first a binaryzation needed. Also, we need a rotation matrix and a mapping matrix.
  > After this step, we get a standard keyboard picture

- *position location*
  > Using the standard picture, locat every key by finding its corresponding coordinates in the lower left and upper right corners.
  > Create a new class for those keys.

- *click detection*
  > Using mediapipe, we can locate each of our finger(in this proj, due to the hashrate of Raspberry Pi, only the index finger was included).
  > Use the width coordinates as the depth coordinates(they act similar in 2D frame), set a thereshold value for detecting the speed of falling of your finger.
  > Add a low pass filter in case of shaking.

### *Something more*
- *buzzer mode*
  > To make more fun, this keyboard is able to voice a sound using a buzzer. By pressing "shift", user can switch between buzzer mode and keyboard mode.
- *virtual mouse*
  > The virtual mouse function is also based on mediapipe and openCV
