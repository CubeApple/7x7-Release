# 🎵 7x7 Rhythm Game

<img width="893" height="666" alt="image" src="https://github.com/user-attachments/assets/574e03b0-0d7c-43b8-8536-c6cf60dc607f" />
<img width="896" height="668" alt="image" src="https://github.com/user-attachments/assets/cf362101-bbce-4de2-b937-985a93820450" />



**음악의 흐름에 맞춰 7×7 보드 위에서 장애물을 피하고, 곡이 끝날 때까지 살아남는 리듬 액션 게임입니다.**

Pygame으로 제작한 싱글 플레이 게임입니다. 23개의 음악 스테이지를 선택해 플레이할 수 있으며, 음악 진행에 반응하는 비주얼라이저와 스테이지별 기록·클리어 통계를 제공합니다.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green?logo=python)
![Genre](https://img.shields.io/badge/Genre-Rhythm%20%7C%20Action-purple)

## ✨ 주요 기능

- **23개의 정규 음악 스테이지** — 일반 스테이지 19개와 보스 스테이지 4개
- **개별 보스 해금 조건** — 스테이지 7, 12, 22, 23은 각기 다른 진행률·클리어 조건을 만족해야 플레이 가능
- **음악 반응형 비주얼라이저** — 24개 주파수 대역의 스펙트럼과 음악 특징에 반응하는 화면 효과
- **회피 중심의 게임 플레이** — 방향키로 보드 위를 이동하며 다양한 장애물과 패턴을 피하기
- **플레이 기록 저장** — 최고 진행률, 클리어 횟수, 최고 클리어 등급을 로컬 JSON 파일에 보관
- **일시정지 및 게임 통계** — 플레이 중 기록과 스테이지 정보를 확인
- **데이터 버전 고정** — 게임 저장 데이터와 음악 분석 데이터의 버전은 별도 요청 전까지 1로 유지

## 🛠️ 기술 스택

| 구분 | 기술 |
|---|---|
| 언어 | Python 3 |
| 게임 라이브러리 | Pygame |
| 저장 데이터 | JSON |
| 음악 시각화 데이터 | `music/main_rhythm.json` |

## 📦 프로젝트 구성

```text
7x7/
├── 7x7.py
├── 7x7_data.json          # 플레이 기록 (없으면 실행 시 새로 생성)
├── font/
│   └── Jua-Regular.ttf
└── music/
    ├── main_rhythm.json
    ├── Sunburst_NCS.mp3
    ├── MintParfait.mp3
    ├── SmokedTurkeyRag.mp3
    ├── DaDiDuDonut.mp3
    ├── Butterfly.mp3
    ├── FizzyPixel.mp3
    ├── MyLittleHero.mp3
    ├── PixelPig.mp3
    ├── Chess.mp3
    ├── AmongUsTrapRemix.mp3
    ├── TheWorldRevolvong.mp3
    ├── Megalovania.mp3
    ├── Enemy.mp3
    ├── NyanCat.mp3
    ├── EEEAAAOOO.mp3
    ├── LemonOiia.mp3
    ├── Unity.mp3
    ├── Xenogenesis.mp3
    ├── PUNGYEON.mp3
    ├── Raya(Slowed).mp3
    ├── FirstSong.mp3
    ├── F1.mp3
    └── YourNewHome.mp3
```

> 음악 및 폰트 파일은 게임 실행에 필요합니다. 프로젝트 폴더 구조와 파일명을 유지해 주세요.

## 🚀 설치 및 실행

### 1. Python 설치

Python 3을 설치하고 터미널에서 버전을 확인합니다.

```bash
python --version
```

Windows에서 `python` 명령을 사용할 수 없다면 `py`를 사용하세요.

### 2. 프로젝트 폴더로 이동

```bash
cd 7x7
```

### 3. Pygame 설치

```bash
python -m pip install pygame
```

Windows에서 `python` 대신 `py`를 사용하는 경우:

```bash
py -m pip install pygame
```

### 4. 게임 실행

```bash
python 7x7.py
```

Windows에서는 다음 명령으로도 실행할 수 있습니다.

```bash
py 7x7.py
```

## 🎮 조작 방법

| 키 | 동작 |
|---|---|
| `↑` `↓` | 스테이지 선택 / 게임 중 이동 |
| `←` `→` | 게임 중 이동 |
| `Enter` 또는 `Space` | 선택한 스테이지 시작 |
| `Esc` 짧게 누르기 | 일시정지 중 게임 재개 |
| `Esc` 길게 누르기 | 일시정지 중 스테이지 선택 화면으로 돌아가기 |
| `R` 또는 `Space` 길게 누르기 | 게임 재시작 |
| `H` | 히트박스 표시 전환 |
| 홈 화면 `P` | 플레이어 커스터마이징 / 충돌 테스트 화면 |
| 커스터마이징 `↑` `↓` | 색상 또는 피격 효과 항목 선택 |
| 커스터마이징 `←` `→` | 선택한 색상 또는 피격 효과 변경 |
| 커스터마이징 `Esc` | 옵션 선택과 플레이어 이동 테스트 전환 |
| 커스터마이징 `P` | 맵 선택 화면으로 돌아가기 |

커스터마이징 화면에서는 장애물 대신 중앙을 도는 TBall 하나로 충돌을 시험할 수 있습니다. 색상과 피격 효과 설정은 플레이 기록 JSON 파일에 함께 저장됩니다.

## 🏁 플레이 방법

1. 홈 화면에서 방향키로 스테이지를 선택합니다.
2. `Enter` 또는 `Space`를 눌러 게임을 시작합니다.
3. 방향키로 7×7 보드 위를 이동하며 장애물을 피합니다.
4. 음악이 끝날 때까지 살아남으면 스테이지를 클리어합니다.
5. 클리어 기록과 등급은 자동으로 저장됩니다.

보스 해금 조건은 다음과 같습니다.

- **스테이지 7 My Little Hero** — 스테이지 1~6 모두 최고 진행률 30% 이상
- **스테이지 12 Megalovania** — 스테이지 10·11 모두 클리어
- **스테이지 22 F1** — 스테이지 17~21 모두 최고 진행률 30% 이상
- **스테이지 23 Your New Home** — 스테이지 1~22 모두 최고 진행률 20% 이상

잠긴 보스는 선택 화면에서 `[LOCKED]`로 표시되고 시작할 수 없습니다. 잠금 미리보기는 음악 및 실제 장애물 대신 기본 Ball 패턴을 보여줍니다. 플레이 기록은 프로젝트 폴더의 `7x7_data.json`에 저장되며, 예전 10곡 순서의 기록도 곡 파일명을 기준으로 새 스테이지 위치에 보존됩니다.

## 🎼 수록 스테이지

| 번호 | 곡 | 아티스트 | 구분 |
|---:|---|---|---|
| 1 | Sunburst | NCS | 일반 |
| 2 | Mint Parfait | a_hisa | 일반 |
| 3 | Smoked Turkey Rag | a_hisa | 일반 |
| 4 | Da Di Du Donut | a_hisa | 일반 |
| 5 | Butterfly | a_hisa | 일반 |
| 6 | Fizzy Pixel | 기타/기본 | 일반 |
| 7 | My Little Hero | a_hisa | 보스 |
| 8 | Pixel Pig | Di Young | 일반 |
| 9 | Chess | joyful | 일반 |
| 10 | Among Us Trap Theme | Leonz | 일반 |
| 11 | The World Revolving | Toby Fox | 일반 |
| 12 | Megalovania | Toby Fox | 보스 |
| 13 | Enemy (Epic ver) | Samuel Kim | 일반 |
| 14 | Nyan Cat | daniwell | 일반 |
| 15 | EEEAAAOOO | MyFuckinMess | 일반 |
| 16 | Lemon Oiia | OIIA Cat | 일반 |
| 17 | Unity | TheFatRat | 일반 |
| 18 | Xenogenesis | TheFatRat | 일반 |
| 19 | 풍년 | 국립국악원 | 일반 |
| 20 | Raya (Slowed) | Zericxxn | 일반 |
| 21 | First Song | Roga. | 일반 |
| 22 | F1 | Hans Zimmer | 보스 |
| 23 | Your New Home (Epic ver) | Carameii | 보스 |

모든 곡은 실제 오디오를 분석한 음높이·온셋·주파수 대역 데이터를 사용합니다. 특히 11·12번 곡은 스펙트럼 증폭을 높여 시각 효과가 보다 뚜렷하게 반응합니다.

## ⚠️ 장애물 안내

장애물은 보드 바깥에서 나타나거나 보드 위에서 움직이며, 플레이어와 충돌하면 HP를 잃습니다. 움직임과 경고 표시를 살펴 빈 칸으로 피하세요.

| 장애물 | 특징 | 대응 요령 |
|---|---|---|
| 기본 공 (Ball) | 흰색 공이 생성된 방향과 속도에 따라 직선으로 이동합니다. 기존 기본 속도보다 32% 빠르게 이동합니다. | 공의 진행 방향을 보고 옆 칸이나 빈 줄로 이동합니다. |
| 궤도 공 (TBall) | 파란 공이 원형 궤도를 따라 회전합니다. 생성 직전에는 `!` 경고가 표시됩니다. | 경고가 나타나면 궤도 주변을 피하고, 공의 회전 경로가 지나간 뒤 이동합니다. |
| 부메랑 공 (VBall) | 분홍색 공이 선택된 타일 중심까지 프레임별 가감속으로 이동한 뒤, 속도를 반전하며 되돌아옵니다. 화면 밖으로 벗어나면 제거됩니다. | 공의 목표 타일과 속도가 줄어드는 정점을 살피고, 왕복 경로를 피해 이동합니다. |
| 레이저 (Laser) | 방향 장치가 보드 가장자리로 다가온 뒤 경고·충전 단계를 거쳐 긴 빔을 발사합니다. 발사 후 빔을 거두고 퇴장합니다. | 장치가 향하는 방향의 빔 경로에서 벗어나고, 발사 전후의 단계 변화를 확인합니다. |
| 통나무 (Log) | 길이가 여러 칸인 통나무가 화면 가장자리에서 가로 또는 세로로 굴러와 보드를 가로지릅니다. | 통나무의 길이와 이동 방향을 보고 경로 전체를 피합니다. 짧은 공보다 넓은 공간을 확보하세요. |
| 폭탄 (Bomb) | 무작위 타일에 8각별 테두리로 나타나 내부가 차오른 뒤 폭발합니다. `I`~`IV`는 폭발 중심에서 연쇄되는 칸의 거리이며, 직각형은 대각선, 45도형은 상하좌우로 퍼집니다. | 충전 중인 폭탄과 로마 숫자로 범위를 살피고, 폭발이 시작되기 전에 해당 칸과 연쇄 경로에서 벗어납니다. |

메인 폭탄(`Bomb`)이 자신의 연쇄 서브 폭탄(`SubBomb`) 생성, 순서·위치 예약, 갱신과 정리까지 소유하며, 서브 폭탄은 다시 연쇄를 만들지 않아 계획된 경로만 한 번 실행합니다. `I`는 메인 폭발만, `II`~`IV`는 선택한 십자 방향의 1~3칸 거리까지 연쇄합니다. 같은 거리의 칸은 함께 폭발하고, 이후 거리의 웨이브는 `BOMB_CHAIN_DELAY_SECONDS` 간격으로 이어집니다. 첫 연쇄 웨이브는 메인 폭탄의 폭발 애니메이션·피격 시간이 끝난 뒤 시작합니다. 메인·서브 폭탄은 각각 폭발 뒤 `BOMB_DAMAGE_WINDOW_SECONDS` 동안 회전하며 크게 부풀었다가 줄어들고, 해당 타일에 피해를 줍니다. 회전 속도는 `BOMB_EXPLOSION_ROTATION_DEGREES` 값으로 조절합니다.

`Ball`, `TBall`, `VBall`과 플레이어는 원형 히트박스끼리의 거리로 충돌을 판정합니다. `Laser`와 `Log`는 직사각형 장애물 영역을 유지하되, 플레이어 원과의 교차로 피격을 판정합니다. 플레이어는 흰색 원과 연두색 후광으로 표시됩니다.

레이저의 발사 유지 시간은 `LASER_BEAM_DURATION_SECONDS`, 퇴장 속도는 `LASER_RETRACT_SPEED`에서 조정합니다. `BombManager`는 메인 폭탄 생성과 업데이트를 담당합니다.

레벨별 스폰 패턴은 [7x7.py](./7x7.py)의 `spawn_level_1`부터 `spawn_level_23`까지 각 함수에서 직접 수정합니다. 각 장애물은 `state.ball_delay -= dt`와 `if state.ball_delay <= 0:` 형태로 타이머를 관리하며, `random.randint`로 다음 대기 시간과 생성 개수를 정하고 `random.random()`으로 출현 확률을 조절합니다. `lane_pool`과 `direction_pool`에 중복 항목을 넣으면 해당 레인이나 방향이 더 자주 선택됩니다. 예를 들어 `lane_pool = [1, 1, 2, 3, 4, 5, 6, 7, 7]`은 가장자리 레인을 더 자주 선택합니다. `get_spawn_coordinates(direction, lane)`은 1~7번 레인을 시계 방향의 `(행, 열)`로 변환하고, 스폰 함수에 위치와 방향을 전달합니다. `dt`는 기존 타이머 단위를 유지하기 위해 메인 루프에서 `100 / tps`로 전달됩니다. 각 레벨의 기본 스폰 패턴도 개별 함수에 직접 적혀 있어, 다른 레벨에 영향을 주지 않고 조절할 수 있습니다.

플레이어 렌더링의 보간 속도는 `PLAYER_RENDER_SMOOTHING_SPEED`에서 조정할 수 있습니다. VBall은 원래의 프레임 기반 가감속으로 선택된 타일 중심에서 방향을 바꿉니다.

## 📝 참고

- 게임 실행 시 `font/` 및 `music/` 폴더가 `7x7.py`와 같은 프로젝트 루트 아래에 있어야 합니다.
- 음악 파일과 폰트의 저작권 및 사용 조건은 각 원작자와 배포처의 안내를 확인해 주세요.
