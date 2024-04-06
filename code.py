from p5 import *
from pylsl import StreamInlet, resolve_stream

GRAPH_LENGTH = 650  # Size for each graph

# Arrays for data points (ECG, EDA, and respiration)
ecg_points = [0] * GRAPH_LENGTH
eda_points = [0] * GRAPH_LENGTH
resp_points = [0] * GRAPH_LENGTH

# Stream of data from OpenSignals(r)
streams = resolve_stream('name', 'OpenSignals')
stream = StreamInlet(streams[0])

def setup():
    size(1500, 900)  # Window size
    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf" #Font
    custom_font = create_font(font_path, 32)
    text_font(custom_font)

    global background_image, second_image, third_image, button_2, button_3, button_1, button_on, display_second_image, display_third_image, biofeedback_on, display_biofeedback_image, biofeedback_image
    
    background_image = load_image('/Users/ines/Desktop/Template.png') #find image in folders
    second_image = load_image('/Users/ines/Desktop/Template2.png') #find image in folders
    third_image = load_image('/Users/ines/Desktop/Template3.png') #find image in folders
    biofeedback_image = load_image('/Users/ines/Desktop/TemplateBio.png') #find image in folders
    
    button_on = Button(1100, 35, 270, 100, "On", background_image)
    button_1 = Button(70, 40, 100, 100, "1", background_image)
    button_2 = Button(1300, 750, 100, 100, "2", second_image)
    button_3 = Button(70, 40, 100, 100, "3", third_image)
    
    display_second_image = False
    display_third_image = False
    display_biofeedback_image =False
    biofeedback_on = False

#ECG
peak_count=0
resp_count=0
valeurs_minute_ecg=[] # list to have 6 data : 60sec/10sec=6

#Electrodermal activity of skin
data_eda = [] #list for eda data

#Respiration
valeurs_minute_resp=[] # list to have 6 data : 60sec/10sec=6

#if less than 60 sec.
def calculer_bpm_debut(valeurs_minute_ecg,debut):
    # Sum of array values
    bpm = sum(valeurs_minute_ecg)
    if debut==1:
        bpm=bpm*6
    if debut==2:
        bpm=bpm*3
    if debut==3:
        bpm=bpm*2
    if debut==4:
        bpm=round(bpm*1.5)
    if debut==5:
        bpm=round(bpm*1.2)
    if debut==6:
        bpm=bpm
    # Print result 
    print("BPM :", bpm)
    return bpm

def calculer_resp_debut(valeurs_minute_resp,debut):
    # Sum of array values
    respmin = sum(valeurs_minute_resp)
    if debut==1:
        respmin=respmin*6
    if debut==2:
        respmin=respmin*3
    if debut==3:
        respmin=respmin*2
    if debut==4:
        respmin=round(respmin*1.5)
    if debut==5:
        respmin=round(respmin*1.2)
    if debut==6:
        respmin=respmin
    # Print result 
    print("Nb de resp/min :", respmin)
    return respmin

#if more than 60 sec.
def calculer_bpm(valeurs_minute_ecg):
    # Sum of array values
    bpm = sum(valeurs_minute_ecg)
    # Print result 
    print("BPM :", bpm)
    return bpm

def calculer_resp(valeurs_minute_resp):
    # Sum of array values
    respmin = sum(valeurs_minute_resp)
    # Print result 
    print("Nb de resp/min :", respmin)
    return respmin

#Values initialization
debut=1
n=0
bpm=0
rpm=0
eda_value=0

#if resp ou beat
in_resp=False
in_batt=False

#To display values on the window
def biofeedback_values(bpm,rpm,eda_value):
        textSize(50)
        fill(255)  # White text
        
        text(f"{bpm}", 220, 730)
        text(f"{rpm}", 1190, 730)
        text(f"{eda_value}", 705, 730)

