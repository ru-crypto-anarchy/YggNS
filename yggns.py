#!/usr/bin/python3

# Common Modules
import socket
import re
import binascii
import base64
import argparse
import logging

# Installed Modules
from IPy import IP
import dns.message
import dns.query

args_parser = argparse.ArgumentParser(description='DNS-proxy for clumsy but distribuded NS system for Yggdrasil network.')
args_parser.add_argument('-a', dest='address', type=IP, default=IP('::1'), help='Local DNS-proxy IPv6-address. Default is IPv6 localhost [::1];')
args_parser.add_argument('-p', dest='port', type=int, default=53535, help='Local DNS-proxy UDP port. Default is 53535;')
args_parser.add_argument('-b', dest='bypass_ns', type=IP, help='Bypass DNS server for non-YggNS queries. Default is none and its recomended. If bypass NS is not set then non-YggNS queries will be responded with empty response. Best practice is to forward .ygg requests by your local or LAN resolver, like dnsmasq or dnscrypt, to YggNS;')
args_parser.add_argument('-t', dest='query_timeout', type=int, default=5, help='Query timeout in seconds. Default is 5 seconds;')
args_parser.add_argument('--log', dest='logfile', type=str, help='Output log to file. Requests and responses.')
args = args_parser.parse_args()
args.address = str(args.address)

logging.basicConfig(filename=args.logfile, filemode='w', format='%(asctime)s - %(message)s', level=logging.DEBUG)
logging.debug('YggNS DNS-proxy started!')

# Compile RegExps
re_catch_domain_ipv6 = re.compile(";QUESTION\n([0-9a-zA-Z\-\_]*\.)*((?P<ipv6>0[2,3]{1}[0-9a-fA-F]{30})|(?P<b32>[2,3]{1}[A-Za-z2-7]{24})|(?P<ipv6dash>0?[2,3]{1}[0-9a-fA-F\-]{0,37}))\.ygg\..+\n;ANSWER", re.MULTILINE)

def catch_ygg_ipv6_address(dns_query):
    match_catch_domain_ipv6 = re.search(re_catch_domain_ipv6, dns_query.to_text())
    if match_catch_domain_ipv6:
        if match_catch_domain_ipv6.group('ipv6'):
            logging.debug('Catched Yggdrasil NS in STRAIGHT format: ' + match_catch_domain_ipv6.group('ipv6'))
            catch_domain_ipv6 = match_catch_domain_ipv6.group('ipv6')
            ygg_dns_ipv6 = ''
            for l in range(8):
                ygg_dns_ipv6 = ygg_dns_ipv6 + str(catch_domain_ipv6[l*4:l*4+4]) + ':'
            ygg_dns_ipv6 = ygg_dns_ipv6[:-1]
        elif match_catch_domain_ipv6.group('b32'):
            logging.debug('Catched Yggdrasil NS in BASE32 format: ' + match_catch_domain_ipv6.group('b32'))
            catch_domain_ipv6 = '0' + match_catch_domain_ipv6.group('b32')[0] + binascii.b2a_hex(base64.b32decode(match_catch_domain_ipv6.group('b32')[1:].upper())).decode('ascii')
            ygg_dns_ipv6 = ''
            for l in range(8):
                ygg_dns_ipv6 = ygg_dns_ipv6 + str(catch_domain_ipv6[l*4:l*4+4]) + ':'
            ygg_dns_ipv6 = ygg_dns_ipv6[:-1]
        elif match_catch_domain_ipv6.group('ipv6dash'):
            logging.debug('Catched Yggdrasil NS in DASHED format: ' + match_catch_domain_ipv6.group('ipv6dash'))
            ygg_dns_ipv6 = match_catch_domain_ipv6.group('ipv6dash').replace('-', ':')
        try:
            IP(ygg_dns_ipv6).version
            if IP(ygg_dns_ipv6) not in IP('0200::/7'):
                logging.debug(IP(ygg_dns_ipv6).strFullsize() + ' not in 0200::/7 Yggdrasil address space! Reject!')
                return False
            return ygg_dns_ipv6
        except ValueError:
            logging.debug(ygg_dns_ipv6 + ' not an IPv6 address! Reject!')
            return False
    else:
        return False

s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
s.bind((args.address, args.port))

while True:
    # Grap query from wire
    (wire, args.address) = s.recvfrom(512)
    dns_local_query = dns.message.from_wire(wire)
    logging.debug("INPUT QUERY: " + dns_local_query.to_text().replace("\n", " / "))

    # Try to grap IPv6 Yggdrasill address from DNS message
    ygg_dns_ipv6 = catch_ygg_ipv6_address(dns_local_query)

    if ygg_dns_ipv6:
        # Do a query and sent it back to client
        try:
            logging.debug('Retransmit QUERY to node: ' + ygg_dns_ipv6)
            dns_remote_response = dns.query.udp(dns_local_query, ygg_dns_ipv6, args.query_timeout)
            logging.debug("Got RESPONSE: " + dns_remote_response.to_text().replace("\n", " / "))
            s.sendto(dns_remote_response.to_wire(), args.address)
        except dns.exception.Timeout:
            logging.debug("QUERY timeout!")
            continue
        except OSError:
            continue
    # ELSE do a query to bypass nameserver
    else:
        logging.debug('QUERY domain is not in YggNS format!')
        if args.bypass_ns:
            try:
                logging.debug('Retransmit QUERY to bypass DNS resolver: ' + str(args.bypass_ns))
                dns_remote_response = dns.query.udp(dns_local_query, str(args.bypass_ns))
                s.sendto(dns_remote_response.to_wire(), args.address)
            except OSError:
                continue
        else:
            logging.debug('No bypass DNS set! Making an empty RESPONSE!')
            try:
                dns_reject_response = dns.message.make_response(dns_local_query)
                s.sendto(dns_reject_response.to_wire(), args.address)
            except OSError:
                continue
