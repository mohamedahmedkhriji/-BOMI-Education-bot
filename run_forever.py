import subprocess
import time
import sys
import os

def run_bot():
    while True:
        try:
            print("Starting bot...")
            process = subprocess.Popen([sys.executable, "start_bot.py"], 
                                     cwd=os.path.dirname(os.path.abspath(__file__)))
            process.wait()
            print("Bot stopped. Restarting in 5 seconds...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("Stopping bot...")
            if 'process' in locals():
                process.terminate()
            break
        except Exception as e:
            print(f"Error: {e}. Restarting in 10 seconds...")
            time.sleep(10)

if __name__ == '__main__':
    run_bot()