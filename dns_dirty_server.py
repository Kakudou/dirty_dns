import socket
import dnslib
import json
import random
import string


def start_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"DNS is listening on {host}:{port}")
    value = ""
    while True:
        data, address = sock.recvfrom(1024)
        response, value = manage_data(data, value, address)
        sock.sendto(response, address)

def to_hex(s):
    return s.encode().hex()

def from_hex(s):
    return bytes.fromhex(s).decode()

def generate_random_word(length):
    vowels = 'aeiou'
    consonants = ''.join(set(string.ascii_lowercase) - set(vowels))
    word = ''
    for i in range(length):
        if i % 2 == 0:
            word += random.choice(consonants)
        else:
            word += random.choice(vowels)
    return word

def manage_data(data, value, address):
    request = dnslib.DNSRecord.parse(data)
    reply = dnslib.DNSRecord(dnslib.DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
    qname = str(request.q.qname)
    qtype = request.q.qtype
    qtype_hr = dnslib.QTYPE[qtype]

    dns_records = json.load(open("dns_beacon.json"))

    if qname in dns_records and qtype_hr in dns_records[qname]:
            answer = eval(f"dnslib.{qtype_hr}(dns_records[qname].get(qtype_hr))")
            reply.add_answer(dnslib.RR(rname=qname, rtype=qtype, rdata=answer))
    elif qname not in dns_records:
        sock8888 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dns_query = dnslib.DNSRecord.question(qname, qtype_hr).pack()
        sock8888.sendto(dns_query, ("8.8.8.8", 53))
        response, _ = sock8888.recvfrom(512)
        reply = dnslib.DNSRecord.parse(response)
        reply.header.id = request.header.id

    elif qname in dns_records and qtype_hr == "DNSKEY":
            custom_answer = input(f"Enter the answer for {qname} ({qtype_hr}): ")

#? 5: RSA/SHA-1
#? 7: RSA/SHA-1 (deprecated)
#? 8: RSA/SHA-256
#? 10: RSA/SHA-512
#? 13: ECDSA Curve P-256 with SHA-256
#? 14: ECDSA Curve P-384 with SHA-384
#? 15: Ed25519
#? 16: Ed448

            answer = dnslib.DNSKEY(
                flags=256,
                protocol=3,
                algorithm=13, # Could be use to specify the pld type
                key=to_hex(custom_answer)
            )

            # and ttl, time before next refresh
            reply.add_answer(dnslib.RR(rname=qname, rtype=qtype, rdata=answer, ttl=0))
    elif qtype_hr == "PTR" and 'arpa' in qname:
            ptr = ([key for key, value in dns_records.items() if '.'.join(value.get('A').split('.')[::-1]) in qname][0])
            reply.add_answer(dnslib.RR(rname=qname, rtype=qtype, rdata=dnslib.PTR(ptr)))
    elif qtype_hr == "CNAME":
        real_qname = qname.split('.', 1)[1]
        if real_qname in dns_records:
            nb = int(qname.split('a', 1)[0])
            to_remove = f"{nb}a"
            if nb > 0:
                value += qname[len(to_remove):].split('.')[0]

                nb_letter = random.randint(3, 10)
                word = generate_random_word(nb_letter)

                reply.add_answer(dnslib.RR(rname=qname, rtype=qtype, rdata=dnslib.CNAME(f"{word}{real_qname[:-1]}")))
            else:
                value += qname[len(to_remove):].split('.')[0]
                reply.add_answer(dnslib.RR(rname=qname, rtype=qtype, rdata=dnslib.CNAME(f"{real_qname}")))
                print(from_hex(value))
                value = ""

    return reply.pack(), value

if __name__ == "__main__":
    start_server("127.0.0.1", 4242)

