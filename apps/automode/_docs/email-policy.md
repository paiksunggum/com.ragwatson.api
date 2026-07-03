# Gmail → n8n → 백엔드 실시간 전송 하네스

> Gmail로 들어온 메일을 실시간(Push) 또는 주기적(Polling)으로 감지해 n8n을 거쳐 자체 백엔드(FastAPI)로 전달하는 시스템 구축 절차. 두 번의 실제 구축 세션을 통합·정리한 재사용 가능한 런북(runbook).

---

## 0. 아키텍처 개요

```
Gmail 새 메일
   │
   ▼
Google Cloud Pub/Sub (토픽 + Push 구독)
   │  (Pub/Sub는 인터넷 공개 HTTPS로만 push 가능)
   ▼
Cloudflare Tunnel (localhost → 공개 HTTPS)
   │
   ▼
n8n Webhook 노드
   │  (Pub/Sub 알림엔 메일 내용이 없고 historyId만 있음)
   ▼
n8n: Gmail "메일 조회" 노드 (historyId/최신 메일 조회)
   │
   ▼
n8n: HTTP Request 노드 → 백엔드 API 호출 (POST 권장)
   │
   ▼
FastAPI 백엔드 (/receive 등 수신 엔드포인트)
```

**두 가지 감지 방식 비교**

| 방식 | 지연 | 난이도 | 비용 | 비고 |
|---|---|---|---|---|
| 폴링 (Gmail Trigger, Poll) | 최대 1분 | 낮음 | 무료 | n8n 기본 노드만으로 완결. 실시간이 꼭 필요 없으면 이걸로 충분 |
| Push (Pub/Sub) | 거의 실시간 | 높음 | 무료(소량) | 공개 HTTPS 엔드포인트 필수, watch 7일 만료, 인프라 복잡도 증가 |

실시간성이 꼭 필요하지 않다면 **폴링으로 끝내는 것을 권장**. Push는 아래 전 단계를 다 거쳐야 완성됨.

---

## 1. 사전 조건 확인

- [ ] n8n을 어디서 돌릴 것인가 → **셀프호스팅(Docker) 무료 권장** (n8n Cloud는 유료)
- [ ] n8n과 백엔드가 같은 컴퓨터/네트워크에 있는가
- [ ] 백엔드가 외부에서 접근 가능한 공개 주소를 가지고 있는가, 아니면 로컬인가
- [ ] "홈페이지로 전송"의 목적: (a) DB 저장 후 화면 표시 / (b) 단순 데이터 수신 / (c) 기존 파이프라인과 연결
- [ ] 도메인 소유 여부 (Cloudflare Named Tunnel 고정 URL 사용 가능 여부 결정)

---

## 2. n8n 셀프호스팅 (무료)

```bash
docker run -d --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

- `http://localhost:5678` 접속 → 최초 1회 계정 생성
- 워크플로우/실행 횟수 제한 없음 (커뮤니티 에디션)

---

## 3. (폴링 방식) Gmail Trigger 노드 설정

> 실시간이 필요 없다면 여기서 끝내고 4~7단계는 건너뛰어도 됨.

1. 새 워크플로우 생성 (기존 워크플로우와 섞지 말 것 — 독립된 흐름으로 추가)
2. `+` → **Gmail** 검색 → 목록 하단 **Triggers** 섹션의 **On message received** 선택
   - ⚠️ Gmail(send) 노드와 다름. 액션 노드 목록에선 트리거가 안 보일 수 있으니, Gmail 클릭 후 하위 Triggers 섹션에서 찾을 것
3. Credential: 기존 Gmail 계정이 있으면 재사용 가능 (신규 OAuth 발급 불필요)
4. 설정값: `Poll Times = Every Minute`, `Event = Message Received`, `Simplify = ON`
5. **Fetch Test Event** / **Test this trigger**로 실제 메일 수신 확인
6. 출력 필드 확인: `Subject`, `From`, `To`, `snippet`, `id` 등 (Simplify ON 상태 기준)

이후 뒤에 **HTTP Request 노드**를 붙여 백엔드로 전송하면 완결 (7단계 형식 참고).

---

## 4. (Push 방식) 공개 HTTPS 확보 — Cloudflare Tunnel

```bash
brew install cloudflared          # 최초 1회
cloudflared tunnel --url http://localhost:5678 &
```

- 실행 시 출력되는 `https://xxxxx.trycloudflare.com` 이 공개 주소
- 상태 확인: `curl -s -o /dev/null -w "%{http_code}" https://xxxxx.trycloudflare.com`

