# kofic-box-office-mcp

문화공공데이터광장 `영화진흥위원회_박스오피스` OpenAPI를 Streamable HTTP MCP 서버로 제공하는 파이썬 프로젝트입니다.

- 대상 문서: <https://www.culture.go.kr/data/openapi/openapiView.do?id=203>
- 대상 엔드포인트: `https://api.kcisa.kr/openapi/service/rest/meta5/getKFCC0502`
- 전송 방식: Streamable HTTP MCP only

이 서버는 문화포털 OpenAPI를 LLM과 MCP 클라이언트가 바로 사용할 수 있도록 안정적인 JSON 응답 구조로 감싸 줍니다.

## 제공 기능

- MCP 도구 `get_kofic_box_office`
- MCP 리소스 `kofic-box-office://reference`
- 문화포털 API의 JSON 응답 우선 처리
- JSON 미지원 또는 예외 상황 대비 XML fallback 파싱
- 원본 응답 payload 보존
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

- `KOFIC_BOX_OFFICE_SERVICE_KEY`: 디코딩된 원본 서비스키
- 또는 `KOFIC_BOX_OFFICE_SERVICE_KEY_ENCODED`: 이미 URL 인코딩된 서비스키

선택:

- `KOFIC_BOX_OFFICE_API_BASE`: 기본값 `https://api.kcisa.kr/openapi/service/rest/meta5`
- `KOFIC_BOX_OFFICE_TIMEOUT_SECONDS`: 기본값 `15`
- `KOFIC_BOX_OFFICE_MCP_HOST`: 기본값 `127.0.0.1`
- `KOFIC_BOX_OFFICE_MCP_PORT`: 기본값 `8000`
- `KOFIC_BOX_OFFICE_MCP_PATH`: 기본값 `/mcp`
- `KOFIC_BOX_OFFICE_MCP_ALLOWED_HOSTS`: 쉼표 구분 Host 허용 목록
- `KOFIC_BOX_OFFICE_MCP_ALLOWED_ORIGINS`: 쉼표 구분 Origin 허용 목록

예시:

```bash
export KOFIC_BOX_OFFICE_SERVICE_KEY='your-decoded-service-key'
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

응답:

- `items`: LLM이 바로 쓰기 쉬운 정규화된 항목 목록
- `response_header`: 원본 API `header`
- `response_body`: 원본 API `body`를 유지하면서 `items`만 리스트로 정규화한 값
- `api_payload`: 원본 전체 payload

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
