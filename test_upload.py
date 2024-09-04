import time
import logging
import os
from CloudflareBypasser import CloudflareBypasser
from DrissionPage import ChromiumPage, ChromiumOptions
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cloudflare_bypass.log', mode='w')
    ]
)

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

result_list = []

def main():
    # Chromium Browser Path
    isHeadless = os.getenv('HEADLESS', 'false').lower() == 'true'
    
    if isHeadless:
        from pyvirtualdisplay import Display

        display = Display(visible=0, size=(1920, 1080))
        display.start()

    browser_path = os.getenv('CHROME_PATH', "/usr/bin/google-chrome")
    
    # Windows Example
    # browser_path = os.getenv('CHROME_PATH', r"C:/Program Files/Google/Chrome/Application/chrome.exe")

    # Arguments to make the browser better for automation and less detectable.
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
        # "--headless=new"
    ]

    options = get_chromium_options(browser_path, arguments)

    # Initialize the browser
    driver = ChromiumPage(addr_or_opts=options)
    try:
        driver.get('https://ideogram.ai/t/explore')
        logging.info('Starting Cloudflare bypass.')
        cf_bypasser = CloudflareBypasser(driver)
        cf_bypasser.bypass()
        logging.info("Title of the page: %s", driver.title)
        textarea = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[1]/div/div[1]/div[1]/div/textarea[1]')
        textarea.click()
        upload_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/div[3]/div/button')
        upload_button.click.to_upload(r'/data02/CloudflareBypassForScraping/1.jpg')
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
        image_weight = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[1]/div[4]/div[2]/div[2]/div/input')
        image_weight.input(30)
        realistic_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[3]')
        realistic_button.click()
        magic_on_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[2]')
        magic_on_button.click()
        magic_auto_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[1]')
        magic_off_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[3]')
        seed_number = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[12]/div[2]/div/input')
        seed_number.input(123)        
        generate_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[4]/button/div[2]')
        generate_button.click(by_js=False)
        img_path1, img_path2, img_path3, img_path4 = "", "", "", ""
        while True:
            try:
                time.sleep(1)
                response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[1]/div/div/div/div/a/img')
                img_path = response.attr('src')  # 获取 src 属性
                print(img_path)
                path_parts = img_path.split('/') 
                print(path_parts[-2])
                
                # 检查路径是否符合条件
                if len(path_parts) >= 2 and path_parts[-2] == 'response':
                    print('success!')
                    img_path1 = img_path
                    
                    # 获取其他图片的路径
                    response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[2]/div/div/div/div/a/img')
                    img_path2 = response.attr('src')
                    
                    response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[3]/div/div/div/div/a/img')
                    img_path3 = response.attr('src')
                    
                    response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[4]/div/div/div/div/a/img')
                    img_path4 = response.attr('src')
                    
                    # 退出循环
                    break
            except Exception as e:
                print(f"An error occurred: {e}")
                continue
        
        # 将结果添加到结果列表
        result_list.append(img_path1)
        result_list.append(img_path2)
        result_list.append(img_path3)
        result_list.append(img_path4)
        
        
            
        
        textarea = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[1]/div/div[1]/div[1]/div/textarea[1]')
        textarea.click()
                
        upload_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/div[3]/div/button')
        upload_button.click.to_upload(r'/data02/CloudflareBypassForScraping/2.jpg')
        # time.sleep(100)
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
        
        image_weight = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[1]/div[4]/div[2]/div[2]/div/input')
        image_weight.input(30)
        realistic_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[3]')
        realistic_button.click()
        magic_on_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[2]')
        magic_on_button.click()
        magic_auto_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[1]')
        magic_off_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[3]')
        seed_number = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[12]/div[2]/div/input')
        seed_number.clear()
        seed_number.input(321)        
        time.sleep(5)
        while True:
            try:
                print('fuck!')
                generate_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[4]/button/div[2]')
                generate_button.click(by_js=None)
                generate_button.click(by_js=False)
                break
            except Exception as e:
                print(f"操作失败，异常信息: {e}")
                time.sleep(1)
        
        
        # img_path1, img_path2, img_path3, img_path4 = "", "", "", ""
        
        # while True:
        #     try:
        #         time.sleep(1)
        #         response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[1]/div/div/div/div/a/img')
        #         img_path = response.attr('src')  # 获取 src 属性
        #         print(img_path)
        #         path_parts = img_path.split('/') 
        #         print(path_parts[-2])
                
        #         # 检查路径是否符合条件
        #         if len(path_parts) >= 2 and path_parts[-2] == 'response':
        #             print('success!')
        #             img_path1 = img_path
                    
        #             # 获取其他图片的路径
        #             response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[2]/div/div/div/div/a/img')
        #             img_path2 = response.attr('src')
                    
        #             response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[3]/div/div/div/div/a/img')
        #             img_path3 = response.attr('src')
                    
        #             response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[4]/div/div/div/div/a/img')
        #             img_path4 = response.attr('src')
                    
        #             # 退出循环
        #             break
        #     except Exception as e:
        #         print(f"An error occurred: {e}")
        #         continue
        
        # # 将结果添加到结果列表
        # result_list.append(img_path1)
        # result_list.append(img_path2)
        # result_list.append(img_path3)
        # result_list.append(img_path4)
        
        for x in result_list:
            print(x)
        time.sleep(100000)
        # logging.info('Navigating to the demo page.')
        # driver.get('https://ideogram.ai/t/explore')

        # # Where the bypass starts
        # logging.info('Starting Cloudflare bypass.')
        # cf_bypasser = CloudflareBypasser(driver)

        # # If you are solving an in-page captcha (like the one here: https://seleniumbase.io/apps/turnstile), use cf_bypasser.click_verification_button() directly instead of cf_bypasser.bypass().
        # # It will automatically locate the button and click it. Do your own check if needed.

        # cf_bypasser.bypass()

        # logging.info("Enjoy the content!")
        # logging.info("Title of the page: %s", driver.title)
        # textarea = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[1]/div/div[1]/div[1]/div/textarea[1]')
        # textarea.click()
        # upload_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/div[3]/div/button')
        # upload_button.click.to_upload(r'/data02/CloudflareBypassForScraping/1.jpg')
        # time.sleep(1)
        # while True:
        #     try:
        #         remix_button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[2]/div[2]/div[2]/button[2]')
        #         remix_button.click(by_js=None)
        #         break
        #     except Exception as e:
        #         print(f"操作失败，异常信息: {e}")
        #         time.sleep(1)
        
        # image_weight = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[1]/div[4]/div[2]/div[2]/div/input')
        # image_weight.input(30)
        
        # realistic_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[3]')
        # realistic_button.click()
        
        # magic_on_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[2]')
        # magic_on_button.click()
        # time.sleep(10)
        # magic_auto_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[1]')
        # magic_off_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[1]/div[2]/button[3]')
                
        # seed_number = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[3]/div[12]/div[2]/div/input')
        # seed_number.input(123)        
        
        # generate_button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[4]/button')
        # generate_button.click(by_js=False)
        
        # time.sleep(100000)
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
    finally:
        logging.info('Closing the browser.')
        driver.quit()
        if isHeadless:
            display.stop()

if __name__ == '__main__':
    main()


        # remix_button2 = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[2]/div[2]/div[2]/button[2]')
        # remix_button2.click()