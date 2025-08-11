from file_handle import main_process
from file_handle import CustomException
import os
import time
import logging
import csv
import shutil
import dotenv
import subprocess
from file_handle import evaluate_process_time
from datetime import datetime
import redis
from write_result import insert_result_to_es
from file_handle import noti_to_tele

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

redis_client = redis.StrictRedis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))

def check_process(file_path):
    file_name = os.path.basename(file_path)
    status = redis_client.get(file_name)
    if status:
        return status
    else:
        return None
    

def cache_process_status(file_path, status):
    file_name = os.path.basename(file_path)
    redis_client.set(file_name, status)

def delete_cache(file_path):
    file_name = os.path.basename(file_path)
    redis_client.delete(file_name)

def remove_folder():

    step = "Clean"
    start = time.time()
    input_folder = os.getenv('INPUT')
    output_folder = os.getenv('OUTPUT')
    folders = [input_folder, output_folder]

    logger.info(step)
    for folder in folders:
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)
    end = time.time()
    evaluate_process_time(start, end, step)

def get_list_folders_source():
    #bundle
    src_story_folder = os.getenv('STORY_ZIP_PATH')
    src_word_folder = os.getenv('WORD_ZIP_PATH')
    src_lesson_folder = os.getenv('LESSON_ZIP_PATH')
    src_category_folder = os.getenv('CATEGORY_ZIP_PATH')
    src_courseinstall_folder = os.getenv('COURSEINSTALL_ZIP_PATH')
    src_item_folder = os.getenv('ITEM_ZIP_PATH')
    src_theme_folder = os.getenv('THEME_ZIP_PATH')
    src_award_folder = os.getenv('AWARD_ZIP_PATH')
    src_conversation_folder = os.getenv('CONVERSATION')

    #upload_ios
    src_story_upload_ios = os.getenv('STORY_IOS_S3_PATH')
    src_word_upload_ios = os.getenv('WORD_IOS_S3_PATH')
    src_lesson_upload_ios = os.getenv('LESSON_IOS_S3_PATH')
    src_category_upload_ios = os.getenv('CATEGORY_IOS_S3_PATH')
    src_courseinstall_upload_ios = os.getenv('COURSEINSTALL_IOS_S3_PATH')
    src_item_upload_ios = os.getenv('ITEM_IOS_S3_PATH')
    src_theme_upload_ios = os.getenv('THEME_IOS_S3_PATH')
    src_award_upload_ios = os.getenv('AWARD_IOS_S3_PATH')
    src_conversation_upload_ios = os.getenv('CONVERSATION_IOS_S3_PATH')

    #upload_android
    src_story_upload_android = os.getenv('STORY_AND_S3_PATH')
    src_word_upload_android = os.getenv('WORD_AND_S3_PATH')
    src_lesson_upload_android = os.getenv('LESSON_AND_S3_PATH')
    src_category_upload_android = os.getenv('CATEGORY_AND_S3_PATH')
    src_courseinstall_upload_android = os.getenv('COURSEINSTALL_AND_S3_PATH')
    src_item_upload_android = os.getenv('ITEM_AND_S3_PATH')
    src_theme_upload_android = os.getenv('THEME_AND_S3_PATH')
    src_award_upload_android = os.getenv('AWARD_AND_S3_PATH')
    src_conversation_upload_android = os.getenv('CONVERSATION_AND_S3_PATH')

    #upload_win32
    src_story_upload_win32 = os.getenv('STORY_WIN32_S3_PATH')
    src_word_upload_win32 = os.getenv('WORD_WIN32_S3_PATH')
    src_lesson_upload_win32 = os.getenv('LESSON_WIN32_S3_PATH')
    src_category_upload_win32 = os.getenv('CATEGORY_WIN32_S3_PATH')
    src_courseinstall_upload_win32 = os.getenv('COURSEINSTALL_WIN32_S3_PATH')
    src_item_upload_win32 = os.getenv('ITEM_WIN32_S3_PATH')
    src_theme_upload_win32 = os.getenv('THEME_WIN32_S3_PATH')
    src_award_upload_win32 = os.getenv('AWARD_WIN32_S3_PATH')
    src_conversation_upload_win32 = os.getenv('CONVERSATION_WIN32_S3_PATH')

    #low
    src_story_low_folder = os.getenv('STORY_LOW_ZIP_PATH')
    src_word_low_folder = os.getenv('WORD_LOW_ZIP_PATH')
    src_lesson_low_folder = os.getenv('LESSON_LOW_ZIP_PATH')
    src_category_low_folder = os.getenv('CATEGORY_LOW_ZIP_PATH')
    src_courseinstall_low_folder = os.getenv('COURSEINSTALL_LOW_ZIP_PATH')
    src_item_low_folder = os.getenv('ITEM_LOW_ZIP_PATH')
    src_theme_low_folder = os.getenv('THEME_LOW_ZIP_PATH')
    src_award_low_folder = os.getenv('AWARD_LOW_ZIP_PATH')
    #low_upload_ios
    src_story_low_upload_ios = os.getenv('STORY_LOW_IOS_S3_PATH')
    src_word_low_upload_ios = os.getenv('WORD_LOW_IOS_S3_PATH')
    src_lesson_low_upload_ios = os.getenv('LESSON_LOW_IOS_S3_PATH')
    src_category_low_upload_ios = os.getenv('CATEGORY_LOW_IOS_S3_PATH')
    src_courseinstall_low_upload_ios = os.getenv('COURSEINSTALL_LOW_IOS_S3_PATH')
    src_item_low_upload_ios = os.getenv('ITEM_LOW_IOS_S3_PATH')
    src_theme_low_upload_ios = os.getenv('THEME_LOW_IOS_S3_PATH')
    src_award_low_upload_ios = os.getenv('AWARD_LOW_IOS_S3_PATH')
    #low_upload_android
    src_story_low_upload_android = os.getenv('STORY_LOW_AND_S3_PATH')
    src_word_low_upload_android = os.getenv('WORD_LOW_AND_S3_PATH')
    src_lesson_low_upload_android = os.getenv('LESSON_LOW_AND_S3_PATH')
    src_category_low_upload_android = os.getenv('CATEGORY_LOW_AND_S3_PATH')
    src_courseinstall_low_upload_android = os.getenv('COURSEINSTALL_LOW_AND_S3_PATH')
    src_item_low_upload_android = os.getenv('ITEM_LOW_AND_S3_PATH')
    src_theme_low_upload_android = os.getenv('THEME_LOW_AND_S3_PATH')
    src_award_low_upload_android = os.getenv('AWARD_LOW_AND_S3_PATH')
    #addressable
    src_story_addressable_folder = os.getenv('STORY_ADDRESSABLE_ZIP_PATH')
    src_word_addressable_folder = os.getenv('WORD_ADDRESSABLE_ZIP_PATH')
    src_lesson_addressable_folder = os.getenv('LESSON_ADDRESSABLE_ZIP_PATH')
    src_category_addressable_folder = os.getenv('CATEGORY_ADDRESSABLE_ZIP_PATH')
    src_courseinstall_addressable_folder = os.getenv('COURSEINSTALL_ADDRESSABLE_ZIP_PATH')
    src_item_addressable_folder = os.getenv('ITEM_ADDRESSABLE_ZIP_PATH')
    src_theme_addressable_folder = os.getenv('THEME_ADDRESSABLE_ZIP_PATH')
    src_award_addressable_folder = os.getenv('AWARD_ADDRESSABLE_ZIP_PATH')
    #addressable_upload_ios
    src_story_addressable_upload_ios = os.getenv('STORY_ADDRESSABLE_IOS_S3_PATH')
    src_word_addressable_upload_ios = os.getenv('WORD_ADDRESSABLE_IOS_S3_PATH')
    src_lesson_addressable_upload_ios = os.getenv('LESSON_ADDRESSABLE_IOS_S3_PATH')
    src_category_addressable_upload_ios = os.getenv('CATEGORY_ADDRESSABLE_IOS_S3_PATH')
    src_courseinstall_addressable_upload_ios = os.getenv('COURSEINSTALL_ADDRESSABLE_IOS_S3_PATH')
    src_item_addressable_upload_ios = os.getenv('ITEM_ADDRESSABLE_IOS_S3_PATH')
    src_theme_addressable_upload_ios = os.getenv('THEME_ADDRESSABLE_IOS_S3_PATH')
    src_award_addressable_upload_ios = os.getenv('AWARD_ADDRESSABLE_IOS_S3_PATH')
    #addressable_upload_android
    src_story_addressable_upload_android = os.getenv('STORY_ADDRESSABLE_AND_S3_PATH')
    src_word_addressable_upload_android = os.getenv('WORD_ADDRESSABLE_AND_S3_PATH')
    src_lesson_addressable_upload_android = os.getenv('LESSON_ADDRESSABLE_AND_S3_PATH')
    src_category_addressable_upload_android = os.getenv('CATEGORY_ADDRESSABLE_AND_S3_PATH')
    src_courseinstall_addressable_upload_android = os.getenv('COURSEINSTALL_ADDRESSABLE_AND_S3_PATH')
    src_item_addressable_upload_android = os.getenv('ITEM_ADDRESSABLE_AND_S3_PATH')
    src_theme_addressable_upload_android = os.getenv('THEME_ADDRESSABLE_AND_S3_PATH')
    src_award_addressable_upload_android = os.getenv('AWARD_ADDRESSABLE_AND_S3_PATH')

    folders = {}
    if src_story_folder:
        folders['story'] = {
            'folder': src_story_folder,
            'bundle_type': 'story',
            'type' : 'bundle',
            'upload_ios': src_story_upload_ios,
            'upload_android': src_story_upload_android,
            'upload_win32': src_story_upload_win32,
            'count': 0
        }
    if src_word_folder:
        folders['word'] = {
            'folder': src_word_folder,
            'bundle_type': 'word',
            'type' : 'bundle',
            'upload_ios': src_word_upload_ios,
            'upload_android': src_word_upload_android,
            'upload_win32': src_word_upload_win32,
            'count': 0
        }
    if src_lesson_folder:
        folders['lesson'] = {
            'folder': src_lesson_folder,
            'bundle_type': 'lesson',
            'type' : 'bundle',
            'upload_ios': src_lesson_upload_ios,
            'upload_android': src_lesson_upload_android,
            'upload_win32': src_lesson_upload_win32,
            'count': 0
        }
    if src_category_folder:
        folders['category'] = {
            'folder': src_category_folder,
            'bundle_type': 'category',
            'type' : 'bundle',
            'upload_ios': src_category_upload_ios,
            'upload_android': src_category_upload_android,
            'upload_win32': src_category_upload_win32,
            'count': 0
        }
    if src_courseinstall_folder:
        folders['courseinstall'] = {
            'folder': src_courseinstall_folder,
            'bundle_type': 'courseinstall',
            'type' : 'bundle',
            'upload_ios': src_courseinstall_upload_ios,
            'upload_android': src_courseinstall_upload_android,
            'upload_win32': src_courseinstall_upload_win32,
            'count': 0
        }
    if src_item_folder:
        folders['item'] = {
            'folder': src_item_folder,
            'bundle_type': 'item',
            'type' : 'bundle',
            'upload_ios': src_item_upload_ios,
            'upload_android': src_item_upload_android,
            'upload_win32': src_item_upload_win32,
            'count': 0
        }
    if src_theme_folder:
        folders['theme'] = {
            'folder': src_theme_folder,
            'bundle_type': 'theme',
            'type' : 'bundle',
            'upload_ios': src_theme_upload_ios,
            'upload_android': src_theme_upload_android,
            'upload_win32': src_theme_upload_win32,
            'count': 0
        }
    if src_award_folder:
        folders['award'] = {
            'folder': src_award_folder,
            'bundle_type': 'award',
            'type' : 'bundle',
            'upload_ios': src_award_upload_ios,
            'upload_android': src_award_upload_android,
            'upload_win32': src_award_upload_win32,
            'count': 0
        } 
    if src_conversation_folder:
        folders['conversation'] = {
            'folder': src_conversation_folder,
            'bundle_type': 'conversation',
            'type' : 'conversation',
            'upload_ios': src_conversation_upload_ios,
            'upload_android': src_conversation_upload_android,
            'upload_win32': src_conversation_upload_win32,
            'count': 0
        }     
    if src_story_low_folder:
        folders['story_low'] = {
            'folder': src_story_low_folder,
            'bundle_type': 'story',
            'type' : 'low',
            'upload_ios': src_story_low_upload_ios,
            'upload_android': src_story_low_upload_android,
            'upload_win32': '',
            'count': 0
        }
    if src_word_low_folder:
        folders['word_low'] = {
            'folder': src_word_low_folder,
            'bundle_type': 'word',
            'type' : 'low',
            'upload_ios': src_word_low_upload_ios,
            'upload_android': src_word_low_upload_android,
            'upload_win32': '',
            'count': 0
        }
    if src_lesson_low_folder:
        folders['lesson_low'] = {
            'folder': src_lesson_low_folder,
            'bundle_type': 'lesson',
            'type' : 'low',
            'upload_ios': src_lesson_low_upload_ios,
            'upload_android': src_lesson_low_upload_android,
            'upload_win32': '',
            'count': 0
        }
    if src_category_low_folder:
        folders['category_low'] = {
            'folder': src_category_low_folder,
            'bundle_type': 'category',
            'type' : 'low',
            'upload_ios': src_category_low_upload_ios,
            'upload_android': src_category_low_upload_android,
            'upload_win32': '',
            'count': 0
        }
    if src_courseinstall_low_folder:
        folders['courseinstall_low'] = {
            'folder': src_courseinstall_low_folder,
            'bundle_type': 'courseinstall',
            'type' : 'low',
            'upload_ios': src_courseinstall_low_upload_ios,
            'upload_android': src_courseinstall_low_upload_android,
            'upload_win32': '',
            'count': 0
        }
    if src_item_low_folder:
        folders['item_low'] = {
            'folder': src_item_low_folder,
            'bundle_type': 'item',
            'type' : 'low',
            'upload_ios': src_item_low_upload_ios,
            'upload_android': src_item_low_upload_android,
            'upload_win32': '',
            'count': 0
        }
    if src_theme_low_folder:
        folders['theme_low'] = {
            'folder': src_theme_low_folder,
            'bundle_type': 'theme',
            'type' : 'low',
            'upload_ios': src_theme_low_upload_ios,
            'upload_android': src_theme_low_upload_android,
            'upload_win32': '',
            'count': 0
        }
    if src_award_low_folder:
        folders['award_low'] = {
            'folder': src_award_low_folder,
            'bundle_type': 'award',
            'type' : 'low',
            'upload_ios': src_award_low_upload_ios,
            'upload_android': src_award_low_upload_android,
            'upload_win32': '',
            'count': 0
        } 
    if src_story_addressable_folder:
        folders['story_addressable'] = {
            'folder': src_story_addressable_folder,
            'bundle_type': 'story',
            'type' : 'addressable',
            'upload_ios': src_story_addressable_upload_ios,
            'upload_android': src_story_addressable_upload_android,
            'count': 0
        }
    if src_word_addressable_folder:
        folders['word_addressable'] = {
            'folder': src_word_addressable_folder,
            'bundle_type': 'word',
            'type' : 'addressable',
            'upload_ios': src_word_addressable_upload_ios,
            'upload_android': src_word_addressable_upload_android,
            'count': 0
        }
    if src_lesson_addressable_folder:
        folders['lesson_addressable'] = {
            'folder': src_lesson_addressable_folder,
            'bundle_type': 'lesson',
            'type' : 'addressable',
            'upload_ios': src_lesson_addressable_upload_ios,
            'upload_android': src_lesson_addressable_upload_android,
            'count': 0
        }
    if src_category_addressable_folder:
        folders['category_addressable'] = {
            'folder': src_category_addressable_folder,
            'bundle_type': 'category',
            'type' : 'addressable',
            'upload_ios': src_category_addressable_upload_ios,
            'upload_android': src_category_addressable_upload_android,
            'count': 0
        }
    if src_courseinstall_addressable_folder:
        folders['courseinstall_addressable'] = {
            'folder': src_courseinstall_addressable_folder,
            'bundle_type': 'courseinstall',
            'type' : 'addressable',
            'upload_ios': src_courseinstall_addressable_upload_ios,
            'upload_android': src_courseinstall_addressable_upload_android,
            'count': 0
        }
    if src_item_addressable_folder:
        folders['item_addressable'] = {
            'folder': src_item_addressable_folder,
            'bundle_type': 'item',
            'type' : 'addressable',
            'upload_ios': src_item_addressable_upload_ios,
            'upload_android': src_item_addressable_upload_android,
            'count': 0
        }
    if src_theme_addressable_folder:
        folders['theme_addressable'] = {
            'folder': src_theme_addressable_folder,
            'bundle_type': 'theme',
            'type' : 'addressable',
            'upload_ios': src_theme_addressable_upload_ios,
            'upload_android': src_theme_addressable_upload_android,
            'count': 0
        }
    if src_award_addressable_folder:
        folders['award_addressable'] = {
            'folder': src_award_addressable_folder,
            'bundle_type': 'award',
            'type' : 'addressable',
            'upload_ios': src_award_addressable_upload_ios,
            'upload_android': src_award_addressable_upload_android,
            'count': 0
        } 
        
    return folders

