FROM debian:bullseye

RUN apt -y update && apt -y upgrade && apt -y install sudo && apt -y install wget && apt -y install gnupg
RUN repo_host="http://deb.cloudx.group/bigdata/repo" &&  \
    wget -qO - "${repo_host}/ps-bigdata-cloudx_public_key.gpg" | sudo apt-key add - && \
    echo "deb [arch=amd64] ${repo_host}/ bullseye main" | sudo tee /etc/apt/sources.list.d/cloudx_bigdata.list && \
    sudo apt update
RUN sudo apt -y install gpdb-6
