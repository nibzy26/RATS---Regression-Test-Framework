# RATS---Regression-Test-Framework
Regression Automated Testing System

Introduction:
This framework is designed to automate various manual test that were carried out on IP based Radio Units.
Traffic both voice (T1/E1) and Data Packets Ethernet from customer sites get sent to remote side or to the core of Network over Radio links utilising various modulation schemes.

Tests that were Automated:

1 - Software Upgradation on Remote Radio Sites
2 - Generate Data Traffic on one of the ports and detect Bit Error Rates on The remote side
3 - Change modulation schemes from 64 QAM to 256 QAM
4 - Adaptive Modulation test
5 - Fade Margin Test
6 - Link Aggregation in which we combine two or more radio units to increase link capacity
7 - Synchronous Ethernet Test
8 - QoS (Quality of Service) for bits transmitted
9 - Traffic Shaping
10 Traffic Scheduling
11 - E1 Wayside Chnannel which uses Management channel to carry data traffic.
12 - Traffic Hit detection on configuration change

Python Modules Used:
Tests have heavy dependance on various python modules including
Pysnmp - SNMP Protocol implementation in Python



