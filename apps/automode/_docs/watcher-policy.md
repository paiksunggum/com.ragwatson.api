# [Specification] Watcher/Judge 멀티 에이전트 라우팅 테스트 하네스

> 강사님 원본 스펙(허브-스포크 멀티 에이전트 테스트 하네스)을 이 프로젝트의 실제 스타 토폴로지 구조에 맞게 재해석한 문서.

---

## 0. 원본 스펙 ↔ 실제 프로젝트 매핑

| 스펙 원문 (가상 경로) | 실제 프로젝트 매핑 | 상태 |
|---|---|---|
| `core/lol/t1_mid_faker_orchestrator.py` (Faker/EXAONE) | `apps/automode/adapter/outbound/clients/exaone_slm_client.py` (`ExaoneSLMClient` → `SLMPort`) | 기존 존재 |
| `star_craft/` (온톨로지 허브) | `apps/star_craft/` | 기존 존재 (CLAUDE.md 상 진짜 Hub) |
| `sherlock_homes/` (커뮤니케이션 스포크) | `apps/automode/` | 기존 존재 (email/discord/telegram 담당 스포크) |
| `titanic/`, `silicon_valley/` (기타 스포크) | `apps/titanic/`, `apps/silicon_valley/` | 기존 존재 |
| `detective_watson_watcher_hub.py` | `apps/automode/adapter/inbound/api/v1/watcher_router.py` | 기본 뼈대 구현됨 |
| `police_lestrade_telegram_router` | `apps/automode/adapter/inbound/api/v1/telegram_router.py` | 기존 존재 |
| `police_anderson_discord_router` | `apps/automode/adapter/inbound/api/v1/discord_router.py` | 기존 존재 |
| 홈즈 에이전트 (`sherlock_homes/app/use_cases/`) | `apps/automode/app/use_cases/` (신규 use case 추가 예정) | 미구현 |
| (원본 스펙에 없음) 욕설/비상식 한국어 필터 | `apps/automode/adapter/inbound/api/v1/judge_router.py` + `kor_unsmile` 파인튜닝 모델 | 기본 뼈대 구현됨, 모델 연동 전 |

---

## 1. System Overview & Architecture Context

본 시스템은 허브 앤 스포크(Hub-and-Spoke) + 온톨로지 기반의 멀티 에이전트 아키텍처를 따른다. (CLAUDE.md 10번 "스타 토폴로지 + 온톨로지 아키텍처" 참고)

- **최고 사령탑 (Hub / Brain)**: `apps/automode/adapter/outbound/clients/exaone_slm_client.py`
  Ollama로 서빙되는 EXAONE(`exaone3.5`)이 상주하는 오케스트레이터 클라이언트. (`SLMPort`를 통해 추상화됨)
- **온톨로지 버스 (Ontology Hub)**: `apps/star_craft/`
  전사 데이터 흐름·엔티티 관계(Ontology)·전사 컨텍스트를 총괄하는 허브. 스포크는 반드시 이 허브를 경유해야 서로 통신 가능 (스포크→스포크 직접 참조 금지, `scripts/validate_topology.py`로 강제).
- **커뮤니케이션 스포크 (Communication Spoke)**: `apps/automode/`
  외부 채널(Email, Telegram, Discord 등)과의 소통 및 인바운드 이벤트를 전담.
- **기타 스포크 (Spokes)**: `apps/titanic/`, `apps/silicon_valley/` 등 (ERP의 개별 도메인 파트)

---

## 2. Agent Core Logic & Routing Criteria

외부 커뮤니케이션 채널을 통해 인입되는 이벤트는 다음 기준으로 라우팅된다.

- **Case 0 (필터링)**: 욕설·비상식적 한국어가 감지된 경우
  ➔ `judge_router.py`(Judge)가 `kor_unsmile` 기반 파인튜닝 모델로 1차 차단. Case A/B 라우팅으로 넘어가지 않고 종결.
- **Case A (일반 업무)**: 중요 거래처가 아니거나 단순 문의인 경우
  ➔ `apps/automode/app/use_cases/` 내의 홈즈(Holmes) 역할 유스케이스가 자체적으로 컨텍스트를 소화하여 처리 및 종결.
- **Case B (중요/에스컬레이션 업무)**: 중요 거래처이거나 자동 보고서 생성을 요청하는 경우
  ➔ `apps/star_craft/`를 경유하여 최고 에이전트(EXAONE, `ExaoneSLMClient`)에게 격상(Escalation). 전사 데이터를 취합해 최종 보고서를 생성하고 하향 전달.

---

## 3. Watcher (`watcher_router.py`) 역할 정의

`apps/automode/adapter/inbound/api/v1/watcher_router.py`에 위치한 **왓처(Watcher)**는 본 테스트 하네스의 핵심 검증 대상이자 인바운드 게이트웨이다. 단순한 라우터가 아닌 **'Triage Nurse(초진 및 분류 관문)'** 역할을 수행한다.

### 왓처의 핵심 메커니즘

