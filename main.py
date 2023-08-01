import os
import subprocess
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import util
import numpy as np
import datetime

class App:
    def __init__(self):
        # create main window
        self.main_window = tk.Tk()

        # create window size
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main_window = util.get_button(self.main_window, 
                                                        text="Login", 
                                                        color="green", 
                                                        command=self.login)
        self.login_button_main_window.place(x=750, y=300)


        self.register_new_user_button_main_window = util.get_button(self.main_window, 
                                                                    text="Register new user", 
                                                                    color="gray", 
                                                                    command=self.register_new_user, 
                                                                    fg="black")
        self.register_new_user_button_main_window.place(x=750, y=400)

        # create webcam label
        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        # add stream
        self.add_webcam(self.webcam_label)

        # create db image dir -> store images
        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = './log.txt'


    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()


    def process_webcam(self):
        # read frames captured
        ret, frame = self.cap.read()
        self.most_recent_capture_arr = frame

        # You may need to convert the color.
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)

        # convert cv2 format -> PIL format -> tk format
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
           
        # config label with image
        self._label.imagetk = imgtk
        self._label.configure(image=imgtk)
        
        # repeat call again after 20s
        self._label.after(20, self.process_webcam)

    
    # Login
    def login(self):
        unknow_img_path = './.tmp.jpg'

        # write img to path
        cv2.imwrite(unknow_img_path, self.most_recent_capture_arr)

        # run face_recognition command in sub process to get output
        # ref link: https://github.com/ageitgey/face_recognition
        output = str(subprocess.check_output(['face_recognition', self.db_dir, unknow_img_path]))
        name = output.split(',')[1][:-5]

        
        if name in ['unknown_person', 'no_persons_found']:
            util.msg_box(title='Oops....!!!', description='Unknown user. Please try again!')
        else:
            util.msg_box(title='Welcome back!', description='Hello, {}'.format(name))
            # write log file
            with open(self.log_path, 'a') as f:
                f.write('{}, {}\n'.format(name, datetime.datetime.now()))
                f.close()


        
        os.remove(unknow_img_path)


    
    # Register
    def register_new_user(self):
        # create another window
        self.register_new_user_window = tk.Toplevel(self.main_window)

        self.register_new_user_window.geometry("1200x520+370+120")

        self.login_button_register_new_user_window = util.get_button(self.register_new_user_window, 
                                                        text="Accept", 
                                                        color="green", 
                                                        command=self.accept_register_new_user)
        self.login_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 
                                                                    text="Try again", 
                                                                    color="red", 
                                                                    command=self.try_again_register_new_user, 
                                                                    fg="black")
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        # add single image to label
        self.add_image_to_label(self.capture_label)


        # create entry text
        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=150)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 
                                                                text="Please, \ninput username:")

        self.text_label_register_new_user.place(x=750, y=70)

    

    def add_image_to_label(self, label):
        # config label with image
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imagetk = imgtk
        label.configure(image=imgtk)

        # capture most recent img at register time
        self.register_new_user_capture = self.most_recent_capture_pil.copy()

    

    def try_again_register_new_user(self):
        # exit this window
        self.register_new_user_window.destroy()
    
        

    def accept_register_new_user(self):
        # get data in tk Text input 
        name = self.entry_text_register_new_user.get('1.0', 'end-1c').strip()

        # write image register to db dir
        cv2.imwrite(os.path.join(self.db_dir, '{}.jpg'.format(name)), np.array(self.register_new_user_capture))

        # show message box
        util.msg_box(title="Success!", description="User was registered successfully!!")

        self.register_new_user_window.destroy()

    
 
    # Start app
    def start(self):
        self.main_window.mainloop()
    

if __name__ == "__main__":
    app = App()
    app.start()