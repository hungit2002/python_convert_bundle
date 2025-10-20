import os
import requests
import boto3
from zipfile import ZipFile
import subprocess
import shutil
import time
import logging
from dotenv import load_dotenv
import signal
from contextlib import contextmanager
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@contextmanager
def timeout(seconds):
    """Context manager để giới hạn thời gian chạy của một process
    
    Args:
        seconds: Số giây tối đa cho phép process chạy
    """
    def signal_handler(signum, frame):
        raise TimeoutError(f"Process timed out after {seconds} seconds")
        
    # Đăng ký signal handler
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Tắt alarm
        signal.alarm(0)

def evaluate_process_time(start_time, end_time, step):
    time_taken = end_time - start_time
    logger.info("Step: " + step + f" - Time taken: {time_taken:.3f} seconds")

load_dotenv()

# def noti_to_tele(message):
#     """Gửi thông báo qua Google Chat
#
#     Args:
#         message: Nội dung thông báo cần gửi
#     """
#     url = "https://chat.googleapis.com/v1/spaces/AAQA_FBcFx0/messages"
#     params = {
#         "key": "AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI",
#         "token": "7kUvaRguXgkgO_V7q7hvH8uE5oJuqEhsKhLU0Dpk2gU"
#     }
#     headers = {
#         "Content-Type": "application/json"
#     }
#     data = {
#         "text": message
#     }
#
#     try:
#         response = requests.post(url, params=params, headers=headers, json=data)
#         if response.status_code != 200:
#             logger.error(f"Failed to send notification to Google Chat: {response.text}")
#     except Exception as e:
#         logger.error(f"Error sending notification to Google Chat: {str(e)}")

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
    with ZipFile(zip_file, 'r') as zObject:
        zObject.extractall(path=dest_folder)
    os.remove(zip_file)
    end = time.time()
    evaluate_process_time(start, end, step)

def build_asset_bundle():
    step = "Build Bundle"
    start = time.time()
    logger.info(step)

    args = "/Applications/Unity/Hub/Editor/2022.1.20f1/Unity.app/Contents/MacOS/Unity -executeMethod CreateAssetBundles.BuildDataToBundles -projectPath /Users/monkey/Documents/monkey/MonkeyXAssetBunldeBuilder/AssetBunldeBuilder -batchmode -quit"

    try:
        # Sử dụng Popen thay vì call để không block process chính
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True,
            bufsize=1  # Line buffered
        )
        
        # Đọc output theo dòng để tránh buffer đầy
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logger.debug(f"Unity output: {output.strip()}")
                
        # Kiểm tra return code
        returncode = process.poll()
        if returncode != 0:
            error = process.stderr.read()
            logger.error(f"Unity Editor failed with return code {returncode}")
            logger.error(f"Error output: {error}")
            return False
            
        logger.info("Build Bundle Done")
        end = time.time()
        evaluate_process_time(start, end, step)
        return True
        
    except Exception as e:
        logger.error(f"Error running Unity Editor: {str(e)}")
        if process:
            process.kill()
        return False

def build_asset_conversation_video():
    step = "Build Bundle Conversation Video"
    start = time.time()
    logger.info(step)

    args = "/Applications/Unity/Hub/Editor/2022.1.20f1/Unity.app/Contents/MacOS/Unity -executeMethod CreateAssetBundles.BuildDataToBundlesVideoCall -projectPath /Users/monkey/Documents/monkey/MonkeyXAssetBunldeBuilder/AssetBunldeBuilder -batchmode -quit"

    try:
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True,
            bufsize=1
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logger.debug(f"Unity output: {output.strip()}")
                
        returncode = process.poll()
        if returncode != 0:
            error = process.stderr.read()
            logger.error(f"Unity Editor failed with return code {returncode}")
            logger.error(f"Error output: {error}")
            return False
            
        end = time.time()
        evaluate_process_time(start, end, step)
        return True
        
    except Exception as e:
        logger.error(f"Error running Unity Editor: {str(e)}")
        if process:
            process.kill()
        return False

