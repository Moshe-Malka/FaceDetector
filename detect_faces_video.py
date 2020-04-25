# USAGE
# python detect_faces_video.py --prototxt deploy.prototxt.txt --model res10_300x300_ssd_iter_140000.caffemodel

# import the necessary packages
from imutils.video import VideoStream
from datetime import datetime
from PIL import Image
from uuid import uuid4
import numpy as np
import argparse
import imutils
import time
import cv2
import os

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.8,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream and allow the cammera sensor to warmup
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

image_idx = 0

# confidence_sum = 0
# confidence_count = 0

def create_folder_struct(path):
	if not os.path.exists(os.path.dirname(path)):
		try: os.makedirs(os.path.dirname(path))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST: raise

def save_frame_to_file(frame, path):
	try: 
		pic = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		Image.fromarray(pic).save(fpath)
	except Exception as e:
		print(f"Failed to save image - {e}")

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels

	frame = vs.read()
	frame = imutils.resize(frame, width=400)
 
	# grab the frame dimensions and convert it to a blob
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
 
	# pass the blob through the network and obtain the detections and
	# predictions
	net.setInput(blob)
	detections = net.forward()

	# loop over the detections
	for i in range(detections.shape[2]):
		# extract the confidence (i.e., probability) associated with the
		# prediction
		confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the `confidence` is
		# greater than the minimum confidence
		if confidence < args["confidence"]:
			continue
		
		# print("Face Detected")
		# confidence_sum += confidence
		# confidence_count += 1
		# compute the (x, y)-coordinates of the bounding box for the
		# object
		# box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
		# (startX, startY, endX, endY) = box.astype("int")
 
		# draw the bounding box of the face along with the associated
		# probability
		# print(f"confidence : {confidence}")

		current_minute = datetime.now().minute
		
		fpath = f'images/year={datetime.now().year}/month={datetime.now().month}/day={datetime.now().day}/hour={datetime.now().hour}/minute={current_minute}/snap_{image_idx}_{str(uuid4()).split("-")[-1]}_{confidence}.jpeg'
		
		create_folder_struct(fpath)
		
		save_frame_to_file(frame, fpath)
		
		image_idx += 1

		# text = f"{(confidence * 100):.2f}%"
		# y = startY - 10 if startY - 10 > 10 else startY + 10
		# cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
		# cv2.putText(frame, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
		# print(f"Average Confidence : {(confidence_sum/confidence_count)*100:.2f}%")

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()