**Quick Tunnel vs Named Tunnel**

| 종류 | URL | 도메인 필요 | 특징 |
|---|---|---|---|
| Quick Tunnel | 랜덤(`*.trycloudflare.com`) | ❌ | 즉시 사용 가능, 재시작마다 URL 변경 → Pub/Sub 구독 URL도 매번 갱신 필요 |
| Named Tunnel | 고정 | ✅ (Cloudflare 등록 도메인) | 안정적, 운영 단계에서 권장 |

- Google Pub/Sub는 push 대상 도메인의 **소유권 검증을 요구하지 않음** (공개 HTTPS + 유효 SSL 인증서만 있으면 됨) → `trycloudflare.com` 서브도메인도 사용 가능

⚠️ **터널 지속성 주의**: 터미널/세션이 죽으면 터널도 죽어 push가 끊김. 상시 운영하려면 `launchd`(macOS) 등록 또는 도메인 구매 후 Named Tunnel로 전환 권장.

---

## 5. n8n Webhook 노드 (Push 수신구)

1. `+` → **Webhook** (기본 노드, "On webhook call") 추가 — 기존 흐름에 잇지 말고 독립적으로 배치
2. 설정:
   - Method: `POST`
   - Path: `gmail-push` (자동생성 UUID를 알아보기 쉬운 값으로 교체)
   - Authentication: `None` (초기 테스트용, 운영 시 강화 고려)
   - Respond: `Immediately`
3. 최종 공개 주소 = `<터널 URL>/webhook/gmail-push`
4. `⌘S` 저장

---

## 6. Google Cloud Pub/Sub 설정

### 6-1. 토픽 생성
- Cloud Console → Pub/Sub → API 활성화(최초 1회) → **Topics** → **CREATE TOPIC**
- Topic ID: 예) `gmail-push` (실제 적용값)
- "기본 구독 추가" 체크 해제 (구독은 아래에서 직접 생성)

### 6-2. Gmail에 발행 권한 부여 (필수, 빠지면 push 자체가 안 옴)
- 생성된 토픽 → **Permissions** → **ADD PRINCIPAL**
- 주 구성원: `gmail-api-push@system.gserviceaccount.com` (Google 고정값)
- 역할: **Pub/Sub Publisher**
- 저장

### 6-3. Push 구독 생성
- **Subscriptions** → **구독 만들기**
- Subscription ID: 예) `gmail-push-sub`
- Topic: 위에서 만든 토픽 선택
- 전송 유형: **Push** (기본값 Pull이므로 반드시 변경)
- 엔드포인트 URL: `<터널 URL>/webhook/gmail-push` (실제 적용: `https://n8n.paiksunggum.com/webhook/gmail-push`)
- 인증 사용: 끔 (초기), 페이로드 래핑: 끔 (표준 형식 유지)

### 6-4. 비용
- Pub/Sub 월 10GiB 무료 — Gmail 알림은 건당 수백 바이트라 사실상 $0
- GCP가 결제 계정(카드) 등록을 요구할 수 있으나, 무료 한도 내면 실제 청구 없음

---

## 7. Gmail watch 등록 (Push 스위치 ON)

n8n **HTTP Request 노드**로 1회 호출 (기존 흐름과 독립적으로 추가):

| 항목 | 값 |
|---|---|
| Method | POST |
| URL | `https://gmail.googleapis.com/gmail/v1/users/me/watch` |
| Authentication | Predefined Credential Type → Gmail OAuth2 API → 기존 Gmail account |
| Send Body | ON, Content Type: JSON |

Body:
```json
{
  "topicName": "projects/<PROJECT_ID>/topics/gmail-push",
  "labelIds": ["INBOX"]
}
```

- **Execute step** 실행 → 성공 시 `{ "historyId": "...", "expiration": "..." }` 응답 (expiration ≈ 7일 후)
- 403(Insufficient Permission) 발생 시 Gmail credential에 `gmail.readonly` 스코프 추가 후 재인증

> 이 시점부터 새 메일이 오면 Pub/Sub → 터널 → n8n Webhook까지 실제로 데이터가 도착함. 폴링 트리거는 더 이상 필요 없으므로 삭제 권장.

### Pub/Sub가 실제로 보내는 데이터 형태
```json
{
  "message": {
    "data": "<base64: {\"emailAddress\":\"...\",\"historyId\":숫자}>",
    "messageId": "...",
    "publishTime": "..."
  },
  "subscription": "projects/.../subscriptions/gmail-push-sub"
}
```
→ `message.data`를 base64 디코딩하면 `{emailAddress, historyId}`만 나옴. 실제 제목/발신자/본문은 이 값을 이용해 Gmail API로 **다시 조회**해야 함.