def build_asset_bundle_low_rez():
    step = "Build Bundle Low Res"
    start = time.time()
    logger.info(step)

    args = "/Applications/Unity/Hub/Editor/2022.1.20f1/Unity.app/Contents/MacOS/Unity -executeMethod CreateAssetBundles.BuildDataToBundlesLowRez -projectPath /Users/monkey/Documents/monkey/MonkeyXAssetBunldeBuilder/AssetBunldeBuilder -batchmode -quit"

    try:
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True,
            bufsize=1
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logger.debug(f"Unity output: {output.strip()}")
                
        returncode = process.poll()
        if returncode != 0:
            error = process.stderr.read()
            logger.error(f"Unity Editor failed with return code {returncode}")
            logger.error(f"Error output: {error}")
            return False
            
        end = time.time()
        evaluate_process_time(start, end, step)
        return True
        
    except Exception as e:
        logger.error(f"Error running Unity Editor: {str(e)}")
        if process:
            process.kill()
        return False

def build_asset_addressables():
    step = "Build Addressables"
    start = time.time()
    logger.info(step)

    args = "/Applications/Unity/Hub/Editor/2022.1.20f1/Unity.app/Contents/MacOS/Unity -executeMethod CreateAddressables.ExportBundles -projectPath /Users/monkey/Documents/monkey/MonkeyXAssetBunldeBuilder/AssetBunldeBuilder -batchmode -quit"

    try:
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True,
            bufsize=1
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logger.debug(f"Unity output: {output.strip()}")
                
        returncode = process.poll()
        if returncode != 0:
            error = process.stderr.read()
            logger.error(f"Unity Editor failed with return code {returncode}")
            logger.error(f"Error output: {error}")
            return False
            
        end = time.time()
        evaluate_process_time(start, end, step)
        return True
        
    except Exception as e:
        logger.error(f"Error running Unity Editor: {str(e)}")
        if process:
            process.kill()
        return False

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
        success = False
        if type == 'bundle':
            success = build_asset_bundle_with_timeout()
        elif type == 'low':
            success = build_asset_bundle_low_rez_with_timeout()
        elif type == 'addressable':
            success = build_asset_addressables_with_timeout()
        elif type == 'conversation':
            success = build_asset_conversation_video_with_timeout()

        if not success:
            noti_to_tele("Failed : " + file_name +" Error: build failed")
            return fail_message

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

def build_asset_bundle_with_timeout(timeout_seconds=600):  # Default 10 minutes timeout
    """Build Unity bundle với timeout
    
    Args:
        timeout_seconds: Số giây tối đa cho phép build
        
    Returns:
        bool: True nếu build thành công, False nếu thất bại
    """
    try:
        with timeout(timeout_seconds):
            return build_asset_bundle()
    except TimeoutError as e:
        logger.error(f"Build timed out after {timeout_seconds} seconds: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during build: {str(e)}")
        return False

def build_asset_conversation_video_with_timeout(timeout_seconds=3600):
    try:
        with timeout(timeout_seconds):
            return build_asset_conversation_video()
    except TimeoutError as e:
        logger.error(f"Build timed out after {timeout_seconds} seconds: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during build: {str(e)}")
        return False

def build_asset_bundle_low_rez_with_timeout(timeout_seconds=3600):
    try:
        with timeout(timeout_seconds):
            return build_asset_bundle_low_rez()
    except TimeoutError as e:
        logger.error(f"Build timed out after {timeout_seconds} seconds: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during build: {str(e)}")
        return False

def build_asset_addressables_with_timeout(timeout_seconds=3600):
    try:
        with timeout(timeout_seconds):
            return build_asset_addressables()
    except TimeoutError as e:
        logger.error(f"Build timed out after {timeout_seconds} seconds: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during build: {str(e)}")
        return False
