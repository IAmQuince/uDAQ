---
document_id: DOC-280
title: "Networking, IP Addresses, Command Line, and File Transfer Guide"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-280
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# Networking, IP Addresses, Command Line, and File Transfer Guide

280_NETWORKING_IP_ADDRESSES_COMMAND_LINE_FILE_TRANSFER_GUIDE
0. Purpose
This guide explains the practical networking skills we repeatedly need for Raspberry Pi, Windows, PLC, Ethernet, Wi-Fi, instrument-control, and local-device projects.
It covers:
IP addresses
subnets
gateways
DHCP
static IPs
router-assigned addresses
direct Ethernet connections
Raspberry Pi networking
Windows Command Prompt and PowerShell basics
navigating folders from the command line
ping / ipconfig / arp / tracert / netstat
SSH
SCP file transfer
shared folders
Ethernet-connected instruments
PLC-style Ethernet devices
firewall issues
diagnostic workflows

The goal is to make networking predictable instead of mysterious.
Core rule:
Before debugging software, verify the network path.

Can the computer see the device?
Can the device see the computer?
Are they on compatible IP addresses?
Can they ping?
Can the intended port connect?

1. Core Networking Concepts
1.1 IP Address
An IP address identifies a device on a network.
Example:
192.168.1.25

Common private/local IP ranges:
192.168.x.x
10.x.x.x
172.16.x.x through 172.31.x.x

These are used inside homes, labs, shops, offices, and local test networks.
Example devices:
Laptop:       192.168.1.50
Raspberry Pi: 192.168.1.80
PLC:          192.168.1.20
Router:       192.168.1.1

1.2 Subnet Mask
The subnet mask determines which IP addresses are considered local.
Common subnet mask:
255.255.255.0

This usually means devices with the same first three numbers are on the same local subnet.
Example:
Computer: 192.168.1.50
Device:   192.168.1.80
Mask:     255.255.255.0

These can talk locally because both are in:
192.168.1.x

But:
Computer: 192.168.1.50
Device:   192.168.2.80
Mask:     255.255.255.0

These are not on the same local subnet unless routing is configured.
1.3 Gateway
The gateway is usually the router.
Example:
Gateway: 192.168.1.1

Devices use the gateway to reach other networks or the internet.
For direct Ethernet between two devices, a gateway may not be needed.
1.4 DNS
DNS converts names into IP addresses.
Example:
google.com → IP address
raspberrypi.local → Raspberry Pi IP address, if mDNS/hostname resolution works

If pinging an IP works but pinging a name fails, DNS/name resolution may be the issue.
1.5 MAC Address
A MAC address is the hardware/network-interface address.
Example:
B8:27:EB:12:34:56

Routers often use MAC addresses for DHCP reservations.
1.6 Port
A port identifies a specific service on a device.
Examples:
22      SSH
80      HTTP
443     HTTPS
1883    MQTT
502     Modbus TCP
5900    VNC
3389    Remote Desktop
8080    common alternate web server

An IP address finds the device.
A port finds the service on that device.
Example:
192.168.1.80:22

means:
Raspberry Pi at 192.168.1.80, SSH service on port 22

2. DHCP vs Static IP
2.1 DHCP
DHCP means the router automatically assigns an IP address.
This is common for:
laptops
phones
Raspberry Pis on Wi-Fi
normal home devices

Example:
Router assigns Raspberry Pi: 192.168.1.87

Advantage:
easy
automatic
usually works

Disadvantage:
IP address can change
harder for fixed device connections

2.2 Static IP
A static IP is manually assigned.
Example:
PLC: 192.168.1.20
Subnet: 255.255.255.0
Gateway: 192.168.1.1

Advantage:
predictable
good for PLCs, instruments, servers, Raspberry Pi services

Disadvantage:
easy to misconfigure
can conflict with another device

2.3 DHCP Reservation
A DHCP reservation is usually the best middle ground.
The router still assigns the address, but always gives the same IP to the same MAC address.
Use for:
Raspberry Pi
network printer
test station PC
home server
DAQ computer
PLC gateway

Example:
Raspberry Pi MAC address → always gets 192.168.1.80

This avoids changing device-side static IP settings.

