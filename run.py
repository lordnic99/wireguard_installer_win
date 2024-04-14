import os
import sys
import ctypes
import common
import wireguard_handler
import subprocess
import wg_generator
import json
import segno

wireguard_url   = r"https://download.wireguard.com/windows-client/wireguard-amd64-0.5.3.msi"
wiresock_url    = r"https://www.wiresock.net/sdc_download/909/?key=800439ju4unkj0zn5o7y3ve469bvtg"

CONFIG_VPN = ""

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
    
def ON_FINISH_INSTALLATION():
    os.remove("wiresock.msi")
    os.remove("wireguard.msi")
    print("===========================================")
    print("QR for mobile connect")
    segno.make_qr(CONFIG_VPN)
    print("===========================================")
    print("Client config information")
    print()
    print()
    print(CONFIG_VPN)
            
def wireguard_start():
    wiresock_base = common.get_wiresock_installed_path()
    wiresock_bin = ""
    if wiresock_base != None:
        wiresock_bin = os.path.join(wiresock_base, r"wg-quick-config.exe")
        print(f"found wiresock bin: {wiresock_bin}")
    else:
        print("wiresock not found, reboot and try again")
        os._exit(1)
        
    command = wiresock_bin + r" --restart"
    
    try:
        env = os.environ.copy()
        env["PATH"] += os.pathsep + common.get_wireguard_installed_path()
        wiresock_p = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW, env=env)
        wiresock_p.wait()
        if wiresock_p.returncode == 0:
            print("wiresock ok")
    except Exception as e:
        print("wiresock config failed restart and try agian")
        print(e)
        os._exit(1)

        
def wireguard_config_handler(udp_end_point):
    global CONFIG_VPN
    config_json_dest = r'C:\ProgramData\NT KERNEL\WireSock VPN Gateway\config.json'
    config_master_dest = r'C:\ProgramData\NT KERNEL\WireSock VPN Gateway\wiresock.conf'
    config_client_dest = r'C:\ProgramData\NT KERNEL\WireSock VPN Gateway\wsclient_1.conf'
    
    try:
        os.remove(config_json_dest)
        os.remove(config_master_dest)
        os.remove(config_client_dest)
    except OSError:
        pass
    
    server_private_key, server_public_key = wg_generator.generate_wireguard_keys()
    client_private_key, client_public_key = wg_generator.generate_wireguard_keys()
    
    server_config = wg_generator.create_server_config(server_private_key, client_public_key)
    client_config = wg_generator.create_client_config(client_private_key, server_public_key, udp_end_point)
    
    CONFIG_VPN = client_config
    
    with open(config_master_dest, "w") as server_file:
        server_file.write(server_config)
    with open(config_client_dest, "w") as client_file:
        client_file.write(client_config)
        
    json_config = wg_generator.fill_json_config(server_private_key=server_private_key,
                                                server_public_key=server_public_key,
                                                client_private_key=client_private_key,
                                                client_public_key=client_public_key,
                                                endpoint=udp_end_point)
    with open(config_json_dest, 'w') as file:
        json.dump(json_config, file, indent=4)
        
    
    
def main():
    print("prepare wireguard and wiresock")
    common.download_file(wireguard_url, "wireguard.msi")
    common.download_file(wiresock_url, "wiresock.msi")
    wireguard_handler.main()
    
    udp_endpoint = f"{common.get_public_ip()}:55555"
    
    print("prepare config for wireguard")
    wireguard_config_handler(udp_endpoint)
    
    print("wireguard start")
    wireguard_start()
    
    ON_FINISH_INSTALLATION()
    
if is_admin():
    main()
else:
    ctypes.windll.shell32.ShellExecuteW(None,  "runas", sys.executable, " ".join(sys.argv), None, 1)
    