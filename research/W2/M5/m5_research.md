# Google 검색 크롤링 방식

## 1. requests + BeautifulSoup로 가능한가?

### (1) 시도 결과
	•	Google 검색 결과 HTML을 직접 요청하면:
	•	JavaScript 비활성화 페이지 반환
	•	<noscript> 기반 리다이렉트 페이지 수신
	•	정상적인 div#search 구조를 얻을 수 없음

### (2) 결론
	•	Google 검색 페이지는 Selenium 기반 크롤링 필수

. 상세 페이지 본문 크롤링에 대한 고민

## 2. 단순 HTML 전체 텍스트 추출의 문제점

### (1) 문제
	•	헤더, 푸터, 사이드바, 광고, 메뉴 텍스트가 과도하게 포함됨
	•	실제 후기 본문 대비 노이즈 비율이 매우 높음

### (2) 해결책: readability-lxml 도입
Firefox의 Reader Mode(읽기 모드) 알고리즘을 기반으로 함.

선택 이유
	•	뉴스/블로그/리뷰 페이지에서 본문 중심 추출에 특화
	•	사이트 구조가 달라도 공통적으로 적용 가능
	•	광고·네비게이션 제거에 효과적

적용 방식
	1.	Google 검색 결과에서 얻은 URL로 이동
	2.	readability-lxml로 본문 HTML 추출
	3.	BeautifulSoup으로 불필요 태그 제거
	4.	순수 텍스트만 반환


## 3. Selenium

### (1) Selenium이란

Selenium은 웹 브라우저를 실제로 띄워서 사람이 하는 행동을 코드로 자동화하는 도구.
	•	버튼 클릭
	•	입력창에 키보드 입력
	•	스크롤
	•	마우스 hover
	•	JavaScript 실행 후 렌더링된 DOM 접근

사람이 브라우저로 하는 모든 행동을 코드로 재현

### (2) Selenium이 필요한 이유

#### 1) requests + BeautifulSoup의 한계

requests는 HTML만 받아올 뿐 JavaScript 실행, 동적 렌더링, 클릭 이벤트, SPA(Single Page App)을 가져오지 못함