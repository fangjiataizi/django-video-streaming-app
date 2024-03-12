
# 需要在同一个目录下建一个叫test01的文件夹，下面有三个文件夹，分别是tmp1，tmp2和result
# tmp1, tmp2用于暂存处理中的图像，result用于存两个视频
# 图片结果需要建立一个叫integration的文件夹，下面有三个文件夹，分别是algo1，algo2和intg
# algo1和algo2分别用于存算法1、2的输出，intg用于存整合的后图像
# 网页的两个视频在test01/result/下，图片在integration/intg/下

import cv2
import numpy as np
import time
import glob
import matplotlib.pyplot as plt
import os
from src import settings
from moviepy.editor import VideoFileClip


def denoise(input_image):
    input_image = cv2.threshold(input_image, 254, 255, cv2.THRESH_BINARY)[1]
    input_image_comp = cv2.bitwise_not(input_image)  # could just use 255-img

    kernel1 = np.array([[0, 0, 0],
                        [0, 1, 0],
                        [0, 0, 0]], np.uint8)
    kernel2 = np.array([[1, 1, 1],
                        [1, 0, 1],
                        [1, 1, 1]], np.uint8)

    hitormiss1 = cv2.morphologyEx(input_image, cv2.MORPH_ERODE, kernel1)
    hitormiss2 = cv2.morphologyEx(input_image_comp, cv2.MORPH_ERODE, kernel2)
    hitormiss = cv2.bitwise_and(hitormiss1, hitormiss2)
    output_img = cv2.addWeighted(input_image, 1, hitormiss, -1, 0)
    return (output_img)

