#!/usr/bin/python3

# Common Modules
import re
import base64
import binascii
import argparse

# Installed Modules
from IPy import IP

args_parser = argparse.ArgumentParser(description='Convert IPv6 Yggdrasil address to domain name or domain name to IPv6 address.')
args_parser.add_argument('input', metavar='INPUT', type=str, help='Yggdrasil node IPv6-address or domain name. If its a IPv6 address, then it will be converted to domain name. If its a domain name then it will be converted to IPv6 address;')
args_parser.add_argument('-f', dest='format', metavar='FORMAT', default='S', type=str, help='To what domain format the address will be converted: (S)TRAIGHT, (B)ASE32 or (D)ASHED. Default is STRAIGHT;')
args_parser.add_argument('-s', dest='subd', metavar='SUBDOMAIN', default='', type=str, help='Add subdomain(s) to your YggNS domain;')
args = args_parser.parse_args()

try:
    args.input = IP(args.input)
    if args.input.version() != 6:
        print(str(args.input) + ' is a IPv4 address!')
        exit()
    
    if args.input not in IP('0200::/7'):
        print(str(args.input) + ' not in 0200::/7 Yggdrasil address space!')
        exit()
    
    if args.subd:
        args.subd = args.subd + '.'
    
    if args.format == 'S':
        print(args.subd + args.input.strFullsize().replace(':', '') + '.ygg.')
    elif args.format == 'B':
        print(args.subd +  args.input.strFullsize()[1] + base64.b32encode(bytearray.fromhex(args.input.strFullsize().replace(':', '')[2:])).decode('ascii').lower() + '.ygg.')
    elif args.format == 'D':
        print(args.subd + args.input.strNormal().replace(':', '-') + '.ygg.')
    exit()

except ValueError:
    re_catch_domain_ipv6 = re.compile("([0-9a-zA-Z\-\_]*\.)*((?P<ipv6>0[2,3]{1}[0-9a-fA-F]{30})|(?P<b32>[2,3]{1}[A-Za-z2-7]{24})|(?P<ipv6dash>0?[2,3]{1}[0-9a-fA-F\-]{0,37}))\.ygg")
    match_catch_domain_ipv6 = re.search(re_catch_domain_ipv6, args.input)
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
            ygg_dns_ipv6 = IP(ygg_dns_ipv6)
            ygg_dns_ipv6.version
            if ygg_dns_ipv6 not in IP('0200::/7'):
                print(ygg_dns_ipv6.strFullsize() + ' not in 0200::/7 Yggdrasil address space!')
                exit()
            print(ygg_dns_ipv6.strFullsize())
            exit()
        except ValueError:
             print('Can not convert that name to IPv6 address!')
             exit()
    else:
        print('That domain name is not in YggNS format or it is invalid!')
        exit()