def count_file(folders):

    step = "Count File"
    start = time.time()
    message_count_file = ''

    logger.info(step)
    for keyItem, folderItem in folders.items():
        folder = folderItem['folder']
        if  os.path.exists(folder) and os.path.isdir(folder):
            # Get a list of all files in the directory
            file_list = os.listdir(folder)
            # Count the files 
            folders[keyItem]['count'] = len(file_list)
            message_count_file = message_count_file + str(keyItem) + ": " + str(len(file_list)) + ", "
    
    noti_to_tele(message_count_file)
    end = time.time()
    evaluate_process_time(start, end, step)

def get_file_in_folders(folders):

    step = "Get Zip File"
    start = time.time()
    logger.info(step)
    for keyItem, folderItem in folders.items():
        folder = folderItem['folder']
        bundle_type = folderItem['bundle_type']
        if os.path.exists(folder) and os.path.isdir(folder):
            for root, _, files in os.walk(folder):
                for file_name in files:
                    file_path = os.path.join(root, file_name)

                    if check_process(file_path):
                        continue
                    else:
                        cache_process_status(file_path, "Processing")
                        end = time.time()
                        evaluate_process_time(start, end, step)
                        return file_path, folderItem
                
    end = time.time()
    evaluate_process_time(start, end, step)
    return None
    
