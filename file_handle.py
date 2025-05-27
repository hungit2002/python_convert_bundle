import os
import requests
import boto3
from zipfile import ZipFile
import subprocess
import shutil
import time
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def evaluate_process_time(start_time, end_time, step):
    time_taken = end_time - start_time
    logger.info("Step: " + step + f" - Time taken: {time_taken:.3f} seconds")

load_dotenv()

def noti_to_tele(message):
    token = os.getenv('TOKEN')
    chat_id = os.getenv('CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"

    requests.get(url)

def unzip_file_and_delete(file):
    step = "Unzip File"
    start = time.time()

    # filename: tên file không đuôi ".zip"
    filename = os.path.splitext(os.path.basename(file))[0]

    # Đường dẫn file zip
    zip_file = os.path.join(os.getenv('INPUT'), os.path.basename(file))

    # Đường dẫn thư mục đích
    dest_folder = os.path.join(os.getenv('INPUT'), filename)

    logger.info(step)

    logger.info(step)
    with ZipFile(zip_file, 'r') as zObject:
        zObject.extractall(path=dest_folder)
    # os.remove(zip_file)
    end = time.time()
    evaluate_process_time(start, end, step)

def build_asset_bundle():
    step = "Build Bundle"
    start = time.time()
    logger.info(step)

    #Build Bundle Only Win32
    #args = "/Applications/Unity/Hub/Editor/2022.1.20f1/Unity.app/Contents/MacOS/Unity -executeMethod CreateAssetBundles.BuildDataToBundlesWin -projectPath /Users/monkey/Documents/monkey/MonkeyXAssetBunldeBuilder/AssetBunldeBuilder -batchmode -quit"

    #Build Bundle Normal
    args = "/Applications/Unity/Hub/Editor/2022.1.20f1/Unity.app/Contents/MacOS/Unity -executeMethod CreateAssetBundles.BuildDataToBundles -projectPath /Users/monkey/Documents/monkey/MonkeyXAssetBunldeBuilder/AssetBunldeBuilder -batchmode -quit"

    #Build Bundle Coloring
    # args = "/Applications/Unity/Hub/Editor/2022.1.20f1/Unity.app/Contents/MacOS/Unity -executeMethod CreateAssetBundles.BuildColorRingToBundle -projectPath /Users/monkey/Documents/monkey/MonkeyXAssetBunldeBuilder/AssetBunldeBuilder -batchmode -quit"
    subprocess.call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    end = time.time()
    evaluate_process_time(start, end, step)

def build_asset_conversation_video():
    step = "Build Bundle Conversation Video"
    start = time.time()
    logger.info(step)

    #Build Bundle Normal
    args = "/Applications/Unity/Hub/Editor/2022.1.20f1/Unity.app/Contents/MacOS/Unity -executeMethod CreateAssetBundles.BuildDataToBundlesVideoCall -projectPath /Users/monkey/Documents/monkey/MonkeyXAssetBunldeBuilder/AssetBunldeBuilder -batchmode -quit"

    subprocess.call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    end = time.time()
    evaluate_process_time(start, end, step)

def build_asset_bundle_low_rez():
    step = "Build Bundle Low Res"
    start = time.time()
    logger.info(step)

    args = "/Applications/Unity/Hub/Editor/2022.1.20f1/Unity.app/Contents/MacOS/Unity -executeMethod CreateAssetBundles.BuildDataToBundlesLowRez -projectPath /Users/monkey/Documents/monkey/MonkeyXAssetBunldeBuilder/AssetBunldeBuilder -batchmode -quit"
    subprocess.call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    end = time.time()
    evaluate_process_time(start, end, step)

def build_asset_addressables():
    step = "Build Addressables"
    start = time.time()
    logger.info(step)

    args = "/Applications/Unity/Hub/Editor/2022.1.20f1/Unity.app/Contents/MacOS/Unity -executeMethod CreateAddressables.ExportBundles -projectPath /Users/monkey/Documents/monkey/MonkeyXAssetBunldeBuilder/AssetBunldeBuilder -batchmode -quit"
    subprocess.call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    end = time.time()
    evaluate_process_time(start, end, step)

class CustomException(Exception):
        def __init__(self, message):
            self.message = message

def upload_to_s3(file, bundle_type):
    step = "Upload Bundle"
    start = time.time()

    logger.info(step)
    bundle_file = os.path.basename(file)[:-4]
    ios_bundle = os.getenv('IOS_BUNDLE') + bundle_file + ".bundle"
    and_bundle = os.getenv('ANDROID_BUNDLE') + bundle_file + ".bundle"
    win32_bundle =  os.getenv('WIN32_BUNDLE') + bundle_file + ".bundle"
    s3 = boto3.client('s3',aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))

    match bundle_type:
        case "story":
            ios_s3_bundle = os.getenv('STORY_IOS_S3_PATH') + bundle_file + ".bundle"
            and_s3_bundle = os.getenv('STORY_AND_S3_PATH') + bundle_file + ".bundle"
            win32_s3_bundle = os.getenv('STORY_WIN32_S3_PATH') + bundle_file + ".bundle"
        case "word":
            ios_s3_bundle = os.getenv('WORD_IOS_S3_PATH') + bundle_file + ".bundle"
            and_s3_bundle = os.getenv('WORD_AND_S3_PATH') + bundle_file + ".bundle"
            win32_s3_bundle = os.getenv('WORD_WIN32_S3_PATH') + bundle_file + ".bundle"
        case "courseinstall":
            ios_s3_bundle = os.getenv('COURSEINSTALL_IOS_S3_PATH') + bundle_file + ".bundle"
            and_s3_bundle = os.getenv('COURSEINSTALL_AND_S3_PATH') + bundle_file + ".bundle"
            win32_s3_bundle = os.getenv('COURSEINSTALL_WIN32_S3_PATH') + bundle_file + ".bundle"

    try:
        s3.upload_file(Bucket=os.getenv('S3_BUCKET'), Key=ios_s3_bundle, Filename=ios_bundle)
        s3.upload_file(Bucket=os.getenv('S3_BUCKET'), Key=and_s3_bundle, Filename=and_bundle)
        s3.upload_file(Bucket=os.getenv('S3_BUCKET'), Key=win32_s3_bundle, Filename=win32_bundle)
        return ios_s3_bundle, and_s3_bundle, win32_s3_bundle
    except Exception as e:
        raise CustomException("\nCannot upload bundle to S3" + str(e))

    end = time.time()
    evaluate_process_time(start, end, step)

