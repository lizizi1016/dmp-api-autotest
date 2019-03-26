#!/bin/bash
# ftp setting
ping -c 1 10.186.17.201
if [[ $? == 0 ]]; then
    export FTP_URL="ftp://ftp:ftp@10.186.17.201"
else
    export FTP_URL="ftp://ftp:ftp@10.186.18.20"
fi

# install setting
export UDP_HOME=/opt
export UMC_HOME=${UDP_HOME}/umc
export UMC_ADDR=10.20.30.1
export UMC_PORT=5799

export VERSION=9.9.9.9