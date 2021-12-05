from inference_detection_class import inferenceDectection

my_inference = inferenceDectection()
my_dict = my_inference.classifyImage("/home/swarren/Desktop/mycode/tensorflow_test_steven/images/keyboard.jpg")

my_inference.saveToImage(file_path="/home/swarren/Desktop/mycode/tensorflow_test_steven/inference_detection")
my_inference.showImage()
