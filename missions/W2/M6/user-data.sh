#!/bin/bash
set -e

# 시스템 업데이트
yum update -y

# Docker 설치
amazon-linux-extras install docker -y

# Docker 서비스 시작
systemctl start docker
systemctl enable docker

# ec2-user를 docker 그룹에 추가
usermod -aG docker ec2-user

# 재부팅
reboot