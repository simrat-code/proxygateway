# ProxyGateway
It is a simple and basic http/https proxy-gateway written in Python3.
Supporting only rely request to target and not implement anything like caching or filters.

It can relay client request to other parent proxy eg squid or cntlm on same/different host.
It can handle multiple clients by using multi-threading ie separate thread for each request.

### following command will show help menu:
python3 run_proxygw.py --help
