import time
import logging
import os
import json
from CloudflareBypasser import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions
from flask import Flask, request, jsonify
from datetime import datetime
import shutil
import requests

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cloudflare_bypass.log', mode='w')
    ]
)

result_list = []

def get_chromium_options(browser_path: str, arguments: list) -> ChromiumOptions:
    """
    Configures and returns Chromium options.
    
    :param browser_path: Path to the Chromium browser executable.
    :param arguments: List of arguments for the Chromium browser.
    :return: Configured ChromiumOptions instance.
    """
    options = ChromiumOptions()
    options.set_argument('--auto-open-devtools-for-tabs', 'true') # we don't need this anymore
    options.set_paths(browser_path=browser_path)
    for argument in arguments:
        options.set_argument(argument)
    return options

@app.route('/process_images', methods=['POST'])
def process_images():
    image_type = request.form.get('image-type', default='realistic')
    magic_prompt = request.form.get('magic-prompt', default='')
    seed = request.form.get('seed', type=int, default=-1)
    negative_prompt = request.form.get('negative-prompt', default='none')
    image_weight = request.form.get('image-weight', type=int, default=50)
    input_dir = request.form.get('input_dir')
    # isHeadless = os.getenv('HEADLESS', 'false').lower() == 'true'
    isHeadless = False

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_dir = os.path.join(os.getcwd(), f'results_{timestamp}')
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_dir):
        return jsonify({"error": "input_dir not found"}), 400    

    if isHeadless:
        from pyvirtualdisplay import Display

        display = Display(visible=0, size=(1920, 1080))
        display.start()

    browser_path = os.getenv('CHROME_PATH', "/usr/bin/google-chrome")
    
    arguments = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
        "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
        "-deny-permission-prompts",
        "-disable-gpu",
        "-accept-lang=en-US",
    ]

    options = get_chromium_options(browser_path, arguments)
    driver = ChromiumPage(addr_or_opts=options)
    driver.get('https://ideogram.ai/t/explore')
    cf_bypasser = CloudflareBypasser(driver)
    cf_bypasser.bypass()
    logging.info("Title of the page: %s", driver.title)
    
    image_list = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    is_first = True
    for image in image_list:
        if is_first:
            is_first = False
            textarea = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[1]/div/div[1]/div[1]/div/textarea[1]')
            textarea.click()
            upload_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/div[3]/div/button')
            upload_button.click.to_upload(image)     
            while True:
                try:
                    print('fuck!')
                    remix_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[2]/div[2]/button[2]/div')
                    remix_button.click(by_js=None)
                    remix_button.click(by_js=False)
                    break
                except Exception as e:
                    print(f"操作失败，异常信息: {e}")
                    time.sleep(1)
            image_weight_ele = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[1]/div[4]/div[2]/div[2]/div/input')
            image_weight_ele.clear()
            image_weight_ele.input(image_weight)
            general_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[2]')
            design_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[2]/div//div[4]')
            threed_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[2]/div//div[5]')
            anime_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[2]/div//div[6]')
            realistic_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[3]')
            if image_type == 'general':
                general_button.click()
            elif image_type == 'realistic':
                realistic_button.click()
            elif image_type == 'design':
                design_button.click()
            elif image_type == '3d':
                threed_button.click()
            elif image_type == 'anime':
                anime_button.click()
            
            
            magic_on_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[2]')
            magic_auto_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[1]')
            magic_off_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[3]')
            if magic_prompt == 'on':
                magic_on_button.click()
            elif magic_prompt == 'off':
                magic_off_button.click()
            
            
            seed_number = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[12]/div[2]/div/input')
            if seed != -1:
                seed_number.clear()
                seed_number.input(seed)        
                
            negative_prompt_ele = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[14]/div[2]/div/textarea[1]')
            if negative_prompt != 'none':
                negative_prompt_ele.clear()
                negative_prompt_ele.input(negative_prompt)
            
            time.sleep(5)
            while True:
                try:
                    print('fuck!')
                    generate_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[4]/button/div[2]')
                    generate_button.click()
                    break
                except Exception as e:
                    print(f"操作失败，异常信息: {e}")
                    time.sleep(1)
            img_path1, img_path2, img_path3, img_path4 = "", "", "", ""
            while True:
                try:
                    time.sleep(1)
                    response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[1]/div/div/div/div/a/img')
                    img_path = response.attr('src')  
                    print(img_path)
                    path_parts = img_path.split('/') 
                    print(path_parts[-2])
                    
                    if len(path_parts) >= 2 and path_parts[-2] == 'response':
                        print('success!')
                        img_path1 = img_path
                        
                        response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[2]/div/div/div/div/a/img')
                        img_path2 = response.attr('src')
                        
                        response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[3]/div/div/div/div/a/img')
                        img_path3 = response.attr('src')
                        
                        response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[4]/div/div/div/div/a/img')
                        img_path4 = response.attr('src')
                        
                        break
                except Exception as e:
                    print(f"An error occurred: {e}")
                    continue
            
            result_list.append(img_path1)
            result_list.append(img_path2)
            result_list.append(img_path3)
            result_list.append(img_path4)
        else:
            textarea = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div/div')
            textarea.click()
            time.sleep(5)
            upload_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/div[3]/div/button')
            upload_button.click.to_upload(image)
            while True:
                try:
                    print('fuck!')
                    remix_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[2]/div[2]/button[2]/div')
                    remix_button.click(by_js=None)
                    remix_button.click(by_js=False)
                    break
                except Exception as e:
                    print(f"操作失败，异常信息: {e}")
                    time.sleep(1)
            
            image_weight_ele = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[1]/div[4]/div[2]/div[2]/div/input')
            image_weight_ele.clear()
            image_weight_ele.input(image_weight)
            general_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[2]')
            realistic_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[3]')
            design_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[4]')
            threed_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[5]')
            anime_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[6]')
            if image_type == 'general':
                general_button.click()
            elif image_type == 'realistic':
                realistic_button.click()
            elif image_type == 'design':
                design_button.click()
            elif image_type == '3d':
                threed_button.click()
            elif image_type == 'anime':
                anime_button.click()
            magic_on_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[2]')
            magic_auto_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[1]')
            magic_off_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[3]')
            if magic_prompt == 'on':
                magic_on_button.click()
            elif magic_prompt == 'off':
                magic_off_button.click()
            seed_number = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[12]/div[2]/div/input')
            if seed != -1:
                seed_number.clear()
                seed_number.input(seed)        
            negative_prompt_ele = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[14]/div[2]/div/textarea[1]')
            if negative_prompt != 'none':
                negative_prompt_ele.clear()
                negative_prompt_ele.input(negative_prompt)
            
            time.sleep(5)
            while True:
                try:
                    print('fuck!')
                    generate_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[4]/button/div[2]')
                    generate_button.click()
                    break
                except Exception as e:
                    print(f"操作失败，异常信息: {e}")
                    time.sleep(1)
            img_path1, img_path2, img_path3, img_path4 = "", "", "", ""
            while True:
                try:
                    time.sleep(1)
                    response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[1]/div/div/div/div/a/img')
                    img_path = response.attr('src')  
                    print(img_path)
                    path_parts = img_path.split('/') 
                    print(path_parts[-2])
                    
                    if len(path_parts) >= 2 and path_parts[-2] == 'response':
                        print('success!')
                        img_path1 = img_path
                        
                        response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[2]/div/div/div/div/a/img')
                        img_path2 = response.attr('src')
                        
                        response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[3]/div/div/div/div/a/img')
                        img_path3 = response.attr('src')
                        
                        response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[4]/div/div/div/div/a/img')
                        img_path4 = response.attr('src')
                        
                        break
                except Exception as e:
                    print(f"An error occurred: {e}")
                    continue
            
            result_list.append(img_path1)
            result_list.append(img_path2)
            result_list.append(img_path3)
            result_list.append(img_path4)
    
    for i, img_path in enumerate(result_list):
        try:
            response = requests.get(img_path, stream=True)
            response.raise_for_status() 
            download_image_path = os.path.join(output_dir, f'result_image_{i + 1}.jpg')

            with open(download_image_path, 'wb') as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        out_file.write(chunk)

            logging.info(f"Downloaded image {img_path} to {download_image_path}")

        except Exception as e:
            logging.error(f"Failed to download {img_path}: {e}")

    json_data = {f'result_image_{i + 1}': img_path for i, img_path in enumerate(result_list)}
    json_file_path = os.path.join(output_dir, 'results.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    driver.quit()
    if isHeadless:
        display.stop()

    return jsonify({
        "status": "success",
        "output_dir": output_dir
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)