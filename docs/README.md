# Dual Tetris 문서 생성 가이드

이 디렉토리는 Sphinx를 사용하여 Dual Tetris 프로젝트의 문서를 생성합니다.

## 설치

문서 생성에 필요한 패키지를 설치합니다:

```bash
pip install -r requirements.txt
```

또는 개별 설치:

```bash
pip install sphinx sphinx-rtd-theme
```

## 문서 생성

### HTML 문서 생성 (권장)

Windows:
```bash
make.bat html
```

생성된 HTML 문서는 `_build/html/index.html`에서 확인할 수 있습니다.

### 다른 형식으로 생성

PDF (LaTeX 필요):
```bash
make.bat latexpdf
```

ePub:
```bash
make.bat epub
```

Markdown:
```bash
make.bat markdown
```

### 문서 빌드 정리

```bash
make.bat clean
```

## 문서 보기

HTML 문서가 생성된 후, 브라우저로 다음 파일을 엽니다:

```
docs\_build\html\index.html
```

또는 PowerShell에서:

```powershell
Start-Process docs\_build\html\index.html
```

## 문서 구조

- `conf.py` - Sphinx 설정 파일
- `index.rst` - 메인 문서 페이지
- `modules.rst` - 모듈 자동 문서화 설정
- `_build/` - 생성된 문서 (git에서 제외)
- `_static/` - 정적 파일 (이미지, CSS 등)
- `_templates/` - 커스텀 템플릿

## 자동 문서화

Sphinx의 autodoc 확장을 사용하여 Python 소스 코드의 docstring에서 자동으로 문서를 생성합니다.

코드에 작성된 모든 클래스, 함수, 메서드의 docstring이 자동으로 HTML 문서로 변환됩니다.

## 테마

현재 사용 중인 테마: **Read the Docs (sphinx_rtd_theme)**

테마를 변경하려면 `conf.py`의 `html_theme` 변수를 수정하세요.

사용 가능한 테마:
- `alabaster` (기본)
- `sphinx_rtd_theme` (현재)
- `nature`
- `pyramid`
- `haiku`
- `traditional`

## 문서 업데이트

코드를 수정한 후 문서를 업데이트하려면:

1. 코드의 docstring을 업데이트
2. `make.bat clean` 실행
3. `make.bat html` 실행

문서가 자동으로 갱신됩니다.
