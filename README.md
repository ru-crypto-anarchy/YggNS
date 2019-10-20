### YggNS

DNS-proxy for clumsy and distributed NS-system for Yggdrasil network.

## Idea

In my opinion there is always trade-off between decentralization and centralization in case of domain naming. If domain name is random-like generated from node address and tied to it then it may be distributed across the network without centralization relatively simple. Examples are TOR and I2P. If you want fancy and short domain name then you must register it and tie it to exact identity in hierarchy-like systems like DNS.

For Yggdrasil I want to try some kind of hybrid system. Good old DNS distributed over the network Yggdrasil.

Each node in the Yggdrasil network has an IPv6 address that is associated with the node cryptographically and never changes, no matter where in the network the node is located. Thus, if this IPv6 address is static, it is possible to functionally and inextricably map it to a static domain name.

If the host address for example is `0201:9d54:3c57:d6d2:e8d7:a8ce:841f:eb89`, then it is possible to functionally map it to domain name `02019d543c57d6d2e8d7a8ce841feb89.ygg.'. That is simply IPv6 address in the expanded writing without the symbol `:` in the domain of the second level. Then what can be the methods of domain name resolution?

The most obvious is to simply perform the reverse conversion. Take a second-level domain and make it an IPv6 address. Very simple, but this approach has a drawback. The host owner is deprived of the freedom to flexibly manage the records of his domain name. In this case, you can apply a slightly different approach.

So, if we want to resolve the domain name `02019d543c57d6d2e8d7a8ce841feb89.ygg.` , then we can take from it the IPv6 part `02019d543c57d6d2e8d7a8ce841feb89` and convert it back to the IPv6 address `0201:9d54:3c57:d6d2:e8d7:a8ce:841f: eb89`, and then send a normal DNS query to the DNS server on the host with this address. The host must run a regular DNS server to resolve the address and send back a response. This leaves the host owner with the flexibility to manage his domain. For example, if the domain name is `02019d543c57d6d2e8d7a8ce841feb89.ygg.` administrator can choose not to resolve it at all (send NXDOMAIN), allow only certain types of requests, or resolve names such as ' example.02019d543c57d6d2e8d7a8ce841feb89.ygg.' to another IPv6 address of another node, say '0202:12a9:00e5:4474:d473:82be:16ac:9381`, and then client go to the service of this domain name to another node controlled by same administrator.

In general, it turns out that each node is a DNS server itself. Only the DNS server of the domain name is bound to the node, not the domain itself. The administrator can manage his domain and subdomains at will.

Why do a Yggdrasill network need it?

Couple of reasons:

1) Run services in Yggdrasil network that generally need DNS. Most services can work with direct IP connection, but their functionality will be limited. Some services can not work without DNS.

2) When domain names is needed then most stable solution is to use DNS servers in the Internet. When you have a domain name in the Internet, you can make an AAAA record for IPv6 address in the Yggdrasil network. Example is `y.netwhood.online` resolves to `202:12a9:e5:4474:d473:82be:16ac:9381`. In that case if you want to use DNS __inside the Yggdrasil network__ you __must__ own a domain name __in the Internet__ to use services with DNS supportion.

## Principle of operation and name formats

The principle of operation was described above, but we will reveal in detail. At first about name formats. All domain names must be in the TLD zone `.ygg`. YggNS offers 3 formats:

1) STRAIGHT. 32-symbol fixed format. Derived from the fully disclosed (with __all__ zeros) IPv6 address of the node, but with removed colons `:`. For example address `202:12a9:e5:4474:d473:82be:16ac:9381` must be fully disclosed to `0202:12a9:00e5:4474:d473:82be:16ac:9381` and then colons removed and TLD added. Result is `020212a900e54474d47382be16ac9381.ygg.`.

2) BASE32. 25-symbol fixed format. From the fully disclosed (with __all__ zeros) IPv6 address of the node removed first invariable hex-symbol `0`, second hex-symbol (2 or 3) is fixed, and remaining 120 bits is encoded by base32 to 25 ASCII symbols. For example `202:12a9:e5:4474:d473:82be:16ac:9381` converted to `2aijksahfir2ni44cxylkze4b.ygg.`.

3) DASHED. Variable length format, depending on node IPv6 address. Derived from squeezed IPv6 address by replacing `:` to dashes `-`. For example `202:12a9:e5:4474:d473:82be:16ac:9381` converted to `202-12a9-e5-4474-d473-82be-16ac-9381.ygg.`.

