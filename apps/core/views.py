import os
from django.shortcuts import render,redirect,reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponse
from .models import Video
from PIL import Image, ImageDraw
from moviepy.editor import VideoFileClip
from django.core.files.storage import FileSystemStorage,default_storage

from src import settings
import shutil

from .algs import integration,algo3

def get_video_dimensions(video_path):
    clip = VideoFileClip(video_path)
    width, height = clip.size  # 获取视频的宽度和高度
    return width, height

def video_upload(request):
    message = ''
    if request.method == 'POST':
        title = request.POST.get('title')
        videofile = request.FILES.get('videofile')
        # imagefile = request.FILES.get('imagefile')
        # 保存上传的文件
        video_fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'videos'))
        video_path = video_fs.path(videofile.name)
        # 如果文件已存在，先删除它
        if default_storage.exists(video_path):
            default_storage.delete(video_path)
        video_filename = video_fs.save(videofile.name, videofile)

        #默认存储图片
        # image_fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'images'))
        # image_path = image_fs.path('default.bmp')
        # # 如果文件已存在，先删除它
        # if default_storage.exists(image_path):
        #     default_storage.delete(image_path)
        # image_filename = image_fs.save(imagefile.name, imagefile)
        # marked_image_filename=image_filename.split('.')[0]+'.png'
        # print('viedo_path:{},image_path:{}'.format(video_path,image_path))
        # 获取视频尺寸
        video_width, video_height = get_video_dimensions(video_path)
        # # 获取图片尺寸
        # with Image.open(image_path) as img:
        #     image_width, image_height = img.size
        # # 检查尺寸是否一致
        # if video_width != image_width or video_height != image_height:
        #     # 尺寸不一致，返回错误
        #     return HttpResponse('Video and image dimensions do not match.')
        # 尺寸一致，保存 Video 对象
        video_filename = os.path.join('videos', video_filename)
        image_filename = os.path.join('images', 'default.bmp')
        marked_image_filename = os.path.join('images', 'default.bmp')
        # marked_image_filename = os.path.join('images', marked_image_filename)
        # print('video_filename:{},image_filename:{},marked_image_filename:{}'.format(video_filename, image_filename,marked_image_filename))
        video = Video(title=title, upload_videofile=video_filename, width=video_width, height=video_height,imagefile=image_filename,marked_imagefile=marked_image_filename)
        # video = Video(title=title, videofile=video_filename, width=video_width, height=video_height)
        video.save()
        message = '视频上传成功!'
        print(message)
        # return redirect('video_play', id=video.id,is_display=0)
        return render(request, 'video_upload.html', {'message': message,'video': video})
    else:
        return render(request, 'video_upload.html',{'message': message})

def video_play(request, id,is_display=0):
    print("video_play is called,id:{},is_display:{}".format(id,is_display))
    video=Video.objects.get(id=id)
    return render(request, 'video_play.html', {'video': video,'is_display':is_display})


def mark_points(points, image_path):
    # 打开图片
    # 打开文件
    with open(image_path, 'rb') as f:
        image = Image.open(f)
    # image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        # 遍历所有的点
        for point in points:
            x, y = point
            # 在图片上画一个小圆来标记这个点
            # draw.ellipse((x-5, y-5, x+5, y+5), fill='red')
            # 在图片上画一个十字来标记这个点
            draw.line((x - 3, y - 3, x + 3, y + 3), fill='red')
            draw.line((x - 3, y + 3, x + 3, y - 3), fill='red')
        # 保存图片
        save_image_path=image_path.split('.')[0]+'.png'
        image.save(save_image_path)
        print('save_image_path:',save_image_path)

# 存储所有的点的坐标，键为视频的id，值为标注点列表
points = {}
@csrf_exempt
def save_coordinates(request):
    print("save_coordinates is called")
    x = request.POST.get('x')
    y = request.POST.get('y')
    video_id = request.POST.get('video_id')
    print("Received coordinates: " + x + ", " + y+ ", " + video_id)
    # 根据视频ID获取视频对象
    video = Video.objects.get(id=video_id)
    # 获取视频文件的路径
    video_path = video.generate_videofile.path
    # 获取视频文件的目录和文件名（不包括扩展名）
    directory, filename = os.path.split(video_path)
    print("directory:{}, filename:{}".format(directory, filename))
    filename, _ = os.path.splitext(filename)
    # 构造图片的路径
    # image_path = os.path.join('/'.join(directory.split('/')[:-1]+['images']), filename + '.bmp')
    image_path= video.imagefile.path
    print("image_path:{}".format(image_path))
    # TODO: save the coordinates
    # 如果视频的id还没有在points中，就新建一个空列表
    if video_id not in points:
        points[video_id] = []
    # 把坐标添加到对应视频的列表中
    points[video_id].append((int(x), int(y)))
    # 标记点
    mark_points(points[video_id], image_path)
    return JsonResponse({'status': 'ok'})

