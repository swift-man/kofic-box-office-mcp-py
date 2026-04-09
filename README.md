# kofic-box-office-mcp

문화공공데이터광장의 여러 영화/행사 OpenAPI를 Streamable HTTP MCP 서버로 제공하는 파이썬 프로젝트입니다.

- 대상 문서:
  - `영화진흥위원회_박스오피스`: <https://www.culture.go.kr/data/openapi/openapiView.do?id=203>
  - `한국문화예술위원회_행사정보`: <https://www.culture.go.kr/data/openapi/openapiView.do?id=72&category=C&orderBy=rdfCnt&gubun=A>
- 대상 엔드포인트:
  - `https://api.kcisa.kr/openapi/service/rest/meta5/getKFCC0502`
  - `https://api.kcisa.kr/openapi/service/rest/meta/ARKeven`
- 전송 방식: Streamable HTTP MCP only

이 서버는 문화포털 OpenAPI를 LLM과 MCP 클라이언트가 바로 사용할 수 있도록 안정적인 JSON 응답 구조로 감싸 줍니다. 저장소 이름은 KOFIC 기준으로 시작했지만, 현재는 KOFIC 박스오피스와 ARKO 행사정보를 함께 제공합니다.

## 제공 기능

- MCP 도구 `get_kofic_box_office`
- MCP 도구 `search_kofic_box_office`
- MCP 도구 `list_kofic_box_office_titles`
- MCP 도구 `get_arko_events`
- MCP 도구 `search_arko_events`
- MCP 도구 `list_arko_event_titles`
- MCP 리소스 `kofic-box-office://reference`
- MCP 리소스 `arko-events://reference`
- 문화포털 API의 JSON 응답 우선 처리
- JSON 미지원 또는 예외 상황 대비 XML fallback 파싱
- 원본 응답 payload 보존
- 응답 페이지에 대한 로컬 필터링, 검색, 정렬, 제한
- `.env`와 `scripts/run_http.sh` 기반 실행

## 구조

SOLID 관점에서 책임을 아래처럼 분리했습니다.

- `server.py`: MCP 도구 등록과 프로세스 시작
- `bootstrap.py`: settings, parser, gateway, service 조립
- `service.py`: 입력 검증과 유스케이스 처리
- `gateway.py`: 외부 HTTP 호출
- `response_parser.py`: JSON/XML 파싱과 응답 정규화
- `settings.py`: 환경 변수 로딩
- `runtime.py`: Streamable HTTP 런타임 설정
- `reference.py`: 정적 참조 정보
- `validation.py`: 재사용 검증 유틸리티

## 전제 조건

- Python `3.10+`
- 문화공공데이터광장에서 발급한 서비스키

공식 MCP Python SDK v1.x는 Python `>=3.10`을 요구합니다. 이 저장소도 그 기준으로 사용하면 가장 안전합니다.

## 환경 변수

필수:

- `CULTURE_OPEN_API_SERVICE_KEY`: 디코딩된 원본 서비스키
- 또는 `CULTURE_OPEN_API_SERVICE_KEY_ENCODED`: 이미 URL 인코딩된 서비스키

하위 호환:

- `KOFIC_BOX_OFFICE_SERVICE_KEY`
- `KOFIC_BOX_OFFICE_SERVICE_KEY_ENCODED`

선택:

- `KOFIC_BOX_OFFICE_API_BASE`: 기본값 `https://api.kcisa.kr/openapi/service/rest/meta5`
- `KOFIC_BOX_OFFICE_TIMEOUT_SECONDS`: 기본값 `15`
- `ARKO_EVENT_API_BASE`: 기본값 `https://api.kcisa.kr/openapi/service/rest/meta`
- `ARKO_EVENT_TIMEOUT_SECONDS`: 기본값 `15`
- `KOFIC_BOX_OFFICE_MCP_HOST`: 기본값 `127.0.0.1`
- `KOFIC_BOX_OFFICE_MCP_PORT`: 기본값 `8000`
- `KOFIC_BOX_OFFICE_MCP_PATH`: 기본값 `/mcp`
- `KOFIC_BOX_OFFICE_MCP_ALLOWED_HOSTS`: 쉼표 구분 Host 허용 목록
- `KOFIC_BOX_OFFICE_MCP_ALLOWED_ORIGINS`: 쉼표 구분 Origin 허용 목록

