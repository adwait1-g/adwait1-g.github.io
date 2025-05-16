---
title: Installing moloch!
categories: moloch
comments: true
layout: post
---

By now, you would know what moloch is. The following is how you install moloch on your machine. 

Before starting the install, I'd like to give an overview of the architecture. 

moloch has 3 parts.
1. A  **capturer** which captures the packets from interface(s).
2. A **database and search engine** that is used to store packets' metadata and searching for them - DB+SearchEngine
3. A **viewer** which offers a web-interface where you can search packets, monitor etc.,

Let us see what these three are.

1. The capturer is an application written in C.
2. The database+search engine used is the famous [elasticsearch](https://www.elastic.co/products/elasticsearch). 
3. The viewer is a nodejs app.

So, we need to setup all these three to get started with moloch.

## 1. Download and run elasticsearch as a non-root user

Yes, you heard it. Non-root user, probably yourself. You can do the following.
I am installing version 6.5.4 . You can choose any available version and do the same.

```
$ wget http://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.5.4.zip
--2019-05-22 03:02:23--  http://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.5.4.zip
Resolving proxy.esl.cisco.com (proxy.esl.cisco.com)... 64.102.255.40, 2001:420:620::5
Connecting to proxy.esl.cisco.com (proxy.esl.cisco.com)|64.102.255.40|:8080... connected.
Proxy request sent, awaiting response... 302 Found
Location: https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.5.4.zip [following]
--2019-05-22 03:02:27--  https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.5.4.zip
Connecting to proxy.esl.cisco.com (proxy.esl.cisco.com)|64.102.255.40|:8080... connected.
Proxy request sent, awaiting response... 200 OK
Length: 113405994 (108M) [application/zip]
Saving to: ?elasticsearch-6.5.4.zip?

elasticsearch-6.5.4.zip     100%[=========================================>] 108.15M   449KB/s    in 4m 11s  

2019-05-22 03:06:39 (442 KB/s) - ?elasticsearch-6.5.4.zip? saved [113405994/113405994]

$ unzip elasticsearch-6.5.4.zip
.
.
Stuff gets unzipped
.
.
$ ls
elasticsearch-6.5.4  elasticsearch-6.5.4.zip
```

At this point, you have elasticsearch with you. 

You have downloaded it. Now, start it. Execute the following.
```
$ cd elasticsearch-6.5.4/bin
elasticsearch               elasticsearch-env.bat            elasticsearch-service-x64.exe      elasticsearch-translog.bat
elasticsearch.bat           elasticsearch-keystore           elasticsearch-setup-passwords      elasticsearch-users
elasticsearch-certgen       elasticsearch-keystore.bat       elasticsearch-setup-passwords.bat  elasticsearch-users.bat
elasticsearch-certgen.bat   elasticsearch-migrate            elasticsearch-shard                x-pack
elasticsearch-certutil      elasticsearch-migrate.bat        elasticsearch-shard.bat            x-pack-env
elasticsearch-certutil.bat  elasticsearch-plugin             elasticsearch-sql-cli              x-pack-env.bat
elasticsearch-cli           elasticsearch-plugin.bat         elasticsearch-sql-cli-6.5.4.jar    x-pack-security-env
elasticsearch-cli.bat       elasticsearch-saml-metadata      elasticsearch-sql-cli.bat          x-pack-security-env.bat
elasticsearch-croneval      elasticsearch-saml-metadata.bat  elasticsearch-syskeygen            x-pack-watcher-env
elasticsearch-croneval.bat  elasticsearch-service.bat        elasticsearch-syskeygen.bat        x-pack-watcher-env.bat
elasticsearch-env           elasticsearch-service-mgr.exe    elasticsearch-translog
```

This has scripts to run on different platforms and other stuff too(which I didn't bother to look into). I am able to see **elasticsearch** and **elasticsearch.bat** which are for Linux and Windows respectively. Let us run the script for Linux.

```
$ ./elasticsearch
.
.
A lot of stuff comes in. Read through it. It is very interesting!
.
.
```

You can verify that elasticsearch is running by opening your browser and going to here: ```http://127.0.0.1:9200``` . You will see a proper webpage if everything goes right.


At this point, you have elasticsearch up and running.

Why did we need to run elasticsearch as a non-root user?

* It is because it runs a webserver and running a webserver as root is not very secure. 
* I also tried installing v2.4.0 as root. There was an option to be used along with it, where you explicitly tell elasticsearch that you want to run it as root. But, later versions, it was disabled I think. 

## 2. Installing moloch as root

Now, Lets install moloch. The latest version available at the time of writing this is 1.8.0. So, I'm downloading that.
```
$ wget https://files.molo.ch/builds/ubuntu-18.04/moloch_1.8.0-1_amd64.deb
--2019-05-22 03:13:48--  https://files.molo.ch/builds/ubuntu-18.04/moloch_1.8.0-1_amd64.deb
Resolving proxy.esl.cisco.com (proxy.esl.cisco.com)... 173.36.224.109, 2001:420:620::5
Connecting to proxy.esl.cisco.com (proxy.esl.cisco.com)|173.36.224.109|:8080... connected.
Proxy request sent, awaiting response... 200 OK
Length: 49945822 (48M) [application/x-debian-package]
Saving to: ?moloch_1.8.0-1_amd64.deb?

moloch_1.8.0-1_amd64.deb    100%[=========================================>]  47.63M  17.7MB/s    in 2.7s    

2019-05-22 03:13:51 (17.7 MB/s) - ?moloch_1.8.0-1_amd64.deb? saved [49945822/49945822]
```

Now, run the following as **root**. You have to install stuff.
```
# dpkg -i moloch_1.8.0-1_amd64.deb 
(Reading database ... 231704 files and directories currently installed.)
Preparing to unpack moloch_1.8.0-1_amd64.deb ...
Unpacking moloch (1.8.0-1) ...
Setting up moloch (1.8.0-1) ...
READ /data/moloch/README.txt and RUN /data/moloch/bin/Configure
```

moloch is installed. 

But, it is not yet ready to run. It needs some configuration to be done. Lets do it.

Let us do **RUN /data/moloch/bin/Configure** first and then  **READ /data/moloch/README.txt**. 

```
# cd /data/moloch/bin
# ./Configure
Found interfaces: enp10s0;enp1s0f0;lo;lxcbr0;veth_0;veth_1;virbr0
Semicolon ';' seperated list of interfaces to monitor [eth1] eth1     <---- You specify the interface(s) which you want to monitor. I have just given eth1.
Install Elasticsearch server locally for demo, must have at least 3G of memory, NOT recommended for production use (yes or no) [no] no    <---- Because we already have elasticsearch. Also, it will be downloaded and run as root which is bad.
Elasticsearch server URL [http://localhost:9200] http://localhost:9200
Password to encrypt S2S and other things [no-default] qwerty
Moloch - Creating configuration files
Installing systemd start files, use systemctl
Download GEO files? (yes or no) [yes] yes
Moloch - Downloading GEO files
WARNING: timestamping does nothing in combination with -O. See the manual
for details.

2019-05-22 03:15:35 URL:https://updates.maxmind.com/app/update_secure?edition_id=GeoLite2-Country [1909174/1909174] -> "GeoLite2-Country.mmdb.gz" [1]
WARNING: timestamping does nothing in combination with -O. See the manual
for details.

2019-05-22 03:15:35 URL:https://updates.maxmind.com/app/update_secure?edition_id=GeoLite2-ASN [3606288/3606288] -> "GeoLite2-ASN.mmdb.gz" [1]
2019-05-22 03:15:35 URL:https://raw.githubusercontent.com/wireshark/wireshark/master/manuf [1578163/1578163] -> "oui.txt" [1]

Moloch - Configured - Now continue with step 4 in /data/moloch/README.txt

      /sbin/start elasticsearch # for upstart/Centos 6/Ubuntu 14.04
      systemctl start elasticsearch.service # for systemd/Centos 7/Ubuntu 16.04
 5) Initialize/Upgrade Elasticsearch Moloch configuration
  a) If this is the first install, or want to delete all data
      /data/moloch/db/db.pl http://ESHOST:9200 init
  b) If this is an update to moloch package
      /data/moloch/db/db.pl http://ESHOST:9200 upgrade
 6) Add an admin user if a new install or after an init
      /data/moloch/bin/moloch_add_user.sh admin "Admin User" THEPASSWORD --admin
 7) Start everything
   a) If using upstart (Centos 6 or sometimes Ubuntu 14.04):
      /sbin/start molochcapture
      /sbin/start molochviewer
   b) If using systemd (Centos 7 or Ubuntu 16.04 or sometimes Ubuntu 14.04)
      systemctl start molochcapture.service
      systemctl start molochviewer.service
 8) Look at log files for errors
      /data/moloch/logs/viewer.log
      /data/moloch/logs/capture.log
 9) Visit http://MOLOCHHOST:8005 with your favorite browser.
      user: admin
      password: THEPASSWORD from step #6
```

And 75% of moloch is configured. We need to do the last part.
Lets follow the above steps. They are part of README.txt which we don't have to read after we do this.

**Step 5**: Leave it. elasticsearch is peacefully running. So, do not disturb it.

**Step 6**: This is important. Do it as root.
```
/data/moloch/bin/moloch_add_user.sh admin "Admin User" qwerty1234 --admin
```

You use an **Admin User** with name **admin** and password **qwerty1234**. If you are playing around with it, the pasword is ok. If not, please change it to whatever feels safe.

**That is it**. At this point, everything is configured and ready. We need to run moloch.

**Step 7**: Start the viewer. **Do not** start the capture part.
```
# systemctl start molochviewer.service
```
viewer is the web interface where all packets is shown in a particular manner. It is written in nodejs.
 
**Ideally**, the viewer should be running. Just check if it is running. 
```
# systemctl status molochviewer.service
molochviewer.service - Moloch Viewer
   Loaded: loaded (/etc/systemd/system/molochviewer.service; disabled; vendor preset: enabled)
   Active: active (running) since Wed 2019-05-22 03:15:27 PDT; 4h 45min ago
 Main PID: 7979 (sh)
    Tasks: 11 (limit: 4915)
   CGroup: /system.slice/molochviewer.service
           ??7979 /bin/sh -c /data/moloch/bin/node viewer.js -c /data/moloch/etc/config.ini  >> /data/moloch/logs/viewer.log 2>&1
           ??7985 /data/moloch/bin/node viewer.js -c /data/moloch/etc/config.ini
# 
```

That **active (running)** is damn important. it says, it is running. 

Now, the viewer is ready. elasticsearch which is the database and search engine is running and ready. We just need to start capturing packets. That can be done in the following manner.

1. Go to **/data/moloch/bin**
```
# cd /data/moloch/bin
# Configure  moloch_add_user.sh  moloch-capture  moloch_config_interfaces.sh  moloch_update_geo.sh  node  npm  npx  taggerUpload.pl 
```

Do you see that **moloch-capture**? That is the executable responsible for capturing packets and writing it into pcap files. It is like the **tcpdump** executable. Lets go ahead and run it.

```
# ./moloch-capture -c ../etc/config.ini
.
.
A bunch of stuff
.
.
which doesn't stop..
```

If it doesn't stop(it will if there is any error), then you are set. 

Now, it is time to view the captured packets. I never mentioned which IPAddr:PortNo the viewer is hosted on. By default, moloch uses **127.0.0.1:8005**. This detail is present in **/data/moloch/etc/config.ini** file. You can change it to anything you want.

Open up the browser and type in **http://127.0.0.1:8005**. If the viewer is fine, you'll get a window asking for **username** and **password**. I have set it as **admin** and **qwerty1234**. I use it and it will show me the **http://127.0.0.1:8005/sessions**. 

If you see a GUI and packets coming in, you are done.

At this point, **moloch** is up and running!

----------------------------------
The following are a few places we(my friends and me) got stuck while installing and running moloch.

### 1. Running elasticsearch as a non-root user

This is important. You know why.

### 2. The "started too quickly" error

In my opinion, this is bound to happen for the following reason assuming there is no problem in the viewer code.

Once you stop a service(or it fails for some reason), you cannot restart it again till some time passes. There is a minimum time interval after which you can try running again. This is systemd's properties. You can always check if the service is running from the following command.
```
# systemctl status molochviewer.service
```

If it gives a **active (running)**, then nothing to worry. But, sometimes you also get the "service start request repeated too quickly, refusing to start" error. **systemd** puts a limit on things like how many times can you run in a given time interval, time difference between 2 start attempts etc., We should be able to run instantly. We don't need this restriction to be there. To do that, you can do the following. 

1. Go to place where the configuration file of molochviewer is present.

```
# cd /etc/systemd/system
# ls
... Some services and 
molochviewer.service
```

2. Open that file and add **StartLimitInterval=0** in the **[ Services ]** subheader(if you want to call it that.) 

```
[Unit]
Description=Moloch Viewer
After=network.target

[Service]
Type=simple
Restart=on-failure
StandardOutput=tty
EnvironmentFile=-/data/moloch/etc/molochviewer.env
ExecStart=/bin/sh -c '/data/moloch/bin/node viewer.js -c /data/moloch/etc/config.ini ${OPTIONS} >> /data/moloch/logs/viewer.log 2>&1'
WorkingDirectory=/data/moloch/viewer
StartLimitInterval=0   <---- Newly added by me

[Install]
WantedBy=multi-user.target
```

Note that all this must be done as root. 

3. Notify **systemd** that a change in configuration file of one of the services has been made. 
```
# systemctl daemon-reload
```

After this, you are free from that error.

[This](https://serverfault.com/questions/845471/service-start-request-repeated-too-quickly-refusing-to-start-limit) stackoverflow answer explains it better. 

### 3. How do you read existing pcap files?

[Moloch faq answers this](https://molo.ch/faq#how-do-i-import-existing-pcaps). But I want to elaborate a little bit. This is what it says.
```
# {moloch_dir}/bin/moloch-capture -c [config_file] -r [pcap_file]
```

Normally, it translates to this.
```
# /data/moloch/bin/moloch-capture -c ../etc/config.ini -r path/to/your/file.pcap
.
.
And it outputs some interesting stuff.
.
.
```

I expected it to be ready in the viewer and went to http://127.0.0.1:8005. It was not there.

Where should I search these packets now? I had no clue. 

Solution: There is a **tags** feature in moloch. You can associte a packet with a tag - tag is like another piece of metadata related to a packet. 

So, while reading that pcap file, add this **tags** option too. This way, all packets inside that pcap file have a **unique tag** which you can use to search these packets. 
```
# /data/moloch/bin/moloch-capture -c ../etc/config.ini -r path/to/your/file.pcap --tag some_tag
```

Now, go to the viewer. There are 2 things to do.

1. There is a **Search bar** on the top where you can search for packets. It is basically like **filters** in Wireshark. Go ahead and put the filter **tags == some_tag**. 

2. On **top left below the search bar**, you have a space where you can specify the time like - Last hour, Last 72 hours, All etc.,

     * Select **All**. So, out of all packets, that tags filter is applied. 

This way, you see packets that are in that file.

**Andy Wick**, the developer suggested this on slack. I felt its a very friendly group and you can ask stuff without hesitation.

### 4. Checkout the config.ini file

This has a lot of important parameters to set, sometimes default might not suit you. It is generally present in ```/data/moloch/etc/config.ini``` .  

It has IPAddr:Port where viewer has to be rendered, It has parameters which decide when to write the captured packets into a pcap file, it has session-related details and way more than this.

Just check it out.


Only these many for now. I'll add them or share links if it is present in documentation.