---

## 8. 메일 조회 → 백엔드 전송 노드

Webhook 뒤에 이어붙임:

1. **Gmail 노드 (Get many messages 등)** — historyId 기준 또는 최신 메일 1건 조회
2. **HTTP Request 노드** — 백엔드로 전송
   - Body Content Type: JSON
   - Specify Body: `Using Fields Below` 또는 `Using JSON` (표현식 모드 `fx` 필요)
   - 예시 필드 매핑:

   | Name | Value |
   |---|---|
   | subject | `{{ $json.Subject }}` |
   | from | `{{ $json.From }}` |
   | to | `{{ $json.To }}` |
   | preview | `{{ $json.snippet }}` |
   | messageId | `{{ $json.id }}` |

   - JSON 직접 입력 시 표현식 전체를 `{{ }}`로 감싸야 함 (바깥에 별도 `{ }` 추가 금지):
   ```
   {{ JSON.stringify({ subject: $json.Subject, from: $json.From, to: $json.To, preview: $json.snippet, messageId: $json.id }) }}
   ```
3. 백엔드 엔드포인트가 아직 없다면 `webhook.site`의 임시 주소로 먼저 검증 후, 실제 백엔드 URL로 교체

---

## 9. watch 갱신 자동화 (7일 만료 대응)

Push 방식 사용 시 필수. 별도 독립 가지로 추가:

```
Schedule Trigger (매일 1회) → HTTP Request (watch 재호출, 6번과 동일 설정)
```

- Schedule Trigger: `Days`, 1일마다, 임의 시각(예: 새벽 3시)
- HTTP Request: 7단계와 동일한 URL/Body (고정값 JSON, 표현식 아님)
- watch는 여러 번 호출해도 안전 — 만료 타이머만 리셋됨
- 활성화(`Publish`) 후 방치해도 매일 자동 갱신됨

---

## 10. 백엔드(FastAPI) 연동 — 실제 구현 (`apps/automode`)

위 런북대로 구축을 마치고 실제로 완성한 파이프라인. 아래는 더미가 아니라 지금 라이브로 동작 중인 코드다.

**엔드포인트**: `POST /api/automode/receive` (`adapter/inbound/api/v1/receiver_router.py`)

```python
@receiver_router.post("", response_model=ReceivedEmailResponse)
async def receive_email(
    schema: ReceivedEmailRequest,
    use_case: ReceiverUseCase = Depends(get_receiver_use_case),
) -> ReceivedEmailResponse:
    result = await use_case.receive(
        ReceivedEmailCommand(
            subject=schema.subject,
            body=schema.body,
            sender=schema.sender,
            source=schema.source,
            message_id=schema.message_id,
        )
    )
    ...
```

**요청 스키마** (`ReceivedEmailRequest`): `subject`, `body`, `sender`, `source`, `message_id`(선택) — 8절에서 언급한 `Subject/From/snippet/id`를 n8n이 `subject/sender/body/message_id`로 매핑해서 전달.

**저장 파이프라인**: `ReceivedEmailPgVectorRepository`가 `save()` 호출 시
1. `message_id`가 이미 저장돼 있으면 재저장 없이 기존 결과 반환 (Pub/Sub 재전달로 인한 중복 방지, 12절 함정 참고)
2. BGE-M3(Ollama, `bge_m3_embedding_client.py`)로 제목+본문 임베딩 생성 (1024차원)
3. `automode_received_emails` 테이블(pgvector)에 INSERT

**조회용 엔드포인트**: `GET /api/automode/receive` — 저장된 이메일 목록 반환 (`list_emails`)

**n8n 쪽 실제 연결**: `Webhook`(`paik-orchestrator`) 노드에서 `스팸 분류`와 **병렬로** `pgvector 저장` HTTP Request 노드를 붙여서, 스팸 여부와 무관하게 모든 수신 메일이 저장되도록 구성함.

---

## 11. 비용 정리 (전체 무료 확인)

| 구성요소 | 비용 | 근거 |
|---|---|---|
| n8n 셀프호스팅 | 무료 | 커뮤니티 에디션, 무제한 |
| Gmail API (watch/조회) | 무료 | 개인 사용량으로 할당량 초과 불가능 |
| Pub/Sub | 무료 | 월 10GiB 무료 한도, 실사용량은 월 몇 KB |
| Cloudflare Tunnel | 무료 | Named Tunnel(`paiksunggum.com`)로 전환 완료 — 도메인 비용만 별도, 터널 자체는 무료 |
| Schedule Trigger 갱신 | 무료 | n8n + API 호출뿐 |