3. Basic Windows Command Prompt Navigation
3.1 Open Command Prompt
Press:
Windows key + R

Type:
cmd

Press Enter.
3.2 Open PowerShell
Right-click Start menu and choose:
Terminal
PowerShell
Windows Terminal

depending on Windows version.
3.3 Show current folder
Command Prompt:
cd

PowerShell:
pwd

3.4 List files
Command Prompt:
dir

PowerShell:
ls

3.5 Change folder
cd Desktop

Go to a full path:
cd C:\Users\YourName\Documents

If the path has spaces:
cd "C:\Users\YourName\My Documents"

Change drive:
D:

Change drive and folder at same time:
cd /d D:\Projects\MyProject

3.6 Go up one folder
cd ..

Go up two folders:
cd ..\..

3.7 Create folder
mkdir MyProject

3.8 Copy file
copy source.txt destination.txt

Copy into a folder:
copy source.txt C:\Users\YourName\Documents

3.9 Robust folder copy with robocopy
robocopy source_folder destination_folder /E

Example:
robocopy C:\Users\YourName\Desktop\project D:\backup\project /E

/E includes subfolders, including empty ones.
3.10 Clear screen
cls

3.11 Cancel a running command
Press:
Ctrl + C

4. Basic Windows Network Commands
4.1 Show IP configuration
ipconfig

More detail:
ipconfig /all

Look for:
IPv4 Address
Subnet Mask
Default Gateway
DNS Servers
Physical Address

Example:
IPv4 Address . . . . . . . . . . : 192.168.1.50
Subnet Mask . . . . . . . . . . : 255.255.255.0
Default Gateway . . . . . . . . : 192.168.1.1

4.2 Test if a device responds
ping 192.168.1.80

If it works:
Reply from 192.168.1.80

If it fails:
Request timed out
Destination host unreachable

4.3 Ping by hostname
ping raspberrypi.local

If this fails but IP ping works, name resolution is the problem.
Use the IP address directly.
4.4 Trace route
tracert 8.8.8.8

This shows the route packets take to a destination.
For local device debugging, ping is usually more useful than tracert.
4.5 Show ARP table
arp -a

This shows IP-to-MAC mappings recently seen by the computer.
Useful when looking for local devices.
4.6 Show network connections
netstat -ano

Useful for checking open/listening ports.
PowerShell alternative:
Get-NetTCPConnection

4.7 Show routing table
route print

Useful when a computer has both Wi-Fi and Ethernet and traffic is going the wrong way.

5. PowerShell Network Commands
5.1 Show IP addresses
Get-NetIPAddress

5.2 Show network adapters
Get-NetAdapter

5.3 Test connection
Test-Connection 192.168.1.80

5.4 Test a TCP port
Test-NetConnection 192.168.1.80 -Port 22

This is extremely useful.
Examples:
Test-NetConnection 192.168.1.80 -Port 22
Test-NetConnection 192.168.1.80 -Port 1883
Test-NetConnection 192.168.1.20 -Port 502

If ping works but port test fails, the device exists but the service is not reachable.

6. Basic Network Diagnostic Flow
Use this order:
1. Check cable or Wi-Fi connection.
2. Run ipconfig.
3. Identify your computer IP.
4. Identify target device IP.
5. Confirm same subnet.
6. Ping target device.
7. Test target service port.
8. Check firewall.
9. Check service is running.
10. Only then debug application code.

Example:
ipconfig
ping 192.168.1.80

Then:
Test-NetConnection 192.168.1.80 -Port 22

If all of that works, SSH should probably work.

7. Direct Ethernet: Computer to Raspberry Pi
This is a common workflow:
Windows laptop Ethernet port
    → Ethernet cable
        → Raspberry Pi Ethernet port

No router is involved.
This can work in several ways:
automatic link-local addresses
static IP on both devices
internet connection sharing
small travel router/switch

The most predictable method is static IP on both devices.
7.1 Static direct Ethernet example
Set Windows Ethernet adapter to:
IP address: 192.168.10.1
Subnet mask: 255.255.255.0
Gateway: leave blank
DNS: leave blank

