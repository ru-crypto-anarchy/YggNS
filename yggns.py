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

s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
s.bind((address, port))

while True:
    # Grap query from wire
    (wire, address) = s.recvfrom(512)
    dns_local_query = dns.message.from_wire(wire)

    # Try to grap DNS query info from packet
    try:
        dns_local_query_find_name = dns_local_query.find_rrset(dns_local_query.question, dns_local_query.question[0].name, dns.rdataclass.IN, dns.rdatatype.AAAA)
    except KeyError:
        dns_remote_response = dns.query.udp(dns_local_query, bypass_ns)
        s.sendto(dns_remote_response.to_wire(), address)
        continue

    # RegExp for YggNS name format and try to grab it from query
    re_ygg_full_domain = re.compile("([0-9a-zA-Z\-]*\.)*0[2,3]{1}[0-9a-fA-F]{30}\.ygg\.")
    match_ygg_full_domain = re.search(re_ygg_full_domain, str(dns_local_query_find_name.name))

    # IF name from query is in YggNS format THEN try to resolve it through Yggdrasil
    if match_ygg_full_domain:
        # RegExp IPv6-part from full name and convert it to IPv6 address
        re_ygg_dns_address = re.compile("\.?0[2,3]{1}[0-9a-fA-F]{30}\.ygg\.$")
        match_ygg_dns_address = re.search(re_ygg_dns_address, match_ygg_full_domain.group())
        ygg_dns_address = match_ygg_dns_address.group().replace('.', '').replace('ygg', '')
        ygg_dns_address_ipv6 = ''
        for l in range(8):
            ygg_dns_address_ipv6 = ygg_dns_address_ipv6 + str(ygg_dns_address[l*4:l*4+4]) + ':'
        ygg_dns_address_ipv6 = ygg_dns_address_ipv6[:-1]

        # Do a query and sent it back to client
        try:
            dns_remote_response = dns.query.udp(dns_local_query, ygg_dns_address_ipv6, query_timeout)
        except dns.exception.Timeout:
            pass
        s.sendto(dns_remote_response.to_wire(), address)

    # ELSE do a query to bypass nameserver
    else:
        dns_remote_response = dns.query.udp(dns_local_query, bypass_ns)
        s.sendto(dns_remote_response.to_wire(), address)
