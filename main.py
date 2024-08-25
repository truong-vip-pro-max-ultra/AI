import tkinter
from tkinter import *
from tkinter.filedialog import askopenfilename
import cv2
import PIL.Image , PIL.ImageTk
import time

# from blur_bgr.utils import FPSmetric
# from blur_bgr.selfieSegmentation import MPSegmentation
# from blur_bgr.engine import Engine
import numpy as np

WIDTH = 360
HEIGHT = 640


class App:
    def __init__(self, window, window_title, video_source=0):
        self.pos_x = 0
        self.pos_y = 0
        self.index_move = 10
        self.val_size_logo = 50
        self.window = window
        self.window.title(window_title)
        self.window.configure(background='#444444')
        self.window.geometry(f'{self.window.winfo_screenwidth()}x{self.window.winfo_screenheight()}+-10+0')
        self.image_source = video_source
        self.logo_source = ""
        self.radio_blur_val = StringVar(self.window, "1")

        bgr_img = PhotoImage(file = "bgr.png")

        background_label = Label(window, image=bgr_img)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        

        self.title = Label(window,text = "Blur Image",font=("Times",15))
        self.title.pack()

        btn_upload = PhotoImage(file = "btn_upload.png")
        self.btn_open_file=tkinter.Button(window, image=btn_upload, width=60, command=self.open_file_image)
        self.btn_open_file.pack(anchor=tkinter.CENTER, expand=True,padx=200, pady = 100)


        self.lb_option_blur = Label(self.window)
        btn_save = PhotoImage(file = "btn_save.png")
        self.btn_export=tkinter.Button(self.lb_option_blur, image=btn_save, command=self.export_image)

        self.window.mainloop()


    def resize(self,img,new_width=1000):
        ratio = img.height/img.width
        new_height = int(ratio*new_width)
        return img.resize((new_width, new_height), PIL.Image.ANTIALIAS)
    def resize_cv2(self,img,new_width=1000):
        height,width,_ = img.shape
        ratio = height/width
        new_height = int(ratio*new_width)
        return cv2.resize(img,(new_width,new_height))

    def open_file_image(self):
        open_file = Tk()
        open_file.withdraw()
        file_name = askopenfilename()

        self.image_source= file_name

        self.image_core = PIL.Image.open(file_name)

        self.image_bgr = self.resize(self.image_core,500)

        self.image_bgr = PIL.ImageTk.PhotoImage(self.image_bgr)

        self.label_image = tkinter.Label(image=self.image_bgr)
        self.label_image.image = self.image_bgr

        self.label_image.pack()


        self.btn_open_file.after(0, self.btn_open_file.destroy())


        values = {"Mặt người" : "1",
                    "Đôi mắt" : "2",
                    "hình chữ nhật" : "3",
                    "hình tam giác": "4",
                    "hình tròn": "5",
                    "vị trí": "6"
        }
        Label(self.window,text="Select option blur",font=("Times",15)).pack()
        
        self.lb_option_blur.pack(anchor=tkinter.CENTER)
        for (text, value) in values.items():
            if value != '6':
                Radiobutton(self.lb_option_blur, text = text, variable = self.radio_blur_val,
                    value = value, width=10).pack(side=tkinter.LEFT)
            else:
                lb_blur_pos = Label(self.lb_option_blur)
                lb_blur_pos.pack(side=tkinter.LEFT)
                Radiobutton(lb_blur_pos, text = text, variable = self.radio_blur_val,
                    value = value, width=10).pack(side=tkinter.LEFT) 
                lb_input_pos = Label(lb_blur_pos)
                lb_input_pos.pack(side=tkinter.LEFT)

                lb_pos_x = Label(lb_input_pos)
                lb_pos_x.pack(side=tkinter.LEFT)

                lb_pos_y = Label(lb_input_pos)
                lb_pos_y.pack(side=tkinter.RIGHT)


                info_shape = PIL.Image.open(self.image_source)
                info_shape = self.resize(info_shape,500)

                Label(lb_pos_x,text="X: ").pack(side=tkinter.LEFT)
                self.input_pos_x = Scale(lb_pos_x, from_=0, to=info_shape.width-99, orient=HORIZONTAL,command=self.update_pos_blur)
                self.input_pos_x.set(0)
                self.input_pos_x.pack(side=tkinter.RIGHT)
                

                Label(lb_pos_y,text="Y: ").pack(side=tkinter.LEFT)
                self.input_pos_y = Scale(lb_pos_y, from_=0, to=info_shape.height-99, orient=HORIZONTAL,command=self.update_pos_blur)
                self.input_pos_y.set(0)
                self.input_pos_y.pack(side=tkinter.RIGHT)

        self.btn_export.pack(side=tkinter.LEFT,pady = 10)

    def update_pos_blur(self,event):
        try:
            self.lb_blur.after(0, self.lb_blur.destroy())
        except:
            pass
        x = int(self.input_pos_x.get())
        y = int(self.input_pos_y.get())
        self.lb_blur = Label(self.label_image,text="POSITION BLUR",width=14,height=7)
        self.lb_blur.place(x=x,y=y)

    def export_image(self):
        val = self.radio_blur_val.get()
        if val == "1":
            self.blur_model("face")
        elif val == "2":
            self.blur_model("eye")
        elif val == '3':
            self.blur_geometry('rectangle')
        elif val == '4':
            self.blur_geometry('triangle')
        elif val == '5':
            self.blur_geometry('circle')
        elif val == '6':
            self.blur_pos()

    def blur_pos(self):
        size_blur = 100
        frame = cv2.imread(self.image_source)
        frame = self.resize_cv2(frame,500)
        x = int(self.input_pos_x.get())
        y = int(self.input_pos_y.get())
        frame[y:y+size_blur,x:x+size_blur] =  cv2.blur(frame[y:y+size_blur,x:x+size_blur], (100,100))
        cv2.imwrite("output.png",frame)
        PIL.Image.open("output.png").show()
        # cv2.imshow('a',frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     cv2.destroyAllWindows()

    def blur_model(self,model):
        face_cascade = cv2.CascadeClassifier("model/"+model+".xml")

        frame = cv2.imread(self.image_source)
        detections = face_cascade.detectMultiScale(frame,scaleFactor=1.1,minNeighbors=6)
        for face in detections:
            x,y,w,h = face
            frame[y:y+h,x:x+w] =  cv2.blur(frame[y:y+h,x:x+w], (100,100))  #cv2.GaussianBlur(frame[y:y+h,x:x+w],(55,55),2)
        # cv2.imshow('Exporting, Press Q To Exit',frame)
        cv2.imwrite("output.png",frame)
        PIL.Image.open("output.png").show()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()

    def getContours(self,imgContour,img,geometry):
        contours,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area>500:
                # cv2.drawContours(imgContour,cnt,-1,(255,0,255),10)
                peri = cv2.arcLength(cnt,True)
                approx = cv2.approxPolyDP(cnt,0.02*peri,True)
                objCor = len(approx)
                x,y,w,h = cv2.boundingRect(approx)
                if objCor == 3 and geometry == 'triangle':
                    imgContour[y:y+h,x:x+w] = cv2.blur(imgContour[y:y+h,x:x+w], (100,100)) # cv2.GaussianBlur(imgContour[y:y+h,x:x+w],(15,15),cv2.BORDER_DEFAULT)
                elif objCor == 4 and geometry == 'rectangle':
                    imgContour[y:y+h,x:x+w] = cv2.blur(imgContour[y:y+h,x:x+w], (100,100)) # cv2.GaussianBlur(imgContour[y:y+h,x:x+w],(15,15),cv2.BORDER_DEFAULT)
                elif objCor > 4 and geometry == 'circle':
                    imgContour[y:y+h,x:x+w] = cv2.blur(imgContour[y:y+h,x:x+w], (100,100)) # cv2.GaussianBlur(imgContour[y:y+h,x:x+w],(15,15),cv2.BORDER_DEFAULT)
        cv2.imwrite("output.png",imgContour)
        PIL.Image.open("output.png").show()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
    def blur_geometry(self,geometry):

        frame = cv2.imread(self.image_source)

        imgContour = frame.copy()
        imgGray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray,(15,15),1)
        imgCanny = cv2.Canny(imgBlur,50,50)
        self.getContours(imgContour,imgCanny,geometry)

# Create a window and pass it to the Application object
App(tkinter.Tk(), "Blur Object")