예시:

```bash
export CULTURE_OPEN_API_SERVICE_KEY='your-decoded-service-key'
```

## 설치

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 실행

```bash
./scripts/run_http.sh
```

또는:

```bash
python -m kofic_box_office_mcp
```

기본 엔드포인트:

```text
http://127.0.0.1:8000/mcp
```

예를 들어 Claude Code에서는:

```bash
claude mcp add --transport http kofic-box-office http://127.0.0.1:8000/mcp
```

`.env` 파일이 있으면 `scripts/run_http.sh`가 자동으로 읽습니다.

## systemd 등록

예시 유닛 파일:

- `deploy/systemd/kofic-box-office-mcp.service.example`

배포 경로 예시:

```bash
sudo mkdir -p /opt
cd /opt
sudo mv /path/to/kofic-box-office-mcp-py /opt/kofic-box-office-mcp-py
cd /opt/kofic-box-office-mcp-py
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

`.env`에 서비스키를 넣은 뒤 유닛 파일 등록:

```bash
sudo cp deploy/systemd/kofic-box-office-mcp.service.example /etc/systemd/system/kofic-box-office-mcp.service
sudo nano /etc/systemd/system/kofic-box-office-mcp.service
```

수정할 값:

- `User=your-user`
- `Group=your-user`
- `WorkingDirectory=/opt/kofic-box-office-mcp-py`
- `ExecStart=/opt/kofic-box-office-mcp-py/scripts/run_http.sh`

등록 및 시작:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kofic-box-office-mcp
sudo systemctl status kofic-box-office-mcp
```

로그 확인:

```bash
journalctl -u kofic-box-office-mcp -n 50 --no-pager
```

## 도구 설명

### `get_kofic_box_office`

문화포털 `영화진흥위원회_박스오피스` 데이터를 조회합니다.

입력:

- `page_no`: 페이지 번호, 기본값 `1`
- `num_of_rows`: 페이지당 건수, 기본값 `10`
- `query`: 제목, 설명, 제작기관 등 여러 필드에 대한 로컬 검색어
- `creator`: `creator` 필드 부분 일치 필터
- `collection_db`: `collectionDb` 필드 부분 일치 필터
- `subject_keyword`: `subjectKeyword` 필드 부분 일치 필터
- `limit`: 필터링 후 반환할 최대 건수
- `sort_by`: `title`, `creator`, `regDate`, `collectionDb`, `subjectKeyword` 중 정렬 필드
- `sort_order`: `asc` 또는 `desc`

응답:

- `items`: LLM이 바로 쓰기 쉬운 정규화된 항목 목록
- `response_header`: 원본 API `header`
- `response_body`: 원본 API `body`를 유지하면서 `items`만 리스트로 정규화한 값
- `api_payload`: 원본 전체 payload
- `source_item_count`: 원본 페이지에서 받은 항목 수
- `returned_count`: 로컬 필터링/정렬/제한 이후 반환된 항목 수
- `applied_filters`: MCP 서버에서 적용한 로컬 필터 정보
- `applied_sort`: MCP 서버에서 적용한 로컬 정렬 정보

주의:

- `query`, `creator`, `collection_db`, `subject_keyword`, `limit`, `sort_by`, `sort_order`는 상위 문화포털 API 파라미터가 아니라 MCP 서버가 응답 페이지에 대해 로컬로 적용하는 옵션입니다.

### `search_kofic_box_office`

가져온 페이지 안에서 검색어로 빠르게 후보를 찾고, 요약 필드만 간단히 돌려줍니다.

입력:

- `query`: 필수 검색어
- `page_no`: 페이지 번호, 기본값 `1`
- `num_of_rows`: 페이지당 건수, 기본값 `10`
- `limit`: 반환할 최대 건수, 기본값 `5`

응답:

