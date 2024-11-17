from time import sleep, time
import os
from gpiozero import Motor, Servo, DistanceSensor, LineSensor, LED, PWMOutputDevice
from gtts import gTTS
import speech_recognition as sr
import curses
import datetime
import pytz
import webbrowser

# Set up motors
motor_left = Motor(forward=19, backward=13)
motor_right = Motor(forward=26, backward=20)

# Set up sensors
front_right_sensor = DistanceSensor(echo=14, trigger=15, max_distance=2)
front_left_sensor = DistanceSensor(echo=4, trigger=22, max_distance=2)
back_center_sensor = DistanceSensor(echo=5, trigger=6, max_distance=2)
front_servo_sensor = DistanceSensor(echo=24, trigger=23, max_distance=2)

# Set up servo
servo = Servo(17, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

line_sensor = LineSensor(25)
led = LED(16)

# Set up motor enable pins (ENA and ENB) for 50% speed
ena = PWMOutputDevice(18)
enb = PWMOutputDevice(12)



# Global variable to track robot state
current_command = None

# Function to make the robot speak using gTTS
def speak(text):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save("speech.mp3")
    os.system("mpg321 speech.mp3")
    os.remove("speech.mp3")

def run_for_duration(func, duration):
    start_time = time()
    while time() - start_time < duration:
        func()
        sleep(0.1)
    stop_robot()
    recognize_voice_command()

led.off()
   
def scan_for_duration(func, duration):
    start_time = time()
    while time() - start_time < duration:
        func()
        sleep(0.1)
    stop_robot()
    
def dance_for_duration(func, duration):
    start_time = time()
    while time() - start_time < duration:
        func()
        sleep(0.1)
    stop_robot()
   
# Function to recognize voice commands using SpeechRecognition
def recognize_voice_command():
    global current_command
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Listening for voice commands...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Command received: {command}")
        current_command = command  # Store the command to check sensor conditions
        handle_voice_command(command)
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        recognize_voice_command()
        
def play_song(song_name):
    music_folder = "/home/hp/Documents/music"  # Change this path to where your music folder is located
    song_path = os.path.join(music_folder, f"{song_name}.mp3")

    if os.path.exists(song_path):
        print(f"Playing {song_name}...")
        os.system(f'mpg321 "{song_path}"')  # Play the song
        recognize_voice_command()
    else:
        speak(f"Sorry, I couldn't find a song named {song_name}.")
        recognize_voice_command()

def led_on():
    led.on()
    recognize_voice_command()

def led_off():
    led.off()
    recognize_voice_command()

def handle_voice_command(command):
    if ("forward" in command or "forword" in command or "four word" in command or
        "start" in command or "go" in command or "swaraj" in command or "mumbottupo" in command or "mumbai to goa" in command or "8:30" in command):
        move_forward()
    elif ("backward" in command or "bad word" in command or "back word" in command or
          "backword" in command or "bhagwat" in command or "bakwas" in command):
        move_backward()
    elif ("left" in command or "luft" in command or "go left" in command or "turn left" in command):
        run_for_duration(turn_left, 1)
    elif ("right" in command or "turn right" in command or "go right" in command or
          "turn rite" in command or "ten right" in command or "pen drive" in command):
        run_for_duration(turn_right, 1)
    elif "stop" in command:
        stop_robot()
    elif ("follow line" in command or "follow mine" in command):
        follow_line()
    elif ("sing english song" in command or "play english song" in command or "english song" in command):
        play_english_song()
    elif ("sing malayalam song" in command or "play malayalam song" in command or "play malayalam" in command):
        play_malayalam_song()
    elif ("turn on light" in command or "on light"  in command):
        led_on()
    elif ("turn off light" in command or "off light" in command or "of light" in command or "off" in command or "of" in command):
        led_off()
    elif "remote control" in command:
        curses.wrapper(remote_control)
    elif "play" in command:  # Handle the "play <song_name>" command
        song_name = command.split("play", 1)[1].strip()  # Extract song name after 'play'
        if song_name:
            play_song(song_name)  # Call the play_song function
        else:
            speak("Please specify a song name after 'play'.")
    elif "time" in command:
        speak_time()
    elif "new" in command:
        news()
    elif ("weather" in command or "whether" in command):
        weather()
    elif "power down" in command:
        power_down()
    elif "zero degrees" in command:
        servo.value = -1
    elif "90 degrees" in command:
        servo.value = 0
    elif ("180 degrees" in command or "80 degrees" in command):
        servo.value = 1
    else:
        recognize_voice_command()

def power_down():
    os.system('sudo shutdown now')
        
def weather():
    speak("about 29 degree celsius in ernakulam now. expecting rain by 8 pm.")
    recognize_voice_command()
        
def news():
    webbrowser.open("https://www.youtube.com/watch?v=1wECsnGZcfc&autoplay=1")

def follow_line():
    while True:
        if line_sensor.is_active:  # Line detected (black surface)
            print("Line detected, turning left.")
            turn_left()
        else:  # No line detected (white surface)
            print("No line detected, turning right.")
            turn_right()

def play_english_song():
    print("Playing English song...")
    dance()
    song_path = "/home/hp/Documents/english_song.mp3"  # Change this path to where your song is located
    os.system(f"mpg321 {song_path}")
    
def disconnect_servo():
    servo.value = 0
    sleep(0.1)
    servo.detach()

disconnect_servo()


def play_malayalam_song():
    print("Playing Malayalam song...")
    song_path = "/home/hp/Documents/malayalam_song.mp3"  # Change this path to where your song is located
    os.system(f"mpg321 {song_path}")
    servo.value = -1
    dance_for_duration(turn_left, 1)
    sleep(0.1)
    servo.value = 1
    sleep(0.2)
    dance_for_duration(turn_right, 2)
    sleep(0.5)
    servo.value = 0
    sleep(0.2)
    dance_for_duration(turn_left, 4)
    sleep(0.5)
    dance_for_duration(move_forward, 1)
    sleep(0.2)
    dance_for_duration(move_backward, 1)
    sleep(0.3)
    dance_for_duration(turn_right, 4)
    sleep(0.2)
    servo.value = -0.5
    sleep(0.1)
    dance_for_duration(turn_left, 0.5)
    sleep(0.1)
    servo.value = 0
    sleep(0.2)
    dance_for_duration(move_forward, 1)
    sleep(0.1)
    servo.value = 0.5
    sleep(0.1)
    dance_for_duration(turn_right, 1)
    sleep(0.1)
    servo.value = 0
    sleep(0.2)
    dance_for_duration(move_backward, 1)
    sleep(0.1)
    dance_for_duration(turn_left, 0.5)
    sleep(0.1)
    stop_robot()
    sleep(1)

# Motor control functions
def move_forward():
    print("Moving forward.")
    ena.value = 0.40  # Set to 70% speed
    enb.value = 0.40
    motor_left.forward()
    motor_right.forward()

def move_backward():
    print("Moving backward.")
    ena.value = 0.45  # Set to 70% speed
    enb.value = 0.45
    motor_left.backward()
    motor_right.backward()

def turn_left():
    print("Turning left.")
    ena.value = 1  # Set to 70% speed
    enb.value = 1
    motor_left.backward()
    motor_right.forward()

def turn_right():
    print("Turning right.")
    ena.value = 1  # Set to 70% speed
    enb.value = 1
    motor_left.forward()
    motor_right.backward()

def stop_robot():
    print("Stopping robot.")
    motor_left.stop()
    motor_right.stop()

def scan_with_ultrasonic():
    stop_robot()
    print("Starting scan with ultrasonic...")

    positions = [-1, -0.5, 0, 0.5, 1]
    for pos in positions:
        servo.value = pos
        sleep(1)
        distance = front_servo_sensor.distance * 100
        print(f"Servo at position {pos}, Distance: {distance:.1f} cm")
       
        if pos == -0.5 and distance < 25:
            print("Distance less than 25 cm detected at position -0.5. Turning left.")
            scan_for_duration(turn_left, 1)
            scan_with_ultrasonic()
            break
        elif pos == 0.5 and distance < 25:
            print("Distance less than 25 cm detected at position 0.5. Turning right.")
            scan_for_duration(turn_right, 1)
            scan_with_ultrasonic()
            break
        elif pos == 0 and distance < 30:
            print("Obstacle in front. Moving back.")
            scan_for_duration(move_backward, 1)
            scan_with_ultrasonic()
            break
    stop_robot()
    print("Returning servo to center position (90 degrees).")
    servo.value = 0
    sleep(0.5)


def remote_control(stdscr):
    # Disable cursor and enable keypad input
    curses.curs_set(0)
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(10)  # Set input timeout to 100ms (check every 100ms)

    last_command = None  # Track last command to avoid redundant screen updates
    running = True

    while running:
        new_key = stdscr.getch()

        # Exit on 'q'
        if new_key == ord('q'):
            running = False
            break

        # Key press actions
        if new_key == ord('w'):  # Forward
            if last_command != "forward":
                ena.value = 1  # Set to 70% speed
                enb.value = 1
                motor_left.forward()
                motor_right.forward()
                last_command = "forward"
                stdscr.clear()
                stdscr.addstr(0, 0, "Moving forward.")
                stdscr.refresh()

        elif new_key == ord('s'):  # Backward
            if last_command != "backward":
                ena.value = 1  # Set to 70% speed
                enb.value = 1
                motor_left.backward()
                motor_right.backward()
                last_command = "backward"
                stdscr.clear()
                stdscr.addstr(0, 0, "Moving backward.")
                stdscr.refresh()

        elif new_key == ord('a'):  # Turn left
            if last_command != "left":
                ena.value = 1  # Set to 70% speed
                enb.value = 1
                motor_left.backward()
                motor_right.forward()
                last_command = "left"
                stdscr.clear()
                stdscr.addstr(0, 0, "Turning left.")
                stdscr.refresh()

        elif new_key == ord('d'):  # Turn right
            if last_command != "right":
                ena.value = 1  # Set to 70% speed
                enb.value = 1
                motor_left.forward()
                motor_right.backward()
                last_command = "right"
                stdscr.clear()
                stdscr.addstr(0, 0, "Turning right.")
                stdscr.refresh()

        # Stop the robot when no key is pressed (continuous check)
        elif new_key == -1:  # No key pressed, stop the robot
            if last_command is not None:
                motor_left.stop()
                motor_right.stop()
                last_command = None
                stdscr.clear()
                stdscr.addstr(0, 0, "Stopping robot.")
                stdscr.refresh()

        curses.napms(55)  # 30 or 40 or 50 or 55 should be correct

    stop_robot()
    stdscr.clear()  # Clear the screen once the remote control stops
    stdscr.addstr(1, 0, "Remote control stopped.")
    stdscr.refresh()
    curses.napms(20)  # Wait for a second before ending
    recognize_voice_command()
# Run the curses function

def speak_time():
    """Get the current time in IST and speak it out."""
    current_time = get_time_in_ist()  # Get current time in IST
    speech_text = f"The current time in IST is {current_time}"  # Prepare speech text
    speak(speech_text)  # Use speak function to convert text to speech
    recognize_voice_command()

def get_time_in_ist():
    """Get the current time in IST."""
    # Define the IST time zone
    ist = pytz.timezone('Asia/Kolkata')

    # Get current time in UTC
    utc_now = datetime.datetime.now(pytz.utc)

    # Convert the UTC time to IST
    ist_time = utc_now.astimezone(ist)

    # Format the time to a readable string
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')
    



    

# Start remote control


recognize_voice_command()

try:
    while True:
        if current_command not in ["backward", "turn right", "turn left", "degrees", "zero degrees", "90 degrees", "180 degrees", "zero degree", "90 degree", "180 degree", "80 degree"]:
            distance_center = front_servo_sensor.distance * 100
            print(f"Distance Center: {distance_center:.1f} cm")

            if distance_center < 50:
                print("Object detected within 25 cm. Starting scan.")
                run_for_duration(scan_with_ultrasonic, 7)
                stop_robot()
        else:
            print("Center ultrasonic sensor disabled for this command.")

        if current_command not in ["forward", "forword", "four word", "start" , "go", "degrees", "zero degrees", "90 degrees", "180 degrees", "zero degree", "90 degree", "180 degree", "80 degree"]:
            distance_back = back_center_sensor.distance * 100
            print(f"Distance Back: {distance_back:.1f} cm")

            if distance_back > 8:
                print("Back edge detected.")
                run_for_duration(move_forward, 1)
                recognize_voice_command()
        else:
            print("Back sensor disabled for this command.")
  
        if current_command not in ["backward", "bad word", "back word", "backword", "bhagwat", "zero degrees", "90 degrees", "180 degrees", "degrees", "zero degree", "90 degree", "180 degree", "80 degree"]:
            distance_left = front_left_sensor.distance * 100
            print(f"Distance Left: {distance_left:.1f} cm")

            if distance_left > 8:
                print("Edge detected by left sensor.")
                run_for_duration(move_backward, 1)
                recognize_voice_command()
                
            distance_right = front_right_sensor.distance * 100
            print(f"Distance Right: {distance_right:.1f} cm")

            if distance_right > 8:
                print("Edge detected by right sensor.")
                run_for_duration(move_backward, 1)
                recognize_voice_command()
                
        sleep(0.01)
  
except KeyboardInterrupt:
    print("Program stopped by user.")
finally:
    stop_robot()

