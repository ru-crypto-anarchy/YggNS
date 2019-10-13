### YggNS

DNS-proxy for clumsy and distributed NS-system for Yggdrasil network.

## Here is the idea

In my opinion, in DNS there is always trade-off between distribution and centralization from domain naming perspective. If domain name is random-like generated from node address in network, you can relatively easy it distribute accross the network. Examples are TOR and I2P networks. When you want fancy and short domain name you must register it and tie it to some identity in hierarchy-like systems like DNS.

For Yggdrasil, i want to try some kind of hybrid system. Good old DNS that is overlayed and distributed across Yggdrasil network.

Every node in Yggdrasil network have an IPv6-address that is tied to node cryptographically and have not to change accross the network, regardless to what peer nodes it connected. If that address is static, we can map it to static domain-name that is functionally mapped to that IPv6-address.

If node address is something like this: `201:9d54:3c57:d6d2:e8d7:a8ce:841f:eb89`, we can map to it unique domain name like this `02019d543c57d6d2e8d7a8ce841feb89.ygg.`. If we want to resolve domain name `02019d543c57d6d2e8d7a8ce841feb89.ygg.` we can grab from it IPv6 part `02019d543c57d6d2e8d7a8ce841feb89` and convert it to IPv6 address `201:9d54:3c57:d6d2:e8d7:a8ce:841f:eb89`, and send DNS-query to DNS-server on node with that address. Then, why do we need to resolve it when it's already mapped? Well, we can resolve names like this: `example.02019d543c57d6d2e8d7a8ce841feb89.ygg.` and go for it to address `201:9d54:3c57:d6d2:e8d7:a8ce:841f:eb89/7`, but DNS-server on that node can resolve it to another IPv6-address, lets say `202:12a9:e5:4474:d473:82be:16ac:9381`, so we can go for service on this domain name to another node. One administrator can distribute services across multiple nodes, that he or she ownes.

### How to try it

You need python3 and installed library dnspython.

Just start it. DNS-proxy is started on address [::1]:53535 by default. Domain names that are not in YggNS format bypassed to common DNS server. By default it's 8.8.8.8.

Options are inside the script.

Probably, you must start it as root to make script listen at 53 port. Or you can use simple DNS-servers like dnsmasq or unbound to redirect YggNS query through the script.

### What to try

Test site is at http://02019d543c57d6d2e8d7a8ce841feb89.ygg
