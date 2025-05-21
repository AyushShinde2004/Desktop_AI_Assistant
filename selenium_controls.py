from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import atexit
import signal
import sys
import time

driver = None

# Handle Ctrl+C or terminal kill
def signal_handler(sig, frame):
    print("Terminating... Closing browser.")
    cleanup_driver()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # kill

def initialize_driver():
    global driver
    if driver is None:
        chrome_options = uc.ChromeOptions()
        chrome_options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        chrome_options.add_argument("--load-extension=C:\\Users\\LEGION\\OneDrive\\Desktop\\Python Shit\\A.I Assistant\\uBlock")
        chrome_options.add_argument("--disable-extensions-except=C:\\Users\\LEGION\\OneDrive\\Desktop\\Python Shit\\A.I Assistant\\uBlock")
        chrome_options.add_argument("--disable-features=PreloadMediaEngagementData,MediaEngagementBypassAutoplayPolicies")
        chrome_options.add_argument("--window-size=1280,720")
    
        driver = uc.Chrome(options=chrome_options)
        atexit.register(lambda: driver.quit() if driver else None)

def cleanup_driver():
    global driver
    if driver:
        try:
            driver.quit()
        except Exception as e:
            print("Error during driver.quit():", e)
        driver = None

def play_on_youtube(song_name):
    try:
        initialize_driver()
        search_url = f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}"
        driver.get(search_url)
        wait = WebDriverWait(driver, 10)
        first_video = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a#video-title")))
        first_video.click()
        print(f"Playing: {song_name}")
        return True
    except Exception as e:
        print("Error playing video:", e)
        cleanup_driver()
        return False

def selenium_play_pause():
    try:
        script = """
        var video = document.querySelector('video');
        if(video){
            if(video.paused) {
                video.play();
            } else {
                video.pause();
            }
            return video.paused;
        }
        return null;
        """
        paused_state = driver.execute_script(script)
        print("Toggled play/pause on YouTube. Now paused:", paused_state)
    except Exception as e:
        print("Error toggling play/pause:", e)

def selenium_next_video():
    try:
        script = """
        var nextButton = document.querySelector('.ytp-next-button');
        if (nextButton && !nextButton.disabled) {
            nextButton.click();
            return true;
        }
        return false;
        """
        success = driver.execute_script(script)
        if success:
            return True
        else:
            print("Next button not available or disabled.")
            return False
    except Exception as e:
        print(f"Error executing script to play next video: {e}")
        return False