def algo1(vv,cal_dir):
    print(vv)
    files = glob.glob(cal_dir+'/test01/tmp1/*')
    for f in files:
        os.remove(f)
    files = glob.glob(cal_dir+'/test01/tmp2/*')
    for f in files:
        os.remove(f)
    files = glob.glob(cal_dir+'/test01/*.jpg')
    for f in files:
        os.remove(f)
    # v_path = "视频/{}".format(vv)
    v_path=vv
    cap = cv2.VideoCapture(v_path)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print("帧数:{}".format(frame_count))
    for i in range(int(frame_count)):
        _, img = cap.read(i)
        grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=int)
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=int)
        x = cv2.filter2D(grayImage, cv2.CV_16S, kernelx)
        y = cv2.filter2D(grayImage, cv2.CV_16S, kernely)
        absX = cv2.convertScaleAbs(x)
        absY = cv2.convertScaleAbs(y)
        Prewitt = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)
        algo1_image_path=cal_dir+"/tmp1/{:05d}.jpg".format(i)
        print(algo1_image_path)
        cv2.imwrite(algo1_image_path, Prewitt)
    img_array = []
    for i in range(int(frame_count)):
        algo1_image_path = cal_dir+"/tmp1/{:05d}.jpg".format(i)
        img = cv2.imread(algo1_image_path)
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)

    video_name=vv.split('/')[-1].split('.')[0]
    algo1_out_path=cal_dir+"/result/algo1_processed_{}.mp4".format(video_name)
    print("algo1_out_path:{}".format(algo1_out_path))
    out = cv2.VideoWriter(algo1_out_path, cv2.VideoWriter_fourcc(*'DIVX'), 10, size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
    # video_path = '../../media/test01/result/algo1_processed1.mp4'
    cap = cv2.VideoCapture(algo1_out_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    one_frame = np.zeros((height, width), dtype=np.uint8)
    two_frame = np.zeros((height, width), dtype=np.uint8)
    three_frame = np.zeros((height, width), dtype=np.uint8)
    for k in range(int(frame_count)):
        ret, frame = cap.read()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if not ret:
            break
        one_frame, two_frame, three_frame = two_frame, three_frame, frame_gray
        abs1 = cv2.absdiff(one_frame, two_frame)
        _, thresh1 = cv2.threshold(abs1, 15, 555, cv2.THRESH_BINARY)
        abs2 = cv2.absdiff(two_frame, three_frame)
        _, thresh2 = cv2.threshold(abs2, 15, 555, cv2.THRESH_BINARY)
        binary = cv2.bitwise_and(thresh1, thresh2)
        algo1_image_path2 = cal_dir + "/tmp2/{:05d}.jpg".format(k)
        cv2.imwrite(algo1_image_path2, binary)
        if cv2.waitKey(50) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()

    II = cv2.imread(cal_dir+"/tmp2/00001.jpg")
    for k in range(int(frame_count)):
        img = cv2.imread(cal_dir+"/tmp2/{:05d}.jpg".format(k))
        II = II + img
    cv2.imwrite(cal_dir+"/integration/algo1/algo1_processed_{}.jpg".format(video_name), II)
    return (II)

def algo2(vv,cal_dir):
    print(vv)
    files = glob.glob(cal_dir+'/tmp1/*')
    for f in files:
        os.remove(f)
    files = glob.glob(cal_dir+'/tmp2/*')
    for f in files:
        os.remove(f)
    files = glob.glob(cal_dir+'/*.jpg')
    for f in files:
        os.remove(f)

    # v_path = "视频/{}".format(vv)
    v_path=vv
    cap = cv2.VideoCapture(v_path)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print("帧数:{}".format(frame_count))

    for i in range(int(frame_count)):
        _, img = cap.read(i)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        image = img.copy()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gaussian_3 = cv2.GaussianBlur(image, (21, 21), cv2.BORDER_DEFAULT)
        img = cv2.addWeighted(image, 6, gaussian_3, -5.0, 0)
        fgamma = 2
        img = np.uint8(np.power((np.array(img) / 255.0), fgamma) * 255.0)
        img = cv2.normalize(img, img, 0, 255, cv2.NORM_MINMAX)
        img = cv2.convertScaleAbs(img, img)

        cv2.imwrite(cal_dir+"/{}.jpg".format(i), img)

    for i in range(int(frame_count)):
        img = cv2.imread(cal_dir+'/{}.jpg'.format(i))
        grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=int)
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=int)
        x = cv2.filter2D(grayImage, cv2.CV_16S, kernelx)
        y = cv2.filter2D(grayImage, cv2.CV_16S, kernely)
        absX = cv2.convertScaleAbs(x)
        absY = cv2.convertScaleAbs(y)
        Prewitt = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)

        cv2.imwrite(cal_dir+"/tmp1/{:05d}.jpg".format(i), Prewitt)

    img_array = []
    for i in range(int(frame_count)):
        filename = cal_dir+'/tmp1/{:05d}.jpg'.format(i)
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)
    video_name = vv.split('/')[-1].split('.')[0]
    algo2_out_path = cal_dir + "/result/algo2_processed_{}.mp4".format(video_name)
    print("algo2_out_path:{}".format(algo2_out_path))
    out = cv2.VideoWriter(algo2_out_path, cv2.VideoWriter_fourcc(*'DIVX'), 10, size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

    video_path = algo2_out_path
    cap = cv2.VideoCapture(video_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    one_frame = np.zeros((height, width), dtype=np.uint8)
    two_frame = np.zeros((height, width), dtype=np.uint8)
    three_frame = np.zeros((height, width), dtype=np.uint8)

    for k in range(int(frame_count)):
        ret, frame = cap.read()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if not ret:
            break
        one_frame, two_frame, three_frame = two_frame, three_frame, frame_gray
        abs1 = cv2.absdiff(one_frame, two_frame)
        _, thresh1 = cv2.threshold(abs1, 15, 555, cv2.THRESH_BINARY)
        abs2 = cv2.absdiff(two_frame, three_frame)
        _, thresh2 = cv2.threshold(abs2, 15, 555, cv2.THRESH_BINARY)
        binary = cv2.bitwise_and(thresh1, thresh2)
        cv2.imwrite(cal_dir+"/tmp2/{:05d}.jpg".format(k), binary)
        if cv2.waitKey(50) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()

    II = cv2.imread(cal_dir+"/tmp2/00001.jpg")
    for k in range(int(frame_count)):
        img = cv2.imread(cal_dir+"/tmp2/{:05d}.jpg".format(k))
        II = II + img
    cv2.imwrite(cal_dir+"/integration/algo2/algo2_processed_{}.jpg".format(video_name), II)
    return (II)

def integration(vv):
    cal_dir=os.path.join(settings.MEDIA_ROOT, 'test01')
    p1 = algo1(vv,cal_dir)
    p2 = algo2(vv,cal_dir)
    p1 = cv2.threshold(p1, 240, 255, cv2.THRESH_BINARY)[1]
    p2 = cv2.threshold(p2, 250, 255, cv2.THRESH_BINARY)[1]
    p3 = cv2.bitwise_or(p1, p2)
    p3 = denoise(p3)
    video_name = vv.split('/')[-1].split('.')[0]
    image_path=cal_dir+"/integration/intg/intg_{}.jpg".format(video_name)
    cv2.imwrite(image_path, p3)
    algo1_video_path=cal_dir+'/result/algo1_processed_{}.mp4'.format(video_name)
    algo1_image_path=cal_dir+"/integration/algo1/algo1_processed_{}.jpg".format(video_name)
    algo2_video_path = cal_dir + '/result/algo2_processed_{}.mp4'.format(video_name)
    algo2_image_path=cal_dir+"/integration/algo2/algo2_processed_{}.jpg".format(video_name)

    return algo1_video_path,algo2_video_path,algo1_image_path,algo2_image_path,image_path


def transfer_video_to_webm(v_path, cal_dir):
    # 创建一个VideoFileClip对象
    clip = VideoFileClip(v_path)

    # 定义输出视频的路径
    transfer_video_path = cal_dir + '/03_output/V_{}.webm'.format(v_path.split("/")[-1].split(".")[0])

    # 将clip写入文件
    clip.write_videofile(transfer_video_path, codec='libvpx')

    print('init video transfer to webm')
    return transfer_video_path

def transfer_video_to_mp4_moviepy(v_path, cal_dir):
    # 创建一个VideoFileClip对象
    clip = VideoFileClip(v_path)
    # 定义输出视频的路径
    transfer_video_path = cal_dir + '/03_output/V_{}.mp4'.format(v_path.split("/")[-1].split(".")[0])
    # 将clip写入文件
    # clip.write_videofile(transfer_video_path, codec='libx264')
    clip.write_videofile(transfer_video_path, codec='libvpx-vp9', ffmpeg_params=['-pix_fmt', 'yuv420p'])
    print('init video transfer to mp4')
    return transfer_video_path



def transfer_video_to_mp4(v_path,cal_dir):
    cap = cv2.VideoCapture(v_path)
    # 获取视频的宽度、高度和帧率
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    # 创建一个VideoWriter对象
    fourcc = cv2.VideoWriter_fourcc(*'X264')  # 或者使用'X264'
    transfer_video_path = cal_dir + '/03_output/V_{}.mp4'.format(v_path.split("/")[-1].split(".")[0])
    out = cv2.VideoWriter(transfer_video_path, fourcc, fps, (frame_width, frame_height))
    # 读取和写入每一帧
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
    # 释放资源
    cap.release()
    out.release()
    print('init video transfer to mp4')
    return transfer_video_path


def algo3(video):
    v_path= video.upload_videofile.path
    print("v_path:{}".format(v_path))
    cal_dir = os.path.join(settings.MEDIA_ROOT, 'test01/algo3')
    print("cal_dir:{}".format(cal_dir))
    transfer_video_path=transfer_video_to_mp4_moviepy(v_path,cal_dir)
    print("transfer_video_path:{}".format(transfer_video_path))

    files = glob.glob(cal_dir+'/02_intermediate/*')
    for f in files:
        os.remove(f)
    cap=cv2.VideoCapture(v_path)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    print(frame_count)

    img_array = []
    for i in range(int(frame_count)):
        _, img = cap.read(i)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        s = int(round(img.shape[0] / 600, 1) * 10)
        filterSize = (s, s)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, filterSize)
        tophat_img = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel)

        kernelx = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=int)
        kernely = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=int)
        x = cv2.filter2D(tophat_img, cv2.CV_16S, kernelx)
        y = cv2.filter2D(tophat_img, cv2.CV_16S, kernely)
        absX = cv2.convertScaleAbs(x)
        absY = cv2.convertScaleAbs(y)
        Prewitt = cv2.addWeighted(absX, 0.5, absY, 0.5, 0)

        img_array.append(cv2.cvtColor(Prewitt, cv2.COLOR_GRAY2BGR))

    size = (Prewitt.shape[1], Prewitt.shape[0])
    processed_file_path= cal_dir+'/03_output/V_{}_processed.avi'.format(v_path.split("/")[-1].split(".")[0])
    out = cv2.VideoWriter(processed_file_path, cv2.VideoWriter_fourcc(*'DIVX'), 10, size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

    generate_video_path = cal_dir + '/03_output/V_{}_processed.mp4'.format(v_path.split("/")[-1].split(".")[0])
    out=cv2.VideoWriter(generate_video_path, cv2.VideoWriter_fourcc(*'VP80'), 24, size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
    cap = cv2.VideoCapture(processed_file_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    one_frame = np.zeros((height, width), dtype=np.uint8)
    two_frame = np.zeros((height, width), dtype=np.uint8)
    three_frame = np.zeros((height, width), dtype=np.uint8)

    II = np.zeros((height, width, 3), dtype=np.uint8)

    for k in range(int(frame_count)):
        ret, frame = cap.read()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if not ret:
            break
        one_frame, two_frame, three_frame = two_frame, three_frame, frame_gray
        abs1 = cv2.absdiff(one_frame, two_frame)
        _, thresh1 = cv2.threshold(abs1, 15, 555, cv2.THRESH_BINARY)
        abs2 = cv2.absdiff(two_frame, three_frame)
        _, thresh2 = cv2.threshold(abs2, 15, 555, cv2.THRESH_BINARY)

        binary1 = cv2.bitwise_or(thresh1, thresh2)
        out_pic_path=cal_dir+"/02_intermediate/tt_{}.jpg".format(k)
        cv2.imwrite(out_pic_path, binary1)

    for k in range(int(frame_count)):
        read_pic_path = cal_dir + "/02_intermediate/tt_{}.jpg".format(k)
        II += cv2.imread(read_pic_path)

    generate_pic_path=cal_dir+"/03_output/P_{}.jpg".format(v_path.split("/")[-1].split(".")[0])
    cv2.imwrite(generate_pic_path, II)
    cap.release()
    cv2.destroyAllWindows()
    print("generate_pic_path:{}".format(generate_pic_path))
    return generate_pic_path,generate_video_path,transfer_video_path
