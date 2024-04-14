import subprocess
import common
import os


def generate_wireguard_keys():
    env = os.environ.copy()
    env["PATH"] += os.pathsep + common.get_wireguard_installed_path()
    private_key_process = subprocess.run(['wg', 'genkey'], capture_output=True, text=True, shell=True, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
    if private_key_process.returncode != 0:
        raise Exception("Failed to generate private key")
    private_key = private_key_process.stdout.strip()

    public_key_process = subprocess.run(['wg', 'pubkey'], input=private_key, capture_output=True, text=True, shell=True, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
    if public_key_process.returncode != 0:
        raise Exception("Failed to generate public key")
    public_key = public_key_process.stdout.strip()

    return private_key, public_key

def create_server_config(server_private_key, client_public_key):
    config = f"""[Interface]
PrivateKey = {server_private_key}
Address = 10.9.0.1/24
ListenPort = 55555

[Peer]
PublicKey = {client_public_key}
AllowedIPs = 10.9.0.2/32
"""
    return config

def create_client_config(client_private_key, server_public_key, server_endpoint):
    config = f"""[Interface]
PrivateKey = {client_private_key}
Address = 10.9.0.2/24
DNS = 8.8.8.8, 1.1.1.1
MTU = 1420

[Peer]
PublicKey = {server_public_key}
AllowedIPs = 0.0.0.0/0
Endpoint = {server_endpoint}
PersistentKeepalive = 25
"""
    return config


def fill_json_config(server_private_key, server_public_key, client_private_key, client_public_key, endpoint):
    template = {
        "Server": {
            "PrivateKey": server_private_key,
            "ListenPort": 55555,
            "Address": [{"IP": "10.9.0.1", "Mask": "////AA=="}],
            "DNS": None,
            "MTU": 0,
            "Peers": [
                {
                    "PublicKey": client_public_key,
                    "AllowedIPs": [{"IP": "10.9.0.2", "Mask": "/////w=="}],
                    "Endpoint": "",
                    "PersistentKeepalive": 0
                }
            ]
        },
        "Clients": [
            {
                "PrivateKey": client_private_key,
                "ListenPort": 0,
                "Address": [{"IP": "10.9.0.2", "Mask": "////AA=="}],
                "DNS": ["8.8.8.8", "1.1.1.1"],
                "MTU": 1420,
                "Peers": [
                    {
                        "PublicKey": server_public_key,
                        "AllowedIPs": [{"IP": "0.0.0.0", "Mask": "AAAAAA=="}],
                        "Endpoint": endpoint,
                        "PersistentKeepalive": 25
                    }
                ]
            }
        ]
    }

    return template