#!/bin/bash
function update_net_issue {
    destf=/etc/issue.d/netissue.issue
    motdf=/etc/motd.d/netissue.motd
    # echo "$event"
    echo; echo [$(date)]
    ipwarn=""; gwwarn=""; dhwarn=""; pingresult=1
    rt=$(ip route)
    gw=$(echo "$rt" | grep -oP "^default via \K[0-9\.]*" | head -n1)
    dv=$(echo "$rt" | grep -oP "^default .* dev \K\S*" | head -n1)
    ip=$(echo "$rt" | grep -oP "^default .* src \K\S*" | head -n1)
    dhcp=$(echo "$rt" | grep -oP "^default .* \Kdhcp" | head -n1)
    # echo dv:"$dv" ip:"$ip" dhcp:"$dhcp" gw:"$gw" 
    if [ "$ip" == "" ]; then
       ip=$(ip --brief a | grep -oP "$dv\s*UP\s*\K[0-9\.]+" | head -n1)
    fi
    if [ "$ip" != "" ]; then
        wmsline=$(echo "WMS (Weka Management Server) home page is http://$ip:8501")
        echo $wmsline 
        echo $wmsline > $destf
        echo $wmsline > $motdf
        echo
        echo >> $destf
        echo >> $motdf
    else
        echo > $destf
        echo > $motdf
    fi
    [ "$ip" == "" ] && ipwarn="Error: No ip address found for host; please set up networking with nmtui or nmcli"
    [ "$dhcp" == "dhcp" ] && dhwarn=$(echo "Warning: Device $dv ($ip) is using dhcp. Please set a static address with nmcli or nmtui, or reserve the IP on your DHCP server")

    if [ "$gw" == "" ]; then
        gwwarn="Error: No gateway found; please set a gateway with nmcli or nmtui"
    else
        pingresult=$(echo "ping -c 2 -l 2 -w 1 $gw")
        [ $? != 0 ] && gwwarn=$(echo "Error: Ping to gateway $gw failed")
    fi

    [ "$ipwarn" != "" ] && echo $ipwarn 
    [ "$gwwarn" != "" ] && echo $gwwarn 
    [ "$dhwarn" != "" ] && echo $dhwarn 
    [ "$ipwarn" != "" ] && echo $ipwarn >> $destf
    
    [ "$gwwarn" != "" ] && echo $gwwarn >> $destf
    [ "$gwwarn" != "" ] && echo $gwwarn >> $motdf

    [ "$dhwarn" != "" ] && echo $dhwarn >> $destf
    [ "$dhwarn" != "" ] && echo $dhwarn >> $motdf    
}

update_net_issue

ip monitor address | while read event; do
    update_net_issue
done
