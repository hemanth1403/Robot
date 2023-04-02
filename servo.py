from gpiozero import AngularServo

servo = AngularServo(18, min_pulse_width=0.0006, max_pulse_width=0.0023)

servo.angle = 0
servo.angle = -90	
