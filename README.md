# FaceDetector


# SETUP
install the fallowing packages:
boto3
watchdog
Pillow
opencv-python
imutils

# USAGE
first run the face detector:
python3 detect_faces_video.py -p deploy.prototxt.txt -m res10_300x300_ssd_iter_140000.caffemodel 

then run the images folder detector:
python3 images_tracker.py
