#!/usr/bin/env python3
"""
download_bulletins.py

Downloads all CWC weekly reservoir storage bulletin PDFs directly from
the CWC RSMS portal (https://rsms.cwc.gov.in/frameWork/web/bulletin-report-page)
into data/bulletins/.
"""

import argparse
import base64
import hashlib
import hmac
import json
import logging
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("download_bulletins")

SERVICE_URL = "https://rsms.cwc.gov.in/admin/"
STORAGE_URL = "https://rsms.cwc.gov.in/admin/storage/bulletins/"

# Known keys discovered from CWC RSMS application bundle
DEFAULT_AES_KEY = bytes.fromhex("0123456789abcdef0123456789abcdef")
DEFAULT_AES_IV = b"1234567890abcdef"
DEFAULT_HMAC_KEY = b"P2@G2#N201684728499"


def fetch_secret_keys():
    """Fetch and decrypt live secrets from CWC admin API."""
    try:
        url = SERVICE_URL + "get-secret-keys"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        enc_resp = data.get("RESPONSE_DATA")
        if not enc_resp:
            return DEFAULT_AES_KEY, DEFAULT_AES_IV, DEFAULT_HMAC_KEY

        cipher = Cipher(algorithms.AES(DEFAULT_AES_KEY), modes.CBC(DEFAULT_AES_IV))
        decryptor = cipher.decryptor()
        raw_bytes = base64.b64decode(enc_resp)
        decrypted_padded = decryptor.update(raw_bytes) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        dec = unpadder.update(decrypted_padded) + unpadder.finalize()
        keys_obj = json.loads(dec.decode("utf-8")).get("result", {})
        hmac_key = keys_obj.get("API_HASHING_KEY", "").encode("utf-8") or DEFAULT_HMAC_KEY
        return DEFAULT_AES_KEY, DEFAULT_AES_IV, hmac_key
    except Exception as e:
        logger.warning("Could not fetch live secret keys, using defaults: %s", e)
        return DEFAULT_AES_KEY, DEFAULT_AES_IV, DEFAULT_HMAC_KEY


def encrypt_request_data(payload: Any, key: bytes, iv: bytes) -> str:
    """Encrypt payload using AES-128-CBC matching Angular data_encryptV2."""
    p = json.dumps(json.dumps(payload))
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(p.encode("utf-8")) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    enc = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(enc).decode("utf-8")


def decrypt_response_data(enc_b64: str, key: bytes, iv: bytes) -> Any:
    """Decrypt response payload using AES-128-CBC matching Angular data_decryptV2."""
    raw_bytes = base64.b64decode(enc_b64)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(raw_bytes) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    dec = unpadder.update(decrypted_padded) + unpadder.finalize()
    return json.loads(json.loads(dec.decode("utf-8")))


def fetch_bulletin_records(limit: int = 150) -> List[Dict[str, Any]]:
    """Fetch bulletin metadata list from CWC RSMS."""
    key, iv, hmac_key = fetch_secret_keys()
    req_obj = {"vchBulletinName": "", "from_date": "", "to_date": ""}
    enc_req = encrypt_request_data(req_obj, key, iv)
    token = hmac.new(hmac_key, enc_req.encode("utf-8"), hashlib.sha256).hexdigest()

    post_body = json.dumps({"REQUEST_DATA": enc_req, "REQUEST_TOKEN": token}).encode("utf-8")
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    url = f"{SERVICE_URL}bulletin-report-page?page=1&limit={limit}"

    req = urllib.request.Request(url, data=post_body, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        resp_json = json.loads(resp.read().decode("utf-8"))

    if "RESPONSE_DATA" in resp_json:
        dec = decrypt_response_data(resp_json["RESPONSE_DATA"], key, iv)
        records = dec.get("data", {}).get("data", [])
        return records
    return []


def download_all_bulletins(output_dir: Path) -> List[Path]:
    """Download all bulletin PDFs to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Querying CWC RSMS bulletin portal...")
    records = fetch_bulletin_records(limit=150)
    logger.info("Found %d bulletin records from CWC RSMS.", len(records))

    downloaded_files: List[Path] = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for idx, rec in enumerate(records, 1):
        filename = rec.get("vchApprovedFile")
        if not filename or not filename.endswith(".pdf"):
            continue

        target_path = output_dir / filename
        if target_path.exists() and target_path.stat().st_size > 10000:
            logger.info("[%d/%d] Already exists: %s", idx, len(records), filename)
            downloaded_files.append(target_path)
            continue

        file_url = STORAGE_URL + filename
        logger.info("[%d/%d] Downloading %s ...", idx, len(records), filename)
        try:
            req = urllib.request.Request(file_url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                pdf_bytes = resp.read()
                if len(pdf_bytes) > 1000:
                    with open(target_path, "wb") as f_out:
                        f_out.write(pdf_bytes)
                    downloaded_files.append(target_path)
                    logger.info("Saved %s (%.2f MB)", filename, len(pdf_bytes) / 1024 / 1024)
                else:
                    logger.warning("File %s too small (not valid PDF)", filename)
            time.sleep(0.2)  # courteous request delay
        except Exception as e:
            logger.error("Failed to download %s: %s", filename, e)

    logger.info("Completed downloading %d bulletin PDF(s) into %s", len(downloaded_files), output_dir)
    return downloaded_files


def main():
    parser = argparse.ArgumentParser(description="Download weekly bulletin PDFs from CWC RSMS.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/bulletins",
        help="Directory to save downloaded bulletin PDFs (default: data/bulletins)",
    )
    args = parser.parse_args()
    download_all_bulletins(Path(args.output_dir))


if __name__ == "__main__":
    main()
