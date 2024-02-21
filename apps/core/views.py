import os
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponse
from .models import Video
from PIL import Image, ImageDraw
from moviepy.editor import VideoFileClip
from django.core.files.storage import FileSystemStorage

from src import settings


def get_video_dimensions(video_path):
    clip = VideoFileClip(video_path)
    width, height = clip.size  # 获取视频的宽度和高度
    return width, height

def video_upload(request):
    message = ''
    if request.method == 'POST':
        title = request.POST.get('title')
        videofile = request.FILES.get('videofile')
        imagefile = request.FILES.get('imagefile')
        # 保存上传的文件
        video_fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'videos'))
        video_filename = video_fs.save(videofile.name, videofile)

        image_fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'images'))
        image_filename = image_fs.save(imagefile.name, imagefile)
        marked_image_filename=image_filename.split('.')[0]+'.png'

        video_path = video_fs.path(video_filename)
        image_path = image_fs.path(image_filename)
        print('viedo_path:{},image_path:{}'.format(video_path,image_path))
        # 获取视频尺寸
        video_width, video_height = get_video_dimensions(video_path)
        # 获取图片尺寸
        with Image.open(image_path) as img:
            image_width, image_height = img.size
        # 检查尺寸是否一致
        if video_width != image_width or video_height != image_height:
            # 尺寸不一致，返回错误
            return HttpResponse('Video and image dimensions do not match.')
        # 尺寸一致，保存 Video 对象
        video_filename = os.path.join('videos', video_filename)
        image_filename = os.path.join('images', image_filename)
        marked_image_filename = os.path.join('images', marked_image_filename)
        print('video_filename:{},image_filename:{},marked_image_filename:{}'.format(video_filename, image_filename,marked_image_filename))
        video = Video(title=title, videofile=video_filename, width=video_width, height=video_height,imagefile=image_filename,marked_imagefile=marked_image_filename)
        video.save()
        message = 'Video uploaded successfully!'
        print(message)
        return redirect('video_play', id=video.id)
    else:
        return render(request, 'video_upload.html',{'message': message})

def video_play(request, id):
    video = Video.objects.get(id=id)
    return render(request, 'video_play.html', {'video': video})




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
            draw.ellipse((x-5, y-5, x+5, y+5), fill='red')
        # 保存图片
        save_image_path=image_path.split('.')[0]+'.png'
        image.save(save_image_path)


# 存储所有的点的坐标，键为视频的id，值为标注点列表
points = {}

@csrf_exempt
def save_coordinates(request):
    x = request.POST.get('x')
    y = request.POST.get('y')
    video_id = request.POST.get('video_id')
    print("Received coordinates: " + x + ", " + y+ ", " + video_id)
    # 根据视频ID获取视频对象
    video = Video.objects.get(id=video_id)
    # 获取视频文件的路径
    video_path = video.videofile.path
    # 获取视频文件的目录和文件名（不包括扩展名）
    directory, filename = os.path.split(video_path)
    print("directory:{}, filename:{}".format(directory, filename))
    filename, _ = os.path.splitext(filename)
    # 构造图片的路径
    image_path = os.path.join('/'.join(directory.split('/')[:-1]+['images']), filename + '.bmp')
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