@csrf_exempt
def clear_marks(request):
    print("clear_marks is called")
    video_id = request.POST.get('video_id')
    # 根据视频ID获取视频对象
    video = Video.objects.get(id=video_id)
    # 获取图片文件的路径
    image_path = video.imagefile.path
    # 获取标记的图片文件的路径
    marked_image_path = video.marked_imagefile.path
    # # 如果标记的图片文件存在，删除它
    # if os.path.exists(marked_image_path):
    #     os.remove(marked_image_path)
    # 将原始图片复制为标记的图片
    shutil.copyfile(image_path, marked_image_path)
    points[video_id] = []
    return JsonResponse({'status': 'ok'})


def video_mark(request, id):
    print("video_mark is called,id:{}".format(id))
    video = Video.objects.get(id=id)
    return render(request, 'video_mark.html', {'video': video})


def video_display(request, id):
    print("video_display is called,id:{}".format(id))
    video = Video.objects.get(id=id)
    return render(request, 'video_display.html', {'video': video})

#
# def video_displays(request, algo1_video_path,algo2_video_path,image_path):
#     print('video_display is called')
#     print('algo1_video_path:', algo1_video_path)
#     print('algo2_video_path:', algo2_video_path)
#     print('image_path:', image_path)
#     # return render(request,'video_display.html')
#     return render(request, 'video_display.html', {
#         'algo1_video_path': algo1_video_path,
#         'algo2_video_path': algo2_video_path,
#         'image_path': image_path,
#     })

def get_relative_path(absolute_path, base_path):
    return os.path.relpath(absolute_path, base_path)


# @csrf_exempt
# def generate_content(request):
#     if request.method == 'POST':
#         video_id = request.POST.get('video_id')
#         video = Video.objects.get(id=video_id)
#         video_path = video.videofile.path
#         print(video_path)
#         # 在这里调用你的算法生成内容的函数
#         algo1_video_path,algo2_video_path,algo1_image_path,algo2_image_path,image_path = integration(video_path)
#         # algo1_video_path,algo2_video_path,algo1_image_path,algo2_image_path,image_path='1','2','3','4','5'
#         print(algo1_video_path,algo2_video_path,algo1_image_path,algo2_image_path,image_path)
#         integration_image_relative_path = get_relative_path(image_path, settings.MEDIA_ROOT)
#         video.imagefile = integration_image_relative_path
#         video.save()
#
#         video_urls=[algo1_video_path,algo2_video_path]
#         images_urls=[algo1_image_path,algo2_image_path]
#         # video_urls = [get_relative_path(url, settings.MEDIA_ROOT) for url in video_urls]
#         generate_videos=[]
#         for video_path,image_path in zip(video_urls,images_urls):
#             # 创建一个新的Video对象
#             gen_video = Video()
#             # 获取视频文件的宽度和高度
#             clip = VideoFileClip(video_path)
#             gen_video.width = clip.size[0]
#             gen_video.height = clip.size[1]
#             video_relative_path=get_relative_path(video_path, settings.MEDIA_ROOT)
#             image_relative_path=get_relative_path(image_path, settings.MEDIA_ROOT)
#             # 设置你的视频属性
#             gen_video.title = video_relative_path.split('/')[-1].split('.')[0]
#             # 设置你的视频文件的路径
#             gen_video.videofile = video_relative_path
#             gen_video.imagefile = image_relative_path
#             generate_videos.append(gen_video)
#             # 保存你的Video对象
#             gen_video.save()
#         return render(request, 'video_display.html', {'generate_videos': [video]+generate_videos})
#
#     else:
#         return JsonResponse({'error': 'Invalid Method'})
#
#

@csrf_exempt
def generate_content(request):
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        video = Video.objects.get(id=video_id)
        # 在这里调用你的算法生成内容的函数
        # algo3_image_path,algo3_video_path=algo3(video)
        generate_pic_path, generate_video_path, transfer_video_path=algo3(video)
        print(generate_pic_path, generate_video_path, transfer_video_path)
        generate_pic_relative_path=get_relative_path(generate_pic_path, settings.MEDIA_ROOT)
        generate_video_relative_path=get_relative_path(generate_video_path, settings.MEDIA_ROOT)
        transfer_video_relative_path=get_relative_path(transfer_video_path, settings.MEDIA_ROOT)
        video.imagefile = generate_pic_relative_path
        video.marked_imagefile=generate_pic_relative_path.replace(".jpg",".png")
        video.generate_videofile = generate_video_relative_path
        video.transfer_videofile = transfer_video_relative_path
        # gen_video = Video()
        # # 获取视频文件的宽度和高度
        # clip = VideoFileClip(algo3_video_path)
        # gen_video.width = clip.size[0]
        # gen_video.height = clip.size[1]
        # # 设置你的视频属性
        # gen_video.title = algo3_video_relative_path.split('/')[-1].split('.')[0]
        # # 设置你的视频文件的路径
        # gen_video.videofile = algo3_video_relative_path
        # gen_video.imagefile = algo3_image_relative_path
        # gen_video.marked_imagefile = algo3_image_relative_path.replace(".jpg",".png")
        # gen_video.save()
        video.save()
        # print('gen_video:',gen_video.id,gen_video.title,gen_video.videofile,gen_video.imagefile,gen_video.marked_imagefile)
        # return redirect('video_mark', id=gen_video.id)
        return JsonResponse({'redirect_url': reverse('video_mark', args=[video.id])})
    else:
        return JsonResponse({'error': 'Invalid Method'})