When an IPv6 address is taken from the domain name (and checked for validity and belonging to the 0200::/7 subnet), in any of the formats, the __original request without transformations is redirected__ to the DNS server at this IPv6 address. DNS server on the node can be absolutely any - dnsmasq, unbound, bind and others. The choice may depend on the administrator's requirements for functionality or ease of configuration. So, this DNS server resolves the request and sends back a response to the client. The client receives the resolved request and goes to the IPv6 address from the response.

## How to use it

You need python3 and installed libraries dnspython and IPy.

```
pip3 install dnspython
pip3 install IPy
```

Then you need to start __yggns.py__ script. By default it will listen to socket __[::1]:53535__. You need to forward requests for __.ygg__ TLD to that socket.

On Linux is recommended to use it with local recursive resolvers with cache like dnsmasq or dnscrypt. Zone resolving for __.ygg__ must be forwarded to __[::1]:53535__.

For __dnscrypt__ you must configure it in file `forwarding-rules.txt`:

```
ygg [::1]:53535
```

And in `dnscrypt-proxy.toml` you must set forwarding rules file:

```
forwarding_rules = '/etc/dnscrypt-proxy/forwarding-rules.txt'
```

In __dnsmasq__ it may be configured like this:

```
server=/ygg/::1#53535
```

To run __yggns.py__ in background you can execute:

```
nohup yggns.py 2>/dev/null &
```

If you can not use local recursive resolvers you can run YggNS with bypass DNS server. Queries that is not for YggNS will be redirected to that bypass DNS server. Perhaps you will need to run it by root user to listen to port 53.

```
nohup yggns.py -p 53 -b 8.8.8.8 2>/dev/null &
```

Then you must set OS DNS server to __::1__.

__For domain name generation__  you can use __yggns-tool.py__ script. If you input IPv6-address it will output to use formated domain name. By default format is STRAIGHT. You can set format by -f option: (S)TRAIGHT, (B)ASE32 или (D)ASHED.

If you input domain name then script will output IPv6-address.

You can use __any__ DNS server on service node side. 

Example config for __dnsmasq__:

```
listen-address=201:9d54:3c57:d6d2:e8d7:a8ce:841f:eb89
host-record=02019d543c57d6d2e8d7a8ce841feb89.ygg,201:9d54:3c57:d6d2:e8d7:a8ce:841f:eb89
host-record=netwhood.02019d543c57d6d2e8d7a8ce841feb89.ygg,202:12a9:e5:4474:d473:82be:16ac:9381
host-record=2agovipcx23jorv5iz2cb724j.ygg,201:9d54:3c57:d6d2:e8d7:a8ce:841f:eb89
host-record=netwhood.2agovipcx23jorv5iz2cb724j.ygg,202:12a9:e5:4474:d473:82be:16ac:9381
host-record=201-9d54-3c57-d6d2-e8d7-a8ce-841f-eb89.ygg,201:9d54:3c57:d6d2:e8d7:a8ce:841f:eb89
host-record=netwhood.201-9d54-3c57-d6d2-e8d7-a8ce-841f-eb89.ygg,202:12a9:e5:4474:d473:82be:16ac:9381

```

Example config for __unbound__:

```
local-zone:     "02019d543c57d6d2e8d7a8ce841feb89.ygg" redirect
local-data:     "02019d543c57d6d2e8d7a8ce841feb89.ygg. AAAA 201:9d54:3c57:d6d2:e8d7:a8ce:841f:eb89"
local-data-ptr: "201:9d54:3c57:d6d2:e8d7:a8ce:841f:eb89 02019d543c57d6d2e8d7a8ce841feb89.ygg"
```

### What to try

Test sites:

http://02019d543c57d6d2e8d7a8ce841feb89.ygg/

http://2agovipcx23jorv5iz2cb724j.ygg/

http://201-9d54-3c57-d6d2-e8d7-a8ce-841f-eb89.ygg/

netwhood.online mirrors:

http://netwhood.02019d543c57d6d2e8d7a8ce841feb89.ygg/

http://netwhood.2agovipcx23jorv5iz2cb724j.ygg/

http://netwhood.201-9d54-3c57-d6d2-e8d7-a8ce-841f-eb89.ygg/
~                                                           