Set Raspberry Pi Ethernet to:
IP address: 192.168.10.2
Subnet mask: 255.255.255.0
Gateway: leave blank or 192.168.10.1 only if routing through PC
DNS: leave blank unless internet sharing is configured

Then from Windows:
ping 192.168.10.2

SSH:
ssh pi@192.168.10.2

or:
ssh username@192.168.10.2

Use the actual Raspberry Pi username.
7.2 Direct Ethernet rules
Both devices need IPs in the same subnet.
Only one device should use a given IP.
Gateway is not needed for simple direct connection.
Firewall may block ping or file sharing.
SSH must be enabled on the Raspberry Pi.

8. Raspberry Pi Networking
8.1 Find Raspberry Pi IP from the Pi
On the Pi:
hostname -I

More detail:
ip addr

Show routes:
ip route

8.2 Check Wi-Fi
iwconfig

or:
nmcli device status

depending on Raspberry Pi OS version/configuration.
8.3 Ping from Pi
ping 192.168.1.1

Ping internet:
ping 8.8.8.8

Ping DNS name:
ping google.com

Interpretation:
Can ping router but not internet:
    gateway or router issue.

Can ping 8.8.8.8 but not google.com:
    DNS issue.

Cannot ping router:
    local network issue.

8.4 Enable SSH
On modern Raspberry Pi OS, enable SSH using:
Raspberry Pi Imager advanced settings
raspi-config
Raspberry Pi configuration tool

Command line:
sudo raspi-config

Then:
Interface Options
    SSH
        Enable

Check SSH service:
sudo systemctl status ssh

Start it:
sudo systemctl start ssh

Enable at boot:
sudo systemctl enable ssh

9. SSH
9.1 What SSH does
SSH gives command-line access to another computer over the network.
Example:
Windows laptop
    → SSH
        → Raspberry Pi terminal

9.2 SSH from Windows
Try:
ssh username@192.168.1.80

Example:
ssh pi@192.168.1.80

or:
ssh username@192.168.1.80

If hostname works:
ssh username@raspberrypi.local

If hostname fails, use IP.
9.3 First connection warning
The first time you connect, SSH may ask if you trust the host.
If the IP/device is correct, type:
yes

9.4 Exit SSH
exit

10. SCP File Transfer
10.1 Copy file from Windows to Raspberry Pi
From Windows Command Prompt or PowerShell:
scp local_file.py username@192.168.1.80:/home/username/

Example:
scp main.py username@192.168.1.80:/home/username/

10.2 Copy file from Raspberry Pi to Windows
Run from Windows:
scp username@192.168.1.80:/home/username/data.csv .

The final . means current Windows folder.
Example:
scp username@192.168.1.80:/home/username/logs/data.csv .

10.3 Copy a folder recursively
scp -r project_folder username@192.168.1.80:/home/username/

From Pi to Windows:
scp -r username@192.168.1.80:/home/username/project_folder .

10.4 Important SCP rule
Run scp from the computer that has access to both:
the file path
the network target

If you are in Windows and copying to Pi, use Windows paths for local files.
If you are SSH’d into the Pi, you are no longer in Windows. You are operating inside the Pi.

11. SFTP and WinSCP
For users who prefer a graphical file-transfer tool, use WinSCP.
Typical connection settings:
Protocol: SFTP
Host: Raspberry Pi IP address
Port: 22
Username: Pi username
Password: Pi password

Use WinSCP when:
you want drag-and-drop file transfer
you do not want to type scp commands
you are moving many files manually

Use scp when:
you want repeatable command-line instructions
you are scripting transfers
you are documenting exact commands

12. Windows Shared Folders
Windows file sharing can work, but it introduces permissions, firewall, and network-profile issues.
Use when:
multiple Windows computers need shared files
a Raspberry Pi needs to mount a Windows share
large files need to be moved repeatedly

Simpler alternatives:
SCP
WinSCP
USB drive
Git repository
local web server

For quick Raspberry Pi file transfer, SSH/SCP is usually cleaner than Windows SMB sharing.

13. Quick Local Web Server for File Transfer
Sometimes the easiest way to transfer files is to serve a folder temporarily.
On the computer containing the files:
cd C:\Users\YourName\Downloads\folder_to_share
python -m http.server 8000

