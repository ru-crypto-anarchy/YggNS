#!/usr/bin/python3

# OPTIONS
# Local DNS-proxy IP
address = '::1'
# Local DNS-proxy port
port = 53535
# DNS for query-bypass (if query is NOT for an YggNS)
bypass_ns = '8.8.8.8'
# Query timeout
query_timeout = 5

import socket
import re
import dns.message
import dns.query
import base64
import binascii
from IPy import IP

# Compile RegExps
re_catch_domain_ipv6 = re.compile(";QUESTION\n([0-9a-zA-Z\-\_]*\.)*((?P<ipv6>0[2,3]{1}[0-9a-fA-F]{30})|(?P<b32>[2,3]{1}[A-Za-z2-7]{24})|(?P<ipv6dash>0?[2,3]{1}[0-9a-fA-F\-]{0,37}))\.ygg\..+\n;ANSWER", re.MULTILINE)

def catch_ygg_ipv6_address(dns_query):
    match_catch_domain_ipv6 = re.search(re_catch_domain_ipv6, dns_query.to_text())
    if match_catch_domain_ipv6:
        if match_catch_domain_ipv6.group('ipv6'):
            catch_domain_ipv6 = match_catch_domain_ipv6.group('ipv6')
            ygg_dns_ipv6 = ''
            for l in range(8):
                ygg_dns_ipv6 = ygg_dns_ipv6 + str(catch_domain_ipv6[l*4:l*4+4]) + ':'
            ygg_dns_ipv6 = ygg_dns_ipv6[:-1]
        elif match_catch_domain_ipv6.group('b32'):
            catch_domain_ipv6 = '0' + match_catch_domain_ipv6.group('b32')[:1] + binascii.b2a_hex(base64.b32decode(match_catch_domain_ipv6.group('b32')[1:].upper())).decode("ascii")
            ygg_dns_ipv6 = ''
            for l in range(8):
                ygg_dns_ipv6 = ygg_dns_ipv6 + str(catch_domain_ipv6[l*4:l*4+4]) + ':'
            ygg_dns_ipv6 = ygg_dns_ipv6[:-1]
        elif match_catch_domain_ipv6.group('ipv6dash'):
            ygg_dns_ipv6 = match_catch_domain_ipv6.group('ipv6dash').replace('-', ':')
        try:
            IP(ygg_dns_ipv6).version
            return ygg_dns_ipv6
        except ValueError:
            return False
    else:
        return False

s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
s.bind((address, port))

while True:
    # Grap query from wire
    (wire, address) = s.recvfrom(512)
    dns_local_query = dns.message.from_wire(wire)

    ygg_dns_ipv6 = catch_ygg_ipv6_address(dns_local_query)

    if ygg_dns_ipv6:
        # Do a query and sent it back to client
        try:
            dns_remote_response = dns.query.udp(dns_local_query, ygg_dns_ipv6, query_timeout)
            s.sendto(dns_remote_response.to_wire(), address)
        except dns.exception.Timeout:
            continue
        except OSError:
            continue
    # ELSE do a query to bypass nameserver
    else:
        try:
            dns_remote_response = dns.query.udp(dns_local_query, bypass_ns)
            s.sendto(dns_remote_response.to_wire(), address)
        except OSError:
            continue