def upload_to_s3_2(file, upload_ios, upload_android, upload_win32):
    step = "Upload Bundle"
    start = time.time()

    logger.info(step)
    bundle_file = os.path.basename(file)[:-4]
    ios_bundle = os.getenv('IOS_BUNDLE') + bundle_file + ".bundle"
    and_bundle = os.getenv('ANDROID_BUNDLE') + bundle_file + ".bundle"
    win32_bundle = os.getenv('WIN32_BUNDLE') + bundle_file + ".bundle"
    s3 = boto3.client('s3',aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))

    ios_s3_bundle = upload_ios + bundle_file + ".bundle"
    and_s3_bundle = upload_android + bundle_file + ".bundle"
    win32_s3_bundle = upload_win32 + bundle_file + ".bundle"

    try:
        s3.upload_file(Bucket=os.getenv('S3_BUCKET'), Key=ios_s3_bundle, Filename=ios_bundle)
        s3.upload_file(Bucket=os.getenv('S3_BUCKET'), Key=and_s3_bundle, Filename=and_bundle)
        print("upload_win32", upload_win32)
        if(upload_win32 != ""):
            s3.upload_file(Bucket=os.getenv('S3_BUCKET'), Key=win32_s3_bundle, Filename=win32_bundle)

        end = time.time()
        evaluate_process_time(start, end, step)
        return ios_s3_bundle, and_s3_bundle, win32_s3_bundle
    except Exception as e:
        end = time.time()
        evaluate_process_time(start, end, step)
        raise CustomException("\nCannot upload bundle to S3" + str(e))

