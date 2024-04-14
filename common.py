import requests
import os
import winreg
import win32com.client
import requests
from tqdm import tqdm

        
def get_wiresock_installed_path():
    root_key = winreg.HKEY_LOCAL_MACHINE
    subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\Folders"
    try:
        key = winreg.OpenKey(root_key, subkey)
        for i in range(winreg.QueryInfoKey(key)[1]):
            value_name = winreg.EnumValue(key, i)[0]
            if "WireSock" in value_name:
                if "bin" in value_name:
                    return value_name
    except FileNotFoundError:
        pass
    except Exception as e:
        return None
    finally:
        key.Close()    
        
def get_wireguard_installed_path():
    root_key = winreg.HKEY_LOCAL_MACHINE
    subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\Folders"
    try:
        key = winreg.OpenKey(root_key, subkey)
        for i in range(winreg.QueryInfoKey(key)[1]):
            value_name = winreg.EnumValue(key, i)[0]
            if "WireGuard" in value_name:
                return value_name
    except FileNotFoundError:
        pass
    except Exception as e:
        return None
    finally:
        key.Close()    
        
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org")
        return response.text
    except requests.RequestException as e:
        print("Error:", e)
        
        
def check_firewall_rule_exists(port):
    firewall_manager = win32com.client.Dispatch("HNetCfg.FwMgr")
    firewall_policy = firewall_manager.LocalPolicy.CurrentProfile
    rules = firewall_policy.GloballyOpenPorts
    for rule in rules:
        if rule.Port == port:
            return True
    return False

def add_firewall_rule(port, protocol):
    command = 'netsh advfirewall firewall add rule name="HoangVPN {0}" dir=in action=allow protocol={1} localport={0}'.format(port, protocol)
    os.system(command)
    
    command = 'netsh advfirewall firewall add rule name="HoangVPN {0}" dir=out action=allow protocol={1} localport={0}'.format(port, protocol)
    os.system(command)

def download_file(url, file_name):
    
    response = requests.get(url, stream=True)
    response.raise_for_status() 

    file_size = int(response.headers.get('Content-Length', 0))
    chunk_size = 1024

    with open(file_name, 'wb') as f:
        with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as progress_bar:
            for chunk in response.iter_content(chunk_size):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))