#To switch menu 
class Button:
    def __init__(self, x, y, width, height, label, target_image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.target_image = target_image

    def display(self):
        fill(255)

    def clicked(self):
        return self.x < mouse_x < self.x + self.width and self.y < mouse_y < self.y + self.height

def mouse_pressed():
    global display_second_image, display_third_image, biofeedback_on
    if button_on.clicked():
        biofeedback_on = True
       
    if button_1.clicked()and not display_second_image and not display_third_image and not display_biofeedback_image:
        display_second_image = not display_second_image
        display_third_image = False

    elif button_2.clicked() and display_second_image:
        display_third_image = not display_third_image
        display_second_image = False
        
    elif button_3.clicked() and display_third_image:
        display_second_image = False
        display_third_image = False


#Main function to display biofeedback system
def draw():
    global display_second_image, display_third_image, biofeedback_on, display_biofeedback_image
    
    global in_resp, in_batt,resp_count,peak_count,n,debut,bpm,rpm,eda_value

    # Display background image
    image(background_image, 0, 0)
    button_on.display()
    if not display_second_image and not display_third_image:
        button_1.display()
    elif display_second_image:
        button_2.display()
    elif display_third_image:
        button_3.display()

    if display_second_image:
        image(second_image, 0, 0)
    elif display_third_image:
        image(third_image, 0, 0)
    
    #BIOFEEDBACK in real-time
    elif biofeedback_on:
        display_biofeedback_image=True
        image(biofeedback_image, 0, 0)
        if n < 1000 :
            # Pull data from stream and update graphs
            for _ in range(15):  # Pull multiple samples before updating the plots => makes it faster to be real time
                values, timestamp = stream.pull_sample()
                
                # Update for ecg, eda, resp
                update_points(ecg_points, values[1] * 200)
                update_points(eda_points, values[2] * 2)
                update_points(resp_points, values[3] * 50)
                
                #respiration counts
                if in_resp == True:
                    if values[3] < -0.1:
                        in_resp = False
                else :
                    if values[3] > 0.1:
                        resp_count+=1
                        in_resp = True
                        
                #ecg counts            
                if in_batt == True:
                    if values[1] < 0:
                        in_batt = False
                else :
                    if values[1] > 0.2:
                        peak_count+=1
                        in_batt = True

                #eda value
                data_eda.append(values[2])    
            
            #Display graph
            draw_ecg(ecg_points, 52, update_color(bpm,'bpm'))
            draw_ecg(eda_points, 528, update_color(eda_value,'eda'))
            draw_ecg(resp_points, 1005, update_color(rpm,'rpm'))
            #next sample
            n+=15
            #Display values
            biofeedback_values(bpm,rpm,eda_value)
            
        else :
            
            if debut<=6:
                valeurs_minute_resp.append(resp_count)
                valeurs_minute_ecg.append(peak_count)
                bpm=round(calculer_bpm_debut(valeurs_minute_ecg,debut))
                rpm=round(calculer_resp_debut(valeurs_minute_resp,debut))
                eda_value = round(sum(data_eda)/len(data_eda),2)
                debut+=1

            else :
                valeurs_minute_ecg.pop(0)
                valeurs_minute_resp.pop(0)
                valeurs_minute_resp.append(resp_count)
                valeurs_minute_ecg.append(peak_count)
                bpm=round(calculer_bpm(valeurs_minute_ecg))
                rpm=round(calculer_resp(valeurs_minute_resp))
                eda_value = round(sum(data_eda)/len(data_eda),2)
                
            draw_ecg(ecg_points, 52, update_color(bpm,'bpm'))
            draw_ecg(eda_points, 528, update_color(eda_value,'eda'))
            draw_ecg(resp_points, 1005, update_color(rpm,'rpm'))
            
            biofeedback_values(bpm,rpm,eda_value)
            
            n=0
            resp_count=0
            peak_count=0

#To change color of graphs depending on the values
            
def update_color(value, type):
    
    #Reference values
    #bpm ref at 65
    #rpm ref at 15
    #eda ref at 3
    bpmref=65
    rpmref=15
    edaref=3

    if type=='bpm':
        difference=abs(bpmref-value)

        if  difference<2:
            return (0, 204, 0)
        elif difference<4:
            return (0, 153, 0)
        elif difference<6:
            return (0, 153, 76)
        elif difference<8:
            return (0, 153, 153)
        elif difference<10:
            return (0, 76, 153)
        elif difference<14:
            return (0, 0, 153)
        elif difference<18:
            return (76, 0, 153)
        elif difference<24:
            return (153, 0, 153)
        elif difference<30:
            return (153, 0, 76)
        else:
            return (153, 0, 0)
    if type=='eda':
        difference=abs(edaref-value)

        if  difference<0.2:
            return (0, 204, 0)
        elif difference<0.8:
            return (0, 153, 0)
        elif difference<1.4:
            return (0, 153, 76)
        elif difference<2:
            return (0, 153, 153)
        elif difference<3:
            return (0, 76, 153)
        elif difference<5:
            return (0, 0, 153)
        elif difference<7:
            return (76, 0, 153)
        elif difference<9:
            return (153, 0, 153)
        elif difference<11:
            return (153, 0, 76)
        else:
            return (153, 0, 0)
    if type=='rpm':
        difference=abs(rpmref-value)
        if  difference<2:
            return (0, 204, 0)
        elif difference<3:
            return (0, 153, 0)
        elif difference<5:
            return (0, 153, 76)
        elif difference<7:
            return (0, 153, 153)
        elif difference<9:
            return (0, 76, 153)
        elif difference<11:
            return (0, 0, 153)
        elif difference<13:
            return (76, 0, 153)
        elif difference<15:
            return (153, 0, 153)
        elif difference<18:
            return (153, 0, 76)
        else:
            return (153, 0, 0)

#To display graphs 
        
def update_points(points, new_value):
    points.pop(0)
    points.append(new_value)

def draw_ecg(data_points, x_offset, line_color, y_offset=100):
    no_fill()
    stroke(*line_color)
    begin_shape()
    for i, y_value in enumerate(data_points):
        x = lerp(x_offset, x_offset + 1760 / 4, i / GRAPH_LENGTH)
        y = lerp(900 - 150 + y_offset, y_offset, (y_value + 150) / 300)
        vertex(x, y)
    end_shape()
    fill(*line_color)

#RUN CODE
if __name__ == "__main__":
   run()



    