def copy_zip_file(file_path):

    step = "Copy zip to Input"
    start = time.time()

    logger.info(step)
    if file_path:
        try:
            shutil.copy(file_path, os.getenv('INPUT'))
        except Exception as e:
            print(f"Error: {e}")
    end = time.time()
    evaluate_process_time(start, end, step)

def delete_zip_file(file_path):

    step = "Delete Zip file"
    start = time.time()

    logger.info(step)

    try:
        os.remove(file_path)
    except FileNotFoundError:
        print(f"The file '{file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred while trying to delete the file: {e}")
    end = time.time()
    evaluate_process_time(start, end, step)

def move_file_to_dead_letter(file_path, bundle_type):
    """Di chuyển file thất bại vào thư mục dead letter
    
    Args:
        file_path: Đường dẫn file cần di chuyển
        bundle_type: Loại bundle
    """
    step = "Move zip to Dead Letter"
    start = time.time()

    logger.info(step)
    logger.info(f"Moving file: {file_path}")
    
    try:
        # Tạo thư mục dead letter nếu chưa tồn tại
        dead_letter_dir = os.path.join(os.getenv('DL_PATH'), bundle_type)
        os.makedirs(dead_letter_dir, exist_ok=True)
        
        # Lấy tên file
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(dead_letter_dir, file_name)
        
        # Di chuyển file
        shutil.move(file_path, dest_path)
        logger.info(f"Successfully moved file to: {dest_path}")
        
    except FileNotFoundError:
        logger.error(f"Source file not found: {file_path}")
    except Exception as e:
        logger.error(f"Error moving file: {str(e)}")
    finally:
        end = time.time()
        evaluate_process_time(start, end, step)

