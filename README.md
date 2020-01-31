# TrafficMonitor
Traffic Monitor is a proxy application developed using python that allows intercepting HTTP and HTTPS connections between desktop browser and a web server using a typical man-in-the-middle attack(MITM).

Similar to other proxies (such as burp suite), it accepts connections from client and forward them to the destination server.

The goal of traffic monitor is to intercept the HTTP and HTTPS requests and response and save it to the database so later the captured traffic can be replayed.

# Usage
* Install the packages from dist folder using pip
* After installing run the command "trafficmonitor"

# Common Issues
1) if unable to capture the host traffic 
	
- install mitmproxy certificate by accessing "mitm.it" when traffic monitor is running
- check the proxy settings
- if unable to capture traffic using firefox browser change firefox proxy settings to "System Proxy Settings"