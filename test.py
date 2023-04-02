from gpiozero import Angulaservo

servo = AngularServo(18, min_pulse_width=0.0006, max_pulse=0.0023)

servo.angle = 0