1. **감시 및 후킹 (Watch & Hook)**: `receiver_router.py`(Gmail, 실제로 작동 중인 유일한 인바운드 채널), `telegram_router.py`, `discord_router.py` 등 기존 인바운드 라우터로부터 유저 메시지/이벤트를 낚아챔.
2. **0차 필터링 (Judge 경유)**: `judge_router.py`를 통해 욕설·비상식적 한국어인지 먼저 확인.
3. **1차 분류 및 조율 (Validation & Triage)**: 발신자(중요 거래처 여부)와 본문(보고서 요청 등의 의도)을 가볍고 빠르게 분석.
4. **컨텍스트 스위칭 및 라우팅 (Routing Decision)**:
   - 일반 메시지 ➔ `apps/automode/app/use_cases/` (홈즈 역할) 호출.
   - 중요/보고서 메시지 ➔ `apps/star_craft/` 온톨로지 버스로 이벤트 발행(Publish).

**현재 구현 상태**:
- `GET /api/automode/watcher/myself` 자기소개 엔드포인트
- `POST /api/automode/watcher/receive` — Judge 판정 후 정상 메일만 기존 `receiver` 파이프라인(pgvector 저장)으로 전달 (구현 완료, `watcher_interactor.filter_stop_word`)
- Case A(홈즈 처리)/Case B(star_craft 경유 페이커 에스컬레이션) 라우팅 로직은 아직 미구현

> **n8n 실제 연결 상태**: `Webhook`(paik-orchestrator) 노드 바로 뒤에 **Judge 필터 → IF(욕설 아님 확인)** 노드를 삽입해서, 욕설/비상식으로 판정되면 `스팸 분류`(→텔레그램)와 `pgvector 저장` 두 branch 모두 차단되도록 실제로 연결 완료. `receiver_router.py`의 pgvector 저장 로직 자체는 그대로 유지하고, 그 앞단에서 Judge가 게이트 역할을 함.

---

## 4. Judge (`judge_router.py`) 역할 정의

`apps/automode/adapter/inbound/api/v1/judge_router.py`에 위치한 **저지(Judge)**는 왓처의 0차 필터링을 담당하는 정책 기반 검증관이다.

- **모델**: `beomi/KcELECTRA-base`를 Korean Unsmile Dataset(`smilegate-ai/kor_unsmile`, 15,005건)으로 자체 파인튜닝. (`scripts/train_kcelectra_judge.py`, 로컬 맥 MPS로 학습, eval_accuracy=0.875, f1=0.918)
- **저장 위치**: `paik/models/kcelectra-judge/` (git 미포함, `.gitignore` 처리)
- **역할**: 인입된 메시지가 욕설/비상식적 한국어를 포함하는지 판정 → `true`면 Watcher의 Case A/B 라우팅으로 넘기지 않고 즉시 차단 및 로그.
- **현재 구현 상태**:
  - `GET /api/automode/judge/myself` 자기소개 엔드포인트
  - `POST /api/automode/judge/check` — 저장 없이 순수 판정만 반환 (`{is_abusive: bool}`), n8n 게이트로 실사용 중
  - `JudgeFilterPort` / `KcElectraJudgeClient`로 SOLID(DIP) 패턴 적용 — `judge_provider.py`에서 싱글톤으로 모델을 한 번만 로드해 `judge`/`watcher` 양쪽에서 공유

---

## 5. Test Harness Implementation Instructions

### [지시사항 1] 가상 이벤트 생성기 (Mock Event Generator)

- `telegram_router.py`, `discord_router.py` 등 기존 인바운드 라우터가 외부에서 메일/메시지를 수신하는 상황을 모사하는 Mock 데이터 생성기 작성.
- 최소 시나리오:
  - **Scenario 1**: 일반 거래처의 단순 인사/문의 메시지.
  - **Scenario 2**: VIP 거래처(`important_client: true`)의 "분기 실적 자동 보고서 발행 요망" 메시지.
  - **Scenario 3**: 욕설/비상식적 한국어 메시지 (Judge가 걸러야 하는 케이스).

### [지시사항 2] Watcher 라우팅 인터셉터 구현

- Mock 이벤트 생성기의 raw 데이터를 `watcher_router.py`(Watcher)가 가로채어 검증하는 라우팅 로직 구현.
- **Judge 필터 트리거**: 모든 이벤트는 먼저 `judge_router.py`를 거쳐 욕설/비상식 여부 판정.
- **홈즈 호출 트리거**: Scenario 1 감지 시, `apps/automode/app/use_cases/` 내 홈즈 역할 유스케이스 호출 및 로그.
- **페이커 에스컬레이션 트리거**: Scenario 2 감지 시, `apps/star_craft/`를 거쳐 `ExaoneSLMClient`가 최종 활성화되는 이벤트 파이프라인 구현.

### [지시사항 3] 하네스 대시보드 및 검증 로그 출력

- 이벤트 인입부터 최종 처리 완료(Watcher ➔ Judge ➔ Holmes 또는 Watcher ➔ Judge ➔ StarCraft ➔ Faker)까지 전체 저니(Journey)를 콘솔에 추적 서사 로그(Narrative Log) 형태로 출력하는 모니터링 기능 포함.