n8n Cloud를 쓰거나 Gmail을 비정상적으로 대량 호출하는 경우에만 유료화됨 (개인 사용 시 해당 없음).

**실제로 적용한 구성**: `api.paiksunggum.com`(백엔드), `n8n.paiksunggum.com`(n8n) 두 개의 Public Hostname을 같은 Named Tunnel에 등록해서 씀. Cloudflare 대시보드 → Networks → Tunnels → 터널 선택 → 경로 추가 → "게시된 애플리케이션"으로 각각 등록 (서비스 URL은 `http://host.docker.internal:<포트>`, cloudflared가 docker-compose 네트워크 밖의 독립 컨테이너라서 이렇게 우회 필요).

---

## 12. 알아둘 함정 (Troubleshooting)

- **Gmail(send) vs Gmail Trigger**: 이름이 비슷해 혼동하기 쉬움. 트리거는 노드 목록 하단 Triggers 섹션에 있음
- **패널이 "다음 노드 추천" 모드일 때** 트리거가 안 보임 → Esc로 닫고 캔버스 빈 공간에서 `+`로 다시 검색
- **노드 창의 X = 저장 아님**: 설정은 유지되나 디스크 저장은 캔버스의 `Save`/`⌘S`를 눌러야 함
- **Publish 전에는 Production Webhook이 죽어있음**: 트리거 뒤에 노드가 비어있는 상태로 Publish하면 감지만 되고 아무 데도 안 감
- **n8n 표현식 문법**: `{{ }}` 두 겹, 바깥에 추가 중괄호 넣지 말 것. 문자열 내 따옴표는 자동 이스케이프됨
- **Quick Tunnel 재시작 시 URL 변경** → Pub/Sub 구독의 엔드포인트 URL을 그때마다 수동 갱신해야 함 (운영 단계에서는 Named Tunnel + 도메인으로 전환)
- **Pub/Sub 알림에는 메일 내용이 없음** — historyId만 오므로 반드시 별도 조회 단계 필요
- **[실제 사고 사례] Pub/Sub 구독이 죽은 URL을 가리켜도 아무 에러도 안 남**: n8n·터널·백엔드·IAM 권한이 전부 정상인데도 실시간 메일이 하나도 안 들어온 적이 있었음. 원인은 Pub/Sub 구독(`gmail-push-sub`)의 엔드포인트 URL이 예전에 잠깐 띄웠던 **Quick Tunnel(`*.trycloudflare.com`) 주소**로 그대로 남아있던 것 — 그 터널은 이미 죽어 있었지만 Pub/Sub도, n8n도, Google Cloud 콘솔도 어디에도 에러가 안 뜨고 그냥 조용히 실패함.
  - 진단 순서: ① 터널/도메인이 실제로 응답하는지 직접 POST 테스트 ② n8n Executions 탭에서 새 실행이 생기는지 확인 ③ 안 생기면 GCP 콘솔 → Pub/Sub → 구독 → **수정(Edit)** 화면에서 엔드포인트 URL을 직접 눈으로 확인 (목록/상세 화면엔 URL이 안 보이고 수정 화면에서만 보임)
  - Named Tunnel(고정 도메인)로 전환하면 이 문제 자체가 원천적으로 사라짐 — 위 4번 경고가 왜 있는지 이 사고로 실감함

---

## 13. 단계별 완료 체크리스트

- [ ] n8n 셀프호스팅 실행
- [ ] (실시간 동기화) 폴링 Gmail Push 로 전체 체인 구성
- [ ] Cloudflare Tunnel 공개 주소 확보 및 헬스체크
- [ ] n8n Webhook 노드 (`/webhook/gmail-push`) 생성
- [ ] Pub/Sub 토픽 생성 + Gmail Publisher 권한 부여
- [ ] Push 구독 생성 (엔드포인트 = 퀵 터널 URL)
- [ ] `users.watch()` 등록 (historyId/expiration 응답 확인)
- [ ] 메일 조회 → 백엔드 전송 노드 구성 및 실제 메일로 종단 테스트
- [ ] watch 갱신 Schedule Trigger 등록 및 활성화
- [ ] 백엔드 엔드포인트를 POST + 실제 필드 수신 구조로 전환
- [ ] 터널 지속성 방안 결정 (임시 유지 / launchd 자동실행 / 도메인 구매 후 Named Tunnel)