max_retry = 3

def single_process():
    count_retry = 1
    process = "True"

    folders = get_list_folders_source()
    try:
        while process:
            remove_folder()

            f = get_file_in_folders(folders)
            file_path = f[0]
            folderItem = f[1]
            count_file(folders)

            copy_zip_file(f[0])

            p = main_process(file_path, folderItem)
            message = p[0]
            build_time = p[1]
            ios_bundle = p[2]
            and_bundle = p[3]
                   
            if message == "Done":
                delete_zip_file(file_path)
                delete_cache(file_path)
                insert_result_to_es(file_path, folderItem['bundle_type'], message, ios_bundle, and_bundle, build_time ) 
                
                count_retry = 1
                process = "True"
                return process
            else:
                build_time = "0"
                ios_bundle = "Not Exist"
                and_bundle = "Not Exits"
                fail_message = "Failed"
                delete_cache(file_path)
                insert_result_to_es(file_path, folderItem['bundle_type'], fail_message, ios_bundle, and_bundle, build_time ) 
                
                count_retry += 1
                if count_retry == max_retry:
                    move_file_to_dead_letter(file_path, folderItem['bundle_type'])
                    process = "True"
                    return process
        return None
    except FileNotFoundError as fe:
        process = None
        return process
    except CustomException as ce:
        process = None
        return process
    except Exception as e:
        process = None
        return process


if __name__ == '__main__':
    count = 0
    i = 0
    while i < 10:
        p = single_process()
        if p == None:
            logger.info("Nothing to do. Wating for zip file!")
            time.sleep(10)
        logger.info("\n")    