- `items`: `title`, `alternativeTitle`, `creator`, `regDate`, `collectionDb`, `subjectKeyword`, `url` 중심 요약 목록
- `match_fields`: 검색에 사용된 필드 목록
- `returned_count`: 검색 결과 건수

### `list_kofic_box_office_titles`

가져온 페이지를 간단한 제목 목록 뷰로 반환합니다.

입력:

- `page_no`: 페이지 번호, 기본값 `1`
- `num_of_rows`: 페이지당 건수, 기본값 `10`
- `limit`: 반환할 최대 건수, 기본값 `10`

응답:

- `items`: 제목 중심의 요약 목록
- `summary_fields`: 요약에 포함되는 필드 목록
- `returned_count`: 반환 건수

### `get_arko_events`

한국문화예술위원회 `행사정보` 데이터를 조회합니다.

입력:

- `page_no`: 페이지 번호, 기본값 `1`
- `num_of_rows`: 페이지당 건수, 기본값 `10`
- `query`: 제목, 설명, 장소, 키워드 등 여러 필드에 대한 로컬 검색어
- `creator`: `creator` 필드 부분 일치 필터
- `spatial`: `spatial` 필드 부분 일치 필터
- `subject_keyword`: `subjectKeyword` 필드 부분 일치 필터
- `limit`: 필터링 후 반환할 최대 건수
- `sort_by`: `title`, `creator`, `regDate`, `spatial`, `temporalCoverage`, `subjectKeyword` 중 정렬 필드
- `sort_order`: `asc` 또는 `desc`

응답:

- `items`: LLM이 바로 쓰기 쉬운 정규화된 행사 항목 목록
- `response_header`: 원본 API `header`
- `response_body`: 원본 API `body`를 유지하면서 `items`만 리스트로 정규화한 값
- `api_payload`: 원본 전체 payload
- `source_item_count`: 원본 페이지에서 받은 항목 수
- `returned_count`: 로컬 필터링/정렬/제한 이후 반환된 항목 수
- `applied_filters`: MCP 서버에서 적용한 로컬 필터 정보
- `applied_sort`: MCP 서버에서 적용한 로컬 정렬 정보

주의:

- `query`, `creator`, `spatial`, `subject_keyword`, `limit`, `sort_by`, `sort_order`는 상위 문화포털 API 파라미터가 아니라 MCP 서버가 응답 페이지에 대해 로컬로 적용하는 옵션입니다.

### `search_arko_events`

가져온 페이지 안에서 검색어로 빠르게 행사 후보를 찾고, 요약 필드만 간단히 돌려줍니다.

입력:

- `query`: 필수 검색어
- `page_no`: 페이지 번호, 기본값 `1`
- `num_of_rows`: 페이지당 건수, 기본값 `10`
- `limit`: 반환할 최대 건수, 기본값 `5`

응답:

- `items`: `title`, `alternativeTitle`, `creator`, `regDate`, `spatial`, `temporalCoverage`, `subjectKeyword`, `url`, `uci` 중심 요약 목록
- `match_fields`: 검색에 사용된 필드 목록
- `returned_count`: 검색 결과 건수

### `list_arko_event_titles`

가져온 페이지를 간단한 행사 제목 목록 뷰로 반환합니다.

입력:

- `page_no`: 페이지 번호, 기본값 `1`
- `num_of_rows`: 페이지당 건수, 기본값 `10`
- `limit`: 반환할 최대 건수, 기본값 `10`

응답:

- `items`: 행사 제목 중심의 요약 목록
- `summary_fields`: 요약에 포함되는 필드 목록
- `returned_count`: 반환 건수

## 샘플 실행

```bash
curl -G 'https://api.kcisa.kr/openapi/service/rest/meta5/getKFCC0502' \
  --data-urlencode 'serviceKey=YOUR_SERVICE_KEY' \
  --data-urlencode 'pageNo=1' \
  --data-urlencode 'numOfRows=10' \
  -H 'Accept: application/json'
```

## 테스트

```bash
bash -n scripts/run_http.sh
python3 -m compileall src tests
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