def update_api(file, bundle_type):

    step = "Update API"
    start = time.time()

    story_api = os.getenv('STORY_API')
    word_api = os.getenv('WORD_API')
    form = {
       "path_bundle": file
    }

    logger.info(step)
    match bundle_type:
        case "story":
            request = requests.put(story_api, data=form)
            if(request.status_code != 200):
                raise CustomException("Update APi " + request.text + "\n"+story_api)
        case "word":
            request = requests.put(word_api, data=form)
            if(request.status_code != 200):
                raise CustomException("Update APi " + request.text + "\n"+word_api)

    end = time.time()
    evaluate_process_time(start, end, step)



def count_file_in_queue():

    file_count = [0,0,0,0]

    src_story_folder = os.getenv('STORY_ZIP_PATH')
    src_word_folder = os.getenv('WORD_ZIP_PATH')
    src_lesson_folder = os.getenv('LESSON_ZIP_PATH')
    src_category_folder = os.getenv('CATEGORY_ZIP_PATH')
    src_courseinstall_folder = os.getenv('COURSEINSTALL_ZIP_PATH')
    src_item_folder = os.getenv('ITEM_ZIP_PATH')
    src_theme_folder = os.getenv('THEME_ZIP_PATH')
    src_award_folder = os.getenv('AWARD_ZIP_PATH')

    folders = []
    if src_story_folder:
        folders.append(src_story_folder)
        file_count['story'] = 0
    if src_word_folder:
        folders.append(src_word_folder)
        file_count['word'] = 0
    if src_lesson_folder:
        folders.append(src_lesson_folder)
        file_count['lesson'] = 0
    if src_category_folder:
        folders.append(src_category_folder)
        file_count['category'] = 0
    if src_courseinstall_folder:
        folders.append(src_courseinstall_folder)
        file_count['courseinstall'] = 0
    if src_item_folder:
        folders.append(src_item_folder)
        file_count['item'] = 0
    if src_theme_folder:
        folders.append(src_theme_folder)
        file_count['theme'] = 0
    if src_award_folder:
        folders.append(src_award_folder)
        file_count['award'] = 0
    # folders = [src_story_folder, src_word_folder, src_lesson_folder, src_courseinstall_folder]

    i = 0
    for folder in folders:

        if os.path.isdir(folder):
        # Get a list of all files in the directory
            file_list = os.listdir(folder)

            # Count the files
            file_count[i] = len(file_list)
            i += 1

    return file_count



def main_process(file_path, folderItem):
    try:
        done_message = "Done"
        fail_message = "Failed"
        start_time = time.time()
        file_name = os.path.basename(file_path)[:-4]
        bundle_type = folderItem['bundle_type']
        type = folderItem['type']

        noti_to_tele("Start convert: "+bundle_type+" - "+type+" - "+file_name)
        unzip_file_and_delete(file_path)

        #build
        if type == 'bundle':
            build_asset_bundle()
        elif type == 'low':
            build_asset_bundle_low_rez()
        elif type == 'addressable':
            build_asset_addressables()
        elif type == 'conversation':
            build_asset_conversation_video()

        ios_bundle = os.getenv('IOS_BUNDLE') + file_name + ".bundle"
        and_bundle = os.getenv('ANDROID_BUNDLE') + file_name + ".bundle"
        win32_bundle = os.getenv('WIN32_BUNDLE') + file_name + ".bundle"

        if os.path.isfile(ios_bundle) == False or os.path.isfile(and_bundle) == False or (os.path.isfile(win32_bundle) == False and type != "low"):
            noti_to_tele("Failed : " + file_name +" Error: build failed")
            return fail_message

        upload = upload_to_s3_2(file_path, folderItem['upload_ios'], folderItem['upload_android'], folderItem['upload_win32'])

        if bundle_type == "story" or bundle_type == "word":
            update_api(file_name, bundle_type)

        end_time = time.time()
        total_time_taken = end_time - start_time

        noti_to_tele("Successfully: "+bundle_type+" - "+type+" - "+file_name+f"\nBuild time: {total_time_taken:.1f} seconds")

        return done_message, total_time_taken, upload[0], upload[1]
    except CustomException as ce:
        noti_to_tele("Failed: " + file_name +" Error: "+ ce.message)
        return fail_message
    except Exception as e:
        noti_to_tele("Failed: " + file_name +" Error: "+ str(e))
        return fail_message
