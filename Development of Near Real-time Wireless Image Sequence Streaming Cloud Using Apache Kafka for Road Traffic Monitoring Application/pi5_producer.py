import io
import time
import picamera
from kafka import KafkaProducer
import pickle
import threading
import pickle
from datetime import datetime

producer = [KafkaProducer(bootstrap_servers=['10.0.0.8:9092'], acks = 1, linger_ms = 0, retries = 0, max_in_flight_requests_per_connection = 11)]

producer.append(KafkaProducer(bootstrap_servers=['10.0.0.9:9092'], acks = 1, linger_ms = 0, retries = 0, max_in_flight_requests_per_connection = 11))

print('all producers instantiated already here')

topic1 = 'PhayaThai-5'

producer_id = 1
batches = 1
frame = 1
image = 1
max_batches = 3
max_image_in_batch = 50
producer_timeout = 5

gw_switch = []

def save_gw_switch():
    global gw_switch
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d_" + "%H:%M:%S.%f")
    threading.Timer(300.0, save_gw_switch).start()

    with open('/home/raspi5/Downloads/pi5 gw switch list' + current_time + '.txt', 'w') as fp:
        pickle.dump(gw_switch, fp)
    gw_switch *= 0

save_gw_switch()

while True:
    def outputs():
        global producer_id
        global batches
        global max_batches
        global frame
        global image
        global max_image_in_batch
        global producer_timeout

        flag = True

        while (flag or batches == 0):
            if batches <= max_batches:
                flag = True
                print(batches)
                batches+=1
                try:
                    while image <= max_image_in_batch:
                        stream1 = io.BytesIO()
                        yield stream1
#                        img_raw1 = str(frame) + ' chula ' + stream1.getvalue()
                        now = float(round(time.time() * 1000))
                        current_time = datetime.now().strftime("%Y-%m-%d_" + "%H:%M:%S")
                        img_raw1 = str(frame) + ' chula ' + str(now) +  ' chula ' + stream1.getvalue() + ' chula ' + current_time
#                        img_raw1 = str(frame) + ' chula ' + str(now) +  ' chula ' + stream1.getvalue()
                        failure = producer[producer_id].send(topic1, img_raw1)
                        print('Producer is sending: '+ str(frame) + ' to GW '+ str(producer_id+1))
                        frame = frame+1
                        image = image + 1
                        time.sleep(10)
                    image = 1
                    producer[producer_id].flush(timeout = producer_timeout)
                except:
                    gw_old = 'GW'+str(producer_id+1)
                    producer_id = (producer_id + 1)%2
                    gw_new = 'GW'+str(producer_id+1)
                    batches = 1
                    now = datetime.now()
                    current_time = now.strftime("%Y-%m-%d_" + "%H:%M:%S.%f")

                    print('switching from '+ gw_old +' to '+ gw_new)
                    gw_switch.append('switching from '+ gw_old +' to '+ gw_new)
                    gw_switch.append(current_time)
#                print(batches)
#                batches+=1
            else:
                flag = False
                batches = 1
                producer_id = 1

    with picamera.PiCamera(resolution = (320, 180), framerate = 24) as camera:
        camera.capture_sequence(outputs(), 'jpeg', use_video_port=True)