Find the computer IP:
ipconfig

On another device browser:
http://192.168.1.50:8000

Stop server:
Ctrl + C

Use this for:
quick downloads
offline local file sharing
temporary documentation server
moving files to old systems

Caution:
Anyone on the same network may be able to access the served folder while the server is running.
Only serve folders you intend to share.

14. Ethernet Instruments and PLC-Style Devices
Many instruments and PLCs communicate over Ethernet.
Common protocols/ports:
Modbus TCP:       502
HTTP web UI:      80 or 8080
HTTPS web UI:     443
Vendor protocol:  device-specific
SCPI over LAN:    often 5025 or vendor-specific
MQTT:             1883
OPC UA:           often 4840

Always check the device manual.
14.1 PLC-style static IPs
PLCs and industrial Ethernet devices often ship with fixed or default IPs.
Examples:
192.168.0.10
192.168.1.10
192.168.250.1
10.0.0.1

If your computer is not on the same subnet, you may not be able to reach the device.
Example:
PLC:      192.168.0.10
Computer: 192.168.1.50
Mask:     255.255.255.0

These are different subnets.
To connect, temporarily set computer Ethernet to:
IP:      192.168.0.50
Mask:    255.255.255.0
Gateway: blank

Then:
ping 192.168.0.10

14.2 Do not randomly change PLC IP settings
Before changing a PLC/device IP:
record current IP
record subnet mask
record gateway
record device name
record project file
record how to restore connection

Changing the wrong IP can make the device hard to find.
14.3 Isolated industrial network rule
Do not casually bridge PLC/test-equipment networks to the internet or home Wi-Fi.
Safer pattern:
Laptop Ethernet → PLC/test device isolated network
Laptop Wi-Fi    → internet/router

But this can create routing/firewall confusion.
Be careful when a PC has both Wi-Fi and Ethernet active.

15. Computer with Wi-Fi and Ethernet at the Same Time
This is common:
Wi-Fi:
    internet/router

Ethernet:
    Raspberry Pi / PLC / instrument / isolated device

Example:
Wi-Fi adapter:     192.168.1.50
Ethernet adapter:  192.168.10.1
Pi direct cable:   192.168.10.2

This is good because the subnets are different.
Avoid:
Wi-Fi adapter:     192.168.1.50
Ethernet adapter:  192.168.1.60

unless you know what you are doing, because Windows may route traffic unpredictably.
Rule:
Use different subnets for different networks.

Home Wi-Fi:
    192.168.1.x

Direct Ethernet test network:
    192.168.10.x

PLC test network:
    192.168.20.x

16. Static IP on Windows Ethernet Adapter
Use Windows settings:
Settings
    Network & Internet
        Advanced network settings
            More network adapter options

or:
Control Panel
    Network and Sharing Center
        Change adapter settings

Then:
Right-click Ethernet
Properties
Internet Protocol Version 4 (TCP/IPv4)
Properties
Use the following IP address

Example direct Ethernet static IP:
IP address:      192.168.10.1
Subnet mask:     255.255.255.0
Default gateway: blank
DNS:             blank

After setting, verify:
ipconfig

17. Static IP on Raspberry Pi
The exact method depends on Raspberry Pi OS version and network manager configuration.
General approaches:
Raspberry Pi Imager advanced settings
desktop network settings
NetworkManager / nmcli
dhcpcd.conf on older setups
router DHCP reservation

Preferred when possible:
Use router DHCP reservation for normal network use.
Use temporary static IP for direct Ethernet test networks.

For direct Ethernet, using a desktop/network settings GUI may be easier than editing config files.
Always record the original settings before changing them.

18. Finding Devices on a Network
18.1 Router client list
Often easiest:
Log into router
Find connected devices/client list
Look for hostname or MAC address

Raspberry Pi hostnames may appear as:
raspberrypi
raspberrypi.local
custom hostname

18.2 arp -a
On Windows:
arp -a

This shows recently seen devices.
You may need to ping the subnet first.
18.3 Ping sweep with PowerShell
Example for 192.168.1.x:
1..254 | ForEach-Object {
    $ip = "192.168.1.$_"
    if (Test-Connection

GUI Development
