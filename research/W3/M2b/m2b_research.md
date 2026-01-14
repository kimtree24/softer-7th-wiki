# W3 M2b — Hadoop Config Automation & Verification

## 핵심 구조
- config/ 는 호스트에서 관리
- docker-compose로 config를 컨테이너에 마운트
- modify-config.py는 호스트에서 실행하여 XML 수정
- Hadoop 서비스는 컨테이너 내부에서 재시작

## 왜 Dockerfile에 COPY config가 있어도 되는가
초기 이미지 기본값 제공용. 실제 운영 값은 volume 마운트가 덮어씀.