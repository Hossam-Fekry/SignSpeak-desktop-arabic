from tkinter import *
from PIL import Image, ImageTk
import cv2
from tkinter import filedialog
import mediapipe as mp

win = Tk()
width=win.winfo_screenwidth()
height=win.winfo_screenheight()
win.geometry("%dx%d" % (width, height))
win.configure(bg="#ECF0F1")
win.title('Sign Language App')

#make the photos variables
flag = PhotoImage(file="egypt_flag.png").subsample(12)

govern = PhotoImage(file="govern logo.png").subsample(3)
#make the labels for the photos
flag_label = Label(win,image=flag).place(x=50,y=50)
governorate_label = Label(win,image=govern).place(x=width-250,y=30)


global img, finalImage, finger_tips, thumb_tip, cap, image, rgb, hand, results, w, h, mpDraw, mpHands, hands, label1, status

cap=None

Label(win,text='SignSpeak app',font=('Helvatica',25,'bold'),bd=5,bg='#2C3E50',fg='#FFFFFF',relief=SOLID,width=200 ).pack(pady=50,padx=300)

# Initialize variables
finger_tips = [8, 12, 16, 20]
thumb_tip = 4
w = 500
h = 400

if cap:
    cap.release()

label1 = Label(win, width=w, height=h, bg="#ECF0F1")
label1.place(x=250, y=200)
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

########################################### Detection ##########################################

def detect_sign(lm_list):
    """ Detect signs based on landmarks. """
    # Check for "Peace" sign (Index and Middle fingers up, others folded)
    if lm_list[8].y < lm_list[7].y and lm_list[12].y < lm_list[11].y:  # Index and middle fingers up
        if lm_list[16].y > lm_list[15].y and lm_list[20].y > lm_list[19].y:  # Ring and pinky folded
            return "نعم, لقد انتصرنا"  # Peace sign detected
    
    # Check for "I Love You" sign (Thumb, index, and pinky fingers up)
    if lm_list[8].y < lm_list[7].y and lm_list[20].y < lm_list[19].y:  # Index and pinky fingers up
        if lm_list[12].y > lm_list[11].y and lm_list[16].y > lm_list[15].y:  # Middle and ring fingers down
            if lm_list[4].x < lm_list[3].x:  # Thumb extended (optional)
                return "انا احبك"
    
    # Check for "Thumbs Up" (Thumb up, others folded)
    if lm_list[4].y < lm_list[3].y:  # Thumb up
        if lm_list[8].y > lm_list[6].y and lm_list[12].y > lm_list[10].y:  # Index and middle folded
            if lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:  # Ring and pinky folded
                return "اعجاب"  # Thumbs Up sign detected
    
    if lm_list[4].y > lm_list[3].y:  # Thumb pointing down
        if lm_list[8].y > lm_list[6].y and lm_list[12].y > lm_list[10].y and lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:  # Other fingers folded down
            return "عدم اعجاب"
    
    # Check for "Stop" gesture (All fingers straight up)
    if lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y:  # Index and middle up
        if lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y:  # Ring and pinky up
            if lm_list[4].x < lm_list[3].x:  # Thumb extended
                return "توقف"  # Stop gesture detected
    
    # Check for "OK" (👌) sign (Thumb and index finger form a circle, others stretched)
    if lm_list[4].x - lm_list[8].x < 0.03 and lm_list[4].y - lm_list[8].y < 0.03:  # Thumb and index tips are close
        if lm_list[12].y < lm_list[10].y and lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y:  # Other fingers are stretched
            return "بالضبط"  # OK sign detected

        

    return "لم يتم التقاط اشاره"

def live():
    global img
    _, img = cap.read()
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    message = ""

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            lm_list = [lm for lm in hand.landmark]  # Collect all landmarks
            message = detect_sign(lm_list)  # Detect signs
            mpDraw.draw_landmarks(img, hand, mpHands.HAND_CONNECTIONS)
    
    image = Image.fromarray(rgb)
    finalImage = ImageTk.PhotoImage(image)
    label1.configure(image=finalImage)
    
    label1.image = finalImage
    
    # Update the label with the detected message
    status.configure(text=message)

    win.after(1, live)



# Create labels for status and buttons

status = Label(win, text="", font=('Helvetica', 18, 'bold'), bd=5, bg='gray', width=50, fg='#FFFFFF', relief=GROOVE)
status.place(x=400, y=650)

# Buttons
Button(win, text='ابدا مباشره', padx=95, bg='#2C3E50', fg='white', relief=RAISED, width=1, bd=5, font=('Helvatica', 12, 'bold'), command=live).place(x=width-250, y=450)
Button(win, text='خروج', padx=95, bg='#2C3E50', fg='white', relief=RAISED, width=1, bd=5, font=('Helvatica', 12, 'bold'), command=lambda: win.destroy()).place(x=650, y=700)

win.mainloop()
