#!/bin/bash
set -e

# 시스템 업데이트
dnf update -y

# Docker 설치
dnf install -y docker

# Docker 서비스 시작
systemctl enable docker
systemctl start docker

# ec2-user를 docker 그룹에 추가
usermod -aG docker ec2-user