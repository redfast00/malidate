# Malidate

An opensource logging DNS, HTTP and HTTPS server. Can be used to search for exploits with malformed HTTP requests as described in [this whitepaper ](http://blog.portswigger.net/2017/07/cracking-lens-targeting-https-hidden.html). There exists commercial software to do this (Burpsuite and the Burpsuite collaborator server), but that software isn't opensource.

## Requirements

An HTTPS wildcard Certificate, an a domain set up to use the IP address this server is running on as DNS server.

## Architecture

This project (malidate) is the server. When looking for vulnerabilities, clients can use any subdomain that is at least 17 characters long of the domain the malidate server is running on. Each client SHOULD prefix the subdomain they are using with a random alphanumeric string that is at least 16 characters long.

### Endpoints

`https://export.domain.com/prefix`: all history about lookups and HTTP requests starting with that prefix are returned as JSON data. Since the prefix is unique and not trivially guessable, this will only return the lookups with your prefix.

## Setup

```
sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-ports 10443
sudo iptables -t nat -A PREROUTING -p tcp --dport 53 -j REDIRECT --to-ports 10053
sudo iptables -t nat -A PREROUTING -p udp --dport 53 -j REDIRECT --to-ports 10053
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 10080
```

or, for debugging on the loopback interface
```
iptables -t nat -I OUTPUT -p tcp -d 127.0.0.1 --dport 80 -j REDIRECT --to-ports 8080
```