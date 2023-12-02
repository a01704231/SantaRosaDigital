import paho.mqtt.client as mqtt
import numpy as np
import serial
import time

Ts = 1      # intervalo
Fs = 2500   # frecuencia de muestreo
Ps = 1/Fs   # periodo de muestreo
s = Ts/Ps   # muestras en el intervalo

# listas de valores de lectura de micrófonos (1,2,3)
mic1 = []
mic2 = []
mic3 = []

# booleanos que indican la ruta en la que va la ambulancia
route1=False
route2=False

t=0         # variable del tiempo desde la ejecución
state=0     # estado del sistema de semáforos (0 o 1)
timeLast=0  # variable usada en el cambio normal de los semáforos

# conexión con el broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# publicación de tópicos para prender los semáforos en estado 0
def state0():
    global state
    state=0
    client.publish("esp32/lights1","true")
    client.publish("esp32/lights2","true")
    client.publish("esp32/lights3","true")
    client.publish("esp32/lights4","true")
    client.publish("esp32/lights5","false")
    client.publish("esp32/lights6","false")
    client.publish("esp32/lights7","false")
    client.publish("esp32/lights8","false")
    print("lights state:\tG\tG\tG\tG\tR\tR\tR\tR")

# publicación de tópicos para prender los semáforos en estado 1
def state1():
    global state
    state=1
    client.publish("esp32/lights1","false")
    client.publish("esp32/lights2","false")
    client.publish("esp32/lights3","false")
    client.publish("esp32/lights4","false")
    client.publish("esp32/lights5","true")
    client.publish("esp32/lights6","true")
    client.publish("esp32/lights7","true")
    client.publish("esp32/lights8","true")
    print("lights state:\tR\tR\tR\tR\tG\tG\tG\tG")

# función para obtener los valores una línea de la lectura serial
def get_nums(arr):
    parts = arr.split()
    nums = []
    for x in parts:
        try:
            num = float(x)
            nums.append(num)
        except ValueError:
            pass
    return nums

# función para obtener la frecuencia de una muestra
def get_peak_frequency(signal, sampling_rate):
    fft_result = np.fft.fft(signal)
    frequencies = np.fft.fftfreq(len(signal), 1/sampling_rate)
    positive_frequencies = frequencies[:len(frequencies)//2]
    positive_fft_result = np.abs(fft_result[:len(frequencies)//2])
    positive_fft_result[0]=0
    peak_index = np.where(positive_fft_result == max(positive_fft_result))[0]
    peak_frequency = positive_frequencies[peak_index]
    return peak_frequency

# configuración de conexión con el broker mqtt
client = mqtt.Client()
client.on_connect = on_connect
client.connect("192.168.137.182", 1883, 60)

# inciar la cuenta del tiempo
start = time.time()*1000//1

# iniciar semáforos en estado 0
state0()

# iniciar lectura serial (datos de ESP32)
sdata = serial.Serial('/dev/ttyUSB0',115200,timeout=1.0)
time.sleep(2)
sdata.reset_input_buffer()
print("connected")

# ciclo
while True:
    # retraso: periodo de muestreo
    time.sleep(Ps)

    # cambio normal de los semáforos
    end = time.time()*1000//1
    timeNow=end-start
    if ((timeNow-timeLast)>=5000):
        timeLast=timeNow
        if (state==0):
            state1()
        elif (state==1):
            state0()
    
    # cambio de los semáforos si hay ambulancia
    if sdata.in_waiting > 0:
        mydata = sdata.readline().decode('utf-8').rstrip()
        nums = get_nums(mydata)
        for i in range(len(nums)):
            if (nums[i]<0 or nums[i]>4095):
                nums[i]=0
        if (len(nums)==0):
            mic1.append(0)
            mic2.append(0)
            mic3.append(0)
        elif (len(nums)==1):
            mic1.append(nums[0])
            mic2.append(0)
            mic3.append(0)
        elif (len(nums)==2):
            mic1.append(nums[0])
            mic2.append(nums[1])
            mic3.append(0)
        else:
            mic1.append(nums[0])
            mic2.append(nums[1])
            mic3.append(nums[2])
        if (len(mic1)==s):
            f_mic1 = get_peak_frequency(mic1, Fs)[0]
            f_mic2 = get_peak_frequency(mic2, Fs)[0]
            f_mic3 = get_peak_frequency(mic3, Fs)[0]
            t=t+Ts
            print('\nTiempo: '+str(t)+' segundos')
            print(' Frecuencia mic1:\t'+str(f_mic1)+'\n','Frecuencia mic2:\t'+str(f_mic2)+'\n','Frecuencia mic3:\t'+str(f_mic3)+'\n')
            '''
            if (t==Ts):
                print(mic1)
            '''
            if (f_mic1>=700 and f_mic1<=1200):
                route1=True
                route2=False
                state0()
            if (f_mic2>=700 and f_mic2<=1200):
                route2=True
                if (route1==False):
                    state1()
                else:
                    state0()
            if (f_mic3>=700 and f_mic3<=1200):
                route1=False
                if (route2==False):
                    state0()
                else:
                    state1()
            mic1=[]
            mic2=[]
            mic3=[]
