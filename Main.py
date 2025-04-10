from tkinter import *
from PIL import Image, ImageTk
import cv2
from tkinter import filedialog
import mediapipe as mp
from playsound import playsound
import os

root = Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry("%dx%d" % (width, height))
root.configure(bg="#f0f0f5")
root.title('SignSpeak')

# الصور
flag = PhotoImage(file="egypt_flag.png").subsample(12)
govern = PhotoImage(file="govern logo.png").subsample(3)

Label(root, image=flag).place(x=50, y=50)
Label(root, image=govern).place(x=width - 250, y=30)

Label(root, text='SignSpeak', font=('Helvetica', 25, 'bold'), bd=5, bg='#2C3E50', fg='#FFFFFF', relief=SOLID, width=200).pack(pady=50, padx=300)

# المتغيرات
finger_tips = [8, 12, 16, 20]
thumb_tip = 4
w = 500
h = 400

cap = cv2.VideoCapture(0)

label1 = Label(root, width=w, height=h, bg="#ECF0F1")
label1.place(x=250, y=200)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

running = False
last_message = ""
sound_enabled = BooleanVar(value=True)

# دالة لاكتشاف الإشارة بناءً على التنسيق اليدوي
def detect_sign(lm_list):
    if lm_list[8].y < lm_list[7].y and lm_list[12].y < lm_list[11].y:
        if lm_list[16].y > lm_list[15].y and lm_list[20].y > lm_list[19].y:
            return "نعم لقد انتصرنا"
    if lm_list[8].y < lm_list[7].y and lm_list[20].y < lm_list[19].y:
        if lm_list[12].y > lm_list[11].y and lm_list[16].y > lm_list[15].y:
            if lm_list[4].x < lm_list[3].x:
                return "انا أحبك"
    if lm_list[4].y < lm_list[3].y:
        if lm_list[8].y > lm_list[6].y and lm_list[12].y > lm_list[10].y and lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:
            return "أعجاب"
    if lm_list[4].y > lm_list[3].y:
        if lm_list[8].y > lm_list[6].y and lm_list[12].y > lm_list[10].y and lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:
            return "عدم أعجاب"
    if lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y and lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y:
        if lm_list[4].x < lm_list[3].x:
            return "توقف"
    if abs(lm_list[4].x - lm_list[8].x) < 0.03 and abs(lm_list[4].y - lm_list[8].y) < 0.03:
        if lm_list[12].y < lm_list[10].y and lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y:
            return "بالضبط"
    if lm_list[4].y < lm_list[3].y and lm_list[8].y < lm_list[7].y and lm_list[12].y < lm_list[11].y and lm_list[16].y < lm_list[15].y and lm_list[20].y < lm_list[19].y:
        return "انا او نفسي"
    return "لا توجد إشارة"

# دالة لتشغيل الصوت حسب الرسالة
def speak_message(message):
    if sound_enabled.get():  # Check if sound is enabled
        file_path = os.path.join("voices", f"{message}.mp3")
        if os.path.exists(file_path):
            playsound(file_path)

# تشغيل الفيديو الحي
def start_live():
    global running
    running = True
    live()

# إيقاف الفيديو الحي
def stop_live():
    global running
    running = False
    label1.config(image='')  # Clear the image
    status.config(text="تم إيقاف الكاميرا")

# دالة لعرض الفيديو الحي
def live():
    global img, last_message
    if not running:
        return
    _, img = cap.read()
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    message = ""
    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            lm_list = [lm for lm in hand.landmark]
            message = detect_sign(lm_list)
            mpDraw.draw_landmarks(rgb, hand, mpHands.HAND_CONNECTIONS)
    image = Image.fromarray(rgb)
    finalImage = ImageTk.PhotoImage(image)
    label1.configure(image=finalImage)
    label1.image = finalImage
    status.configure(text=message)
    if message != "لا توجد إشارة" and message != last_message:
        speak_message(message)
        last_message = message
    elif message == "لا توجد إشارة":
        last_message = ""
    root.after(100, live)  # Delay reduced for better performance

# دالة لاختيار الفيديو
def video():
    global last_message
    path = filedialog.askopenfilename()
    if not path:
        return
    video_cap = cv2.VideoCapture(path)
    while video_cap.isOpened():
        ret, frame = video_cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (w, h))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        message = ""
        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                lm_list = [lm for lm in hand.landmark]
                message = detect_sign(lm_list)
                mpDraw.draw_landmarks(rgb, hand, mpHands.HAND_CONNECTIONS)
        image = Image.fromarray(rgb)
        finalImage = ImageTk.PhotoImage(image)
        label1.configure(image=finalImage)
        label1.image = finalImage
        status.configure(text=message)
        if message != "لا توجد إشارة" and message != last_message:
            speak_message(message)
            last_message = message
        elif message == "لا توجد إشارة":
            last_message = ""
        root.update()
        cv2.waitKey(50)
    video_cap.release()
    label1.config(image='')  # Clear the image
    status.config(text="تم الانتهاء من الفيديو")

# نافذة "حول"
def about():
    about_win = Toplevel()
    about_win.title("عن المطور")
    about_win.geometry("300x100")
    Label(about_win, text="الاسم: حسام فكري", font=('Helvetica', 12, 'bold')).pack()
    Label(about_win, text="الصف: السادس الابتدائي", font=('Helvetica', 12, 'bold')).pack()
    Label(about_win, text="المدرسة: مدارس العصر الحديث", font=('Helvetica', 12, 'bold')).pack()

status = Label(root, text="", font=('Helvetica', 18, 'bold'), bd=5, bg='gray', width=50, fg='#FFFFFF', relief=GROOVE)
status.place(x=400, y=650)

Button(root, text='تشغيل مباشر', padx=85, bg='#2C3E50', fg='white', relief=FLAT, font=('Helvetica', 12, 'bold'), command=start_live).place(x=width - 250, y=450)
Button(root, text='فيديو', padx=112, bg='#2C3E50', fg='white', relief=FLAT, font=('Helvetica', 12, 'bold'), command=video).place(x=width - 250, y=500)
Button(root, text='إيقاف', padx=112, bg='#2C3E50', fg='white', relief=FLAT, font=('Helvetica', 12, 'bold'), command=stop_live).place(x=width - 250, y=550)
Button(root, text='حول', padx=112, bg='#2C3E50', fg='white', relief=FLAT, font=('Helvetica', 12, 'bold'), command=about).place(x=width - 250, y=600)
Button(root, text='خروج', padx=112, bg='#2C3E50', fg='white', relief=FLAT, font=('Helvetica', 12, 'bold'), command=lambda: root.destroy()).place(x=650, y=700)

school_logo = PhotoImage(file="school logo.png")
Label(root, image=school_logo).place(x=width - 700, y=300)

# Sound Toggle Checkbox
sound_checkbox = Checkbutton(root, text="تشغيل الصوت", variable=sound_enabled, bg="#f0f0f5", font=('Helvetica', 12, 'bold'))
sound_checkbox.place(x=width - 250, y=750)

root.mainloop()
