commands_list_array=[


               "show version",
               "show ip arp",
               "show ip arp vrf CPE-MGT",
               "show interfaces description",
               "show inventory",
               "show ip inter brief",
               "show ip nat translations",
               "show ip dhcp binding",
               "show standby brief",
               "show ip bgp summ",
               "show ip route",
               "ping vrf CPE-MGT 10.255.250.164 re 5",
               "ping vrf CPE-MGT 10.255.250.166 re 5",
               "ping vrf CPE-MGT 172.18.11.236 re 5",

              ]


'''
terminal length 0
show environment all
#show ip arp vrf DATOS
show mac-address-table
show interfaces trunk
show interfaces
show interfaces | inc error
show interfaces description
show vrrp
show ip bgp neighbors
show ip route
show ip route vrf CPE-MGT
show processes cpu sorted 5min | exclude 0.00%
show crypto ikev2 sa
show crypto ipsec sa
show logging
ping $IP_WAN repeat 1000
#ping vrf DATOS 172.30.28.1 repeat 100
#ping vrf CW_MPLS 10.100.110.41 repeat 100
'''