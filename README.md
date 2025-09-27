# Mobile Pi Router

---
# Purpose
Dealing with public Wi-Fi is almost always a pain. Signing into a 
portal that doesn’t always work properly on every device -- your phone, 
laptop, tablet, e-reader, watch, and more is error-prone, 
and it’s an easy way to end up accidentally adding pricey internet 
fees depending on your service. Some Wi-Fi only allows a single device 
per room! Most won’t let your devices communicate with each other, and 
if they do, they may well present a security risk.

The idea is you only need to configure your personal devices once to 
connect to the Raspberry Pi’s hotspot. Then, whenever you travel, you 
only have to connect the Raspberry Pi itself to each new Wi-Fi, 
instead of reconfiguring every device individually.

This repo intends to build upon the excellent tutorial from the Raspberry Pi Foundation: https://www.raspberrypi.com/tutorials/host-a-hotel-wifi-hotspot/


# Overview

1. **Public Wi-Fi side (WAN):**

   * A public DHCP server gives the **Raspberry Pi** a single IP address (just like it would for one laptop).
   * That’s the only address the public network “knows about” and allows. Where number
   of allowed clients is limited, this is the one that counts.

2. **Hotspot side (LAN):**

   * The Raspberry Pi runs its own DHCP server (through NetworkManager).
   * It creates a **private subnet** (for example, `192.168.4.x`).
   * Each connected device (laptop, phone, tablet) gets its own private IP from the Pi.

3. **Translation (NAT):**

   * When your devices talk to the internet, the Pi rewrites their source addresses so they all appear to come from the Pi’s one public IP.
   * Replies come back to that one public IP, and the Pi then maps them to the correct private device.

Like what a home router does — the Pi is just acting as a **router + NAT gateway**.

---
### Table of Contents
1. [How NAT Works on Your Raspberry Pi Router](#how-nat-works-on-your-raspberry-pi-travel-router)
   - [Starting Point](#starting-point)
   - [Step-by-Step NAT Process (on the Pi)](#step-by-step-nat-process-on-the-pi)
     - [1. Device Sends Packet](#1-device-sends-packet)
     - [2. Pi’s NAT Table (iptables / nftables)](#2-pis-nat-table-iptables--nftables)
     - [3. Packet Rewriting (SNAT – Source NAT)](#3-packet-rewriting-snat--source-nat)
     - [4. Internet Reply Comes Back](#4-internet-reply-comes-back)
     - [5. Firewall Role](#5-firewall-role)
   - [Why NAT Makes All Devices Look Like One](#why-nat-makes-all-devices-look-like-one)
   - [Analogy](#analogy)
   - [Credits](#credits)
---

# How NAT Works on Your Raspberry Pi Router

<details>
    <summary>Expand me</summary>
    
When using your Raspberry Pi as a travel router, it employs **Network Address Translation (NAT)** 
to allow multiple devices to share a single public IP address.

## Starting Point
***IP addresses are for example purposes:***

* Your Pi has **two interfaces**:

    * **LAN side (wlan0)** → your devices (private subnet, e.g. `192.168.4.0/24`)
  * **WAN side (wlan1 or LTE HAT)** → public Wi-Fi or carrier (public IP, e.g. `203.0.113.25`)

  * **Goal:** When your laptop (`192.168.4.10`) or phone (`192.168.4.11`) 
    sends traffic to the internet, it must *all appear to come from the 
    Pi’s single public IP (`203.0.113.25`)*.
</details>

---

## Step-by-Step NAT Process (on the Pi)
<details>
    <summary>Expand me</summary>

### 1. Device Sends Packet

* Your laptop wants to visit `example.com`.
* It sends:

  ```
  Source IP: 192.168.4.10
  Dest IP:   93.184.216.34   (example.com)
  Source Port: 50000
  Dest Port:   443 (HTTPS)
  ```
* The packet goes to the Pi (default gateway at `192.168.4.1`).

---

### 2. Pi’s NAT Table (iptables / nftables)

* The Pi checks its **NAT translation table**.

* If this is a new connection, the Pi **creates a mapping**:

  | Internal Device       | Internal IP:Port   | Translated Public IP:Port |
  | --------------------- | ------------------ | ------------------------- |
  | Laptop (192.168.4.10) | 192.168.4.10:50000 | 203.0.113.25:40001        |
  | Phone (192.168.4.11)  | 192.168.4.11:50001 | 203.0.113.25:40002        |

* This way, the Pi knows how to rewrite each packet uniquely, 
even if multiple devices connect to the same site.

---

### 3. Packet Rewriting (SNAT – Source NAT)

* The Pi **rewrites** the packet header:

  ```
  Source IP: 203.0.113.25    (Pi’s WAN IP - it's public IP address)
  Dest IP:   93.184.216.34
  Source Port: 40001         (randomly assigned by NAT)
  Dest Port:   443
  ```
* The public Wi-Fi only sees traffic coming from `203.0.113.25`. It never sees the private `192.168.4.x` addresses.

---

### 4. Internet Reply Comes Back

* The server replies to `203.0.113.25:40001`.
* The Pi checks its NAT table, sees that `40001` was mapped to `192.168.4.10:50000`.
* It **rewrites** the packet back:

  ```
  Source IP: 93.184.216.34
  Dest IP:   192.168.4.10
  Dest Port: 50000
  ```
* Your laptop receives the reply as if it had talked to the server directly.

---

### 5. Firewall Role

* NAT usually runs with a firewall (iptables rules).
* By default, **only traffic that matches an existing NAT table entry is allowed back in**.
* This means your laptop can initiate connections *out*, but strangers on the internet cannot directly initiate connections *into* your laptop.
</details>


---

## All Devices Look Like One

<details>
    <summary>Expand me</summary>

* To the public network:
  * Only one IP (`203.0.113.25`) and one MAC address (Pi’s Wi-Fi interface) exist.
  * Hotel DHCP only sees the Pi.
* To your devices:
  * They each have their own private IPs (`192.168.4.10`, `.11`, etc.).
* The Pi is doing the “magic” translation in between.
</details>

---

## Analogy

Think of NAT like a **mail forwarding office**:

* You (laptop) send a letter with your private apartment number on it.
* The office (Raspberry Pi) replaces it with its street address (public IP) so the outside world only sees one address.
* When replies come in, the office looks at its logbook (NAT table) to see which apartment (device) the mail was originally for, and forwards it.

---

# Credits
* Original idea inspired by various travel router projects and tutorials online.
* Thanks to the Raspberry Pi community for continuous support and innovation.
* https://www.raspberrypi.com/tutorials/host-a-hotel-wifi-hotspot/

