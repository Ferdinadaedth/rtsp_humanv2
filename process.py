import os
import time
import ffmpeg
from queue import Queue
import threading
import subprocess
import cv2
class Rtsp:
    detect_queue=Queue()
    compose_queue=Queue()
    def __init__(self,rtsp_url,rtsp_output_url,demo_input,demo_output):
        self.rtsp_url =rtsp_url
        self.rtsp_output_url=rtsp_output_url
        self.demo_input=demo_input
        self.demo_output=demo_output
        self.lock = threading.Lock()  # 创建互斥锁
    def add_flie_to_queue(self):
        files = os.listdir(self.demo_input)
        sorted_files = sorted(files)
        for file_name in sorted_files:
            file_path = os.path.join(self.demo_input, file_name)
            if os.path.isfile(file_path) and not Rtsp.detect_queue.full():
                Rtsp.detect_queue.put(file_path)
    def detect(self):
        while True:
            if not Rtsp.detect_queue.empty():
                image_path=Rtsp.detect_queue.get()
                file_name = os.path.basename(image_path)
                pipeline_command = (
                f'python deploy/pipeline/pipeline.py --config deploy/pipeline/config/examples/infer_cfg_human_attr.yml '
                f'--image_file={image_path} --device gpu --output_dir demo_output'
                )
            # 使用 subprocess 运行命令行
                return_code = subprocess.call(pipeline_command, shell=True)
                if return_code == 0:
                    os.remove(image_path)
                Rtsp.compose_queue.put("demo_output/"+file_name)
            else:
                self.add_flie_to_queue()
    def split(self):
        output_file = "%Y%m%d_%H%M%S%f.jpg"
        # RTSP视频流URL
        ffmpeg.input(self.rtsp_url).output(f"{self.demo_input}/{output_file}", r=1, strftime=1).run()
    def compose(self):
        #ffmpeg_cmd=f"ffmpeg -f image2pipe -pix_fmt rgb24 -r 1 -i - -c:v libx264 -b:v 2000k -f rtsp {self.rtsp_output_url}"
        ffmpeg_cmd = f"ffmpeg -f image2pipe -r 1 -i - -c:v libx264 -pix_fmt yuv420p -color_range pc -f rtsp {self.rtsp_output_url}"
        p=subprocess.Popen(ffmpeg_cmd,shell=True,stdin=subprocess.PIPE)
        # 从队列中获取图像帧路径并推流
        fps = 1          # 视频帧率
        size = (640, 480) # 需要转为视频的图片的尺寸
        while True:
            image_path = Rtsp.compose_queue.get()
            frame = cv2.imread(image_path)
            if frame is not None:
                _, img_encode = cv2.imencode('.jpg', frame)
                data = img_encode.tobytes()
                p.stdin.write(data)
rtsp = Rtsp("rtsp://admin:passwd4sxt@172.16.0.200:554/h264/ch1/main/av_stream", "rtsp://172.16.0.135:8554/live_stream", "demo_input", "demo_output")
if __name__ == "__main__":
    # 创建并启动线程
    split_thread = threading.Thread(target=rtsp.split)
    add_file_thread = threading.Thread(target=rtsp.add_flie_to_queue)
    detect_thread0 = threading.Thread(target=rtsp.detect)
    detect_thread1 = threading.Thread(target=rtsp.detect)
    #compose_thread = threading.Thread(target=rtsp.compose)

    split_thread.start()
    add_file_thread.start()
    time.sleep(5)
    detect_thread0.start()
    detect_thread1.start()
    time.sleep(3)
    #compose_thread.start()
    # 等待所有线程结束
    split_thread.join()
    add_file_thread.join()
    detect_thread0.join()
    detect_thread1.join()
    #compose_thread.join()