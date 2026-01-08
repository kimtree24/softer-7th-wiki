# W2 Crawling Project

## Project Structure

```
W2/
├── README.md
├── requirements.txt
└── src/
    ├── crawlers/
    │   ├── meeting_blind_crawler.py #블라인드 게시물 크롤러
    │   ├── sdm_google_crawler.py    #구글 검색 크롤러
    │   └── blog_naver_crawler.py    #네이버 블로그 게시물 크롤러
    ├── config/
    │   ├── blind_crawler.yaml       
    │   └── worldcloud.yaml
    └── notebooks/
        ├── blind_wordcloud.ipynb.  #블라인드 상견례 게시물 분석
        ├── blog_wordcloud.ipynb    #네이버 블로그 웨딩홀 게시물 분석
        └── google_wordcloud.ipynb. #구글 스드메(스튜디오, 드레스, 메이크업)관련 게시물 분석
```

## Setup

```bash
pip install -r src/requirements.txt
playwright install  # For naver_crawler only
```

## Usage

### Crawlers

**Blind Meeting Crawler**
```bash
python src/crawlers/meeting_blind_crawler.py
```

**Google SDM Crawler**
```bash
python src/crawlers/sdm_google_crawler.py
```

**Naver Blog Crawler**
```bash
python src/crawlers/blog_naver_crawler.py
```

### Notebooks

**Blind WordCloud**
```bash
jupyter lab src/notebooks/blind_wordcloud.ipynb
```

**Blog WordCloud**
```bash
jupyter lab src/notebooks/blog_wordcloud.ipynb
```

**Google WordCloud**
```bash
jupyter lab src/notebooks/google_wordcloud.ipynb
```
