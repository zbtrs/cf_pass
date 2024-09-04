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
        logging.info('Navigating to the demo page.')
        driver.get('https://ideogram.ai/t/explore')

        # Where the bypass starts
        logging.info('Starting Cloudflare bypass.')
        cf_bypasser = CloudflareBypasser(driver)

        # If you are solving an in-page captcha (like the one here: https://seleniumbase.io/apps/turnstile), use cf_bypasser.click_verification_button() directly instead of cf_bypasser.bypass().
        # It will automatically locate the button and click it. Do your own check if needed.

        cf_bypasser.bypass()

        logging.info("Enjoy the content!")
        logging.info("Title of the page: %s", driver.title)
        
        texts = ['haha', 'test1']  # 你可以根据需要添加更多文本
        result_list = []

        is_first = True

        for text in texts:
            try:
                if is_first is True:
                    textarea = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[1]/div/div[1]/div[1]/div/textarea[1]')
                    textarea.input(text)
                    button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[4]/button')
                    button.click(by_js=False)
                    time.sleep(1)
                
                    button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/button')
                    button.click(by_js=False)
                    is_first = False
                else:
                    textarea = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[1]/div[1]/div/div[1]/div[1]/div/textarea[1]')
                    textarea.clear()
                    textarea.input(text)
                    button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[4]/button')
                    button.click(by_js=False)
                    # //*[@id="root"]/header/div/div[2]/div/div/div/div/div[2]/div[4]/button
                
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
                
            except Exception as e:
                print(f"An error occurred during the text input and click process: {e}")
        
        
        for x in result_list:
            print(x)
        
        # textarea = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[1]/div[1]/div/div[1]/div[1]/div/textarea[1]')
        # textarea.input('haha')
        # button = driver.ele('xpath://*[@id="root"]/div[2]/div/div/div[2]/div/div/div/div/div[2]/div[4]/button')
        # button.click(by_js=False)
        # time.sleep(1)
        # button = driver.ele('xpath://*[@id="root"]/header/div/div[2]/div/div/button')
        # button.click(by_js=False)
        # img_path1 = ""
        # img_path2 = ""
        # img_path3 = ""
        # img_path4 = ""
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
        #             img_path = response.attr('src')
        #             img_path2 = img_path
                    
        #             response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[3]/div/div/div/div/a/img')
        #             img_path = response.attr('src')
        #             img_path3 = img_path
                    
        #             response = driver.ele('xpath://*[@id="root"]/div[3]/div[2]/div[4]/div/div/div/div/a/img')
        #             img_path = response.attr('src')
        #             img_path4 = img_path
                    
        #             # 退出循环
        #             break
        #     except Exception as e:
        #         print(f"An error occurred: {e}")
        #         continue

        # # 输出最终结果
        # print(img_path1)
        # print(img_path2)
        # print(img_path3)
        # print(img_path4)
        time.sleep(100000)
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
    finally:
        logging.info('Closing the browser.')
        driver.quit()
        if isHeadless:
            display.stop()

if __name__ == '__main__':
    main()
