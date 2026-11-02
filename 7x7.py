import pygame
from pygame.surface import Surface
from pygame.color import Color
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union, Sequence
import atexit
import random
import math
import base64
import json
import os
import hashlib
import uuid
from functools import lru_cache


pygame.init()

# ============================================================================
# 기본 화면·보드 설정: 보드 크기나 이동 속도를 조정할 때 이 구역을 확인하세요.
# ============================================================================
# 보드 칸 수를 바꾸면 스폰 위치·충돌 범위 계산에도 영향을 줍니다.
GRID_SIZE = 7
ELEMENT_SCALE = 0.88
CELL_SIZE = round(100 * ELEMENT_SCALE)
BOARD_HALF_SIZE = GRID_SIZE * CELL_SIZE // 2
GRID_EDGE_OFFSET = (GRID_SIZE - 1) * CELL_SIZE // 2
# 이동 시간은 프레임 수, 이동 속도는 칸 간격을 이 시간에 나눈 값입니다.
# 마지막 프레임 속도 반전 때문에 실제 이동량 계산에서 2프레임을 제외합니다.
MOVE_DURATION = 12
NORMAL_MOVE_SPEED = CELL_SIZE / (MOVE_DURATION - 2)
WRAP_MOVE_SPEED = CELL_SIZE * (GRID_SIZE - 1) / (MOVE_DURATION - 2)
# 장애물 속도와 렌더링 보간을 조절하는 설정입니다.
BALL_SPEED_SCALE = 1.32
PLAYER_RENDER_SMOOTHING_SPEED = 36.0
display_size = [1200, 900]
FONT_PATH = "font/Jua-Regular.ttf"
SAVE_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "7x7_data.json")
MAIN_RHYTHM_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "music",
    "main_rhythm.json"
)
# 레이저 본체와 빔을 따로 그리므로 본체 위치를 유지한 채 화면 너머까지 빔을 늘립니다.
LASER_LENGTH = max(display_size) + CELL_SIZE * 2
LASER_BEAM_DURATION_SECONDS = 0.4
LASER_RETRACT_SPEED = 7.5 * ELEMENT_SCALE
dis = pygame.display.set_mode(display_size, pygame.SRCALPHA)
pygame.display.set_caption("7x7")
pygame.mixer.music.load("music/Sunburst_NCS.mp3")
pygame.mixer.music.set_volume(1)


MUSIC_1 = "music/Sunburst_NCS.mp3"
MUSIC_2 = "music/MintParfait.mp3"
MUSIC_3 = "music/SmokedTurkeyRag.mp3"
MUSIC_4 = "music/DaDiDuDonut.mp3"
MUSIC_5 = "music/Butterfly.mp3"
MUSIC_6 = "music/FizzyPixel.mp3"
MUSIC_7 = "music/MyLittleHero.mp3"
MUSIC_8 = "music/PixelPig.mp3"
MUSIC_9 = "music/Chess.mp3"
MUSIC_10 = "music/AmongUsTrapRemix.mp3"
MUSIC_11 = "music/TheWorldRevolvong.mp3"
MUSIC_12 = "music/Megalovania.mp3"
MUSIC_13 = "music/Enemy.mp3"
MUSIC_14 = "music/NyanCat.mp3"
MUSIC_15 = "music/EEEAAAOOO.mp3"
MUSIC_16 = "music/LemonOiia.mp3"
MUSIC_17 = "music/Unity.mp3"
MUSIC_18 = "music/Xenogenesis.mp3"
MUSIC_19 = "music/PUNGYEON.mp3"
MUSIC_20 = "music/Raya(Slowed).mp3"
MUSIC_21 = "music/FirstSong.mp3"
MUSIC_22 = "music/F1.mp3"
MUSIC_23 = "music/YourNewHome.mp3"
MAX_LEVEL = 23
GAME_DATA_VERSION = 1
MAIN_RHYTHM_DATA_VERSION = 1
# 보스 목록·조건 딕셔너리의 키는 0부터, 조건 안의 선행 스테이지 번호는 1부터 셉니다.
MUSIC_TRACKS = (
    MUSIC_1, MUSIC_2, MUSIC_3, MUSIC_4, MUSIC_5, MUSIC_6,
    MUSIC_7, MUSIC_8, MUSIC_9, MUSIC_10, MUSIC_11, MUSIC_12,
    MUSIC_13, MUSIC_14, MUSIC_15, MUSIC_16, MUSIC_17, MUSIC_18,
    MUSIC_19, MUSIC_20, MUSIC_21, MUSIC_22, MUSIC_23
)
TRACK_IDS = tuple(os.path.basename(track) for track in MUSIC_TRACKS)
# 구버전 저장 파일에는 10곡의 이전 순서로 기록되어 있으므로 곡 ID로 새 위치에 옮깁니다.
LEGACY_TRACK_IDS = (
    "Sunburst_NCS.mp3",
    "MintParfait.mp3",
    "SmokedTurkeyRag.mp3",
    "DaDiDuDonut.mp3",
    "Butterfly.mp3",
    "MyLittleHero.mp3",
    "PixelPig.mp3",
    "NyanCat.mp3",
    "TheWorldRevolvong.mp3",
    "Megalovania.mp3"
)
BOSS_LEVEL_INDICES = (6, 11, 21, 22)
# 요구하는 진행률은 해당 보스를 제외한 스테이지의 최고 진행률 기준입니다.
BOSS_PROGRESS_REQUIREMENTS = {
    6: (tuple(range(1, 7)), 30.0),
    21: (tuple(range(17, 22)), 30.0),
    22: (tuple(range(1, 23)), 20.0)
}
# 12번 보스는 10·11번 스테이지를 각각 완주해야 해금됩니다.
BOSS_CLEAR_REQUIREMENTS = {
    11: (10, 11)
}
LEVEL_NAMES = (
    "Sunburst",
    "Mint Parfait",
    "Smoked Turkey Rag",
    "Da-Di-Du Donut",
    "Butterfly",
    "Fizzy Pixel",
    "My Little Hero",
    "Pixel Pig",
    "Chess",
    "Among Us Trap Theme",
    "The World Revolving",
    "Megalovania",
    "Enemy (Epic ver)",
    "Nyan Cat",
    "EEEAAAOOO",
    "Lemon Oiia",
    "Unity",
    "Xenogenesis",
    "풍년",
    "Raya (Slowed)",
    "First Song",
    "F1",
    "Your New Home (Epic ver)"
)
LEVEL_CREATORS = (
    "NCS",
    "a_hisa",
    "a_hisa",
    "a_hisa",
    "a_hisa",
    "a_hisa",
    "a_hisa",
    "Di Young",
    "joyful",
    "Leonz",
    "Toby Fox",
    "Toby Fox",
    "Samuel Kim",
    "daniwell",
    "MyFuckinMess",
    "OIIA Cat",
    "TheFatRat",
    "TheFatRat",
    "국립국악원",
    "Zericxxn",
    "Roga.",
    "Hans Zimmer",
    "Carameii"
)
# 게임 화면 상태: 홈/플레이/일시정지는 이벤트 처리와 업데이트 흐름을 구분합니다.
STATE_HOME = "home"
STATE_PLAY = "play"
STATE_PAUSE = "pause"
debug_boss_unlock_overrides = {}
game_sound = pygame.mixer.Sound(MUSIC_1)
TRACK_DURATION_SECONDS = {0: game_sound.get_length()}

# ----------------------------------------------------------------------------
# 음악 길이·분석 데이터: 시각 효과가 음악 재생 위치에 맞춰 움직이게 합니다.
# ----------------------------------------------------------------------------
def get_track_duration_seconds(level_index: int) -> float:
    """맵별 음악 길이를 한 번 읽어 캐시합니다."""
    if level_index not in TRACK_DURATION_SECONDS:
        duration_sound = pygame.mixer.Sound(MUSIC_TRACKS[level_index])
        TRACK_DURATION_SECONDS[level_index] = duration_sound.get_length()
        del duration_sound
    return TRACK_DURATION_SECONDS[level_index]


def format_track_time(seconds: float) -> str:
    """초 단위 길이를 분:초 형식으로 표시합니다."""
    total_seconds = max(0, int(seconds))
    minutes, remaining_seconds = divmod(total_seconds, 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"

with open(MAIN_RHYTHM_DATA_PATH, "r", encoding="utf-8") as rhythm_file:
    main_rhythm_data = json.load(rhythm_file)
MAIN_RHYTHM_SAMPLE_INTERVAL = main_rhythm_data["sample_interval"]
MAIN_RHYTHM_TRACKS = tuple(
    base64.b64decode(track, validate=True)
    for track in main_rhythm_data["features_base64"]
)
MAIN_RHYTHM_FRAME_COUNTS = main_rhythm_data["frame_counts"]
MAIN_RHYTHM_ONSETS = main_rhythm_data["onsets"]
SPECTRUM_BAND_COUNT = main_rhythm_data["frequency_bands"]
FEATURE_STRIDE = SPECTRUM_BAND_COUNT + 2
MAIN_RHYTHM_TRACK_COUNT = len(MAIN_RHYTHM_TRACKS)
# 한 프레임의 데이터는 [음높이, 온셋 강도, 주파수 대역...] 순서로 저장됩니다.
# 아래 검사는 음악 데이터와 코드의 필드 수·곡 순서가 맞는지 시작 시 확인합니다.
if (
    main_rhythm_data.get("version") != MAIN_RHYTHM_DATA_VERSION
    or not isinstance(MAIN_RHYTHM_SAMPLE_INTERVAL, (int, float))
    or not math.isfinite(MAIN_RHYTHM_SAMPLE_INTERVAL)
    or MAIN_RHYTHM_SAMPLE_INTERVAL <= 0
    or SPECTRUM_BAND_COUNT != 24
    or main_rhythm_data.get("feature_stride") != FEATURE_STRIDE
    or MAIN_RHYTHM_TRACK_COUNT != MAX_LEVEL
    or len(MAIN_RHYTHM_FRAME_COUNTS) != MAIN_RHYTHM_TRACK_COUNT
    or len(MAIN_RHYTHM_ONSETS) != MAIN_RHYTHM_TRACK_COUNT
    or main_rhythm_data["songs"] != [
        os.path.basename(track)
        for track in MUSIC_TRACKS[:MAIN_RHYTHM_TRACK_COUNT]
    ]
    or any(
        not isinstance(frame_count, int)
        or frame_count <= 0
        or len(track) != frame_count * FEATURE_STRIDE
        or any(
            not 48 <= track[index] <= 90
            for index in range(0, len(track), FEATURE_STRIDE)
        )
        for track, frame_count in zip(MAIN_RHYTHM_TRACKS, MAIN_RHYTHM_FRAME_COUNTS)
    )
    or any(
        any(
            len(event) != 2
            or not isinstance(event[0], int)
            or not isinstance(event[1], int)
            or not 0 <= event[1] <= 255
            for event in events
        )
        or any(events[index][0] > events[index + 1][0] for index in range(len(events) - 1))
        for events in MAIN_RHYTHM_ONSETS
    )
):
    raise ValueError("음악 시각화 데이터의 형식이 올바르지 않습니다.")

# ============================================================================
# 화면 연출·조작·장애물 타이밍 설정: 플레이 감각 조정은 이 상수부터 확인하세요.
# ============================================================================
SPECTRUM_BAR_MAX_LENGTH = 104
SPECTRUM_BAR_HEIGHT = 7
SPECTRUM_BAR_TOP = 148
SPECTRUM_BAR_SPACING = 25
SPECTRUM_ATTACK_SPEED = 28.0
SPECTRUM_RELEASE_SPEED = 9.0
SPECTRUM_AGC_ATTACK_SPEED = 12.0
SPECTRUM_AGC_RELEASE_SPEED = 1.1
SPECTRUM_AGC_INITIAL_PEAK = 160.0
SPECTRUM_AGC_PEAK_FLOOR = 80.0
SPECTRUM_AGC_TARGET_LEVEL = 205.0
SPECTRUM_AGC_MAX_LEVEL = 220.0
SPECTRUM_BAR_COLORS = (
    (255, 255, 255),
    (210, 210, 210),
    (140, 140, 140)
)
SPECTRUM_BAR_PATTERN = (0, 1, 2, 1, 0, 1, 2, 1)
ESC_HOME_HOLD_SECONDS = 1.0
RESTART_HOLD_SECONDS = ESC_HOME_HOLD_SECONDS
ESC_PAUSE_TAP_SECONDS = 0.2
HOLD_GAUGE_SIZE = (190, 9)
RECORD_FLASH_DURATION = 1.0
BOMB_CHARGE_SECONDS = 1.8
# 같은 거리의 연쇄 칸은 동시에 터지고, 다음 거리 웨이브까지 기다리는 시간입니다.
BOMB_CHAIN_DELAY_SECONDS = 0.15
# 메인·서브 폭탄 각각의 폭발 애니메이션 및 해당 칸 피격 판정 지속 시간입니다.
BOMB_DAMAGE_WINDOW_SECONDS = 0.35
# 폭발 시간 전체에 걸쳐 회전할 각도입니다. 음수는 시계 방향이며, 값을 낮추면 더 천천히 돕니다.
BOMB_EXPLOSION_ROTATION_DEGREES = 45.0
# 프레임 차이에 따른 타이밍 오차를 줄이는 폭탄 전용 고정 업데이트 간격입니다.
BOMB_SIMULATION_STEP = 1.0 / 120.0
BOMB_SHAPE_SIZE = round(CELL_SIZE * 0.72)
ENEMY_HITBOX_SIZE = round(40 * ELEMENT_SCALE)
LOG_END_INSET = round(16 * ELEMENT_SCALE)
CROWN_IMAGE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "image",
    "crown.png"
)

ball_dis = pygame.Surface((100, 100), pygame.SRCALPHA)
pause_dis = pygame.Surface(display_size, pygame.SRCALPHA)
home_fade_surface = pygame.Surface(display_size, pygame.SRCALPHA)
visual_effect_layer = pygame.Surface(display_size, pygame.SRCALPHA)
customization_ui_layer = pygame.Surface(display_size, pygame.SRCALPHA)
customization_idle_layer = pygame.Surface(display_size, pygame.SRCALPHA)
customization_mode_indicator = pygame.Surface((500, 42), pygame.SRCALPHA)
home_menu_gradient = pygame.Surface((320, display_size[1]), pygame.SRCALPHA)
for gradient_x in range(home_menu_gradient.get_width()):
    gradient_alpha = round(
        88 * gradient_x / (home_menu_gradient.get_width() - 1)
    )
    pygame.draw.line(
        home_menu_gradient,
        (12, 15, 22, gradient_alpha),
        (gradient_x, 0),
        (gradient_x, home_menu_gradient.get_height() - 1)
    )
home_highlight_glow = pygame.Surface((18, 58), pygame.SRCALPHA)
for glow_x in range(home_highlight_glow.get_width()):
    glow_alpha = round(36 * (1.0 - glow_x / home_highlight_glow.get_width()))
    pygame.draw.line(
        home_highlight_glow,
        (218, 230, 255, glow_alpha),
        (glow_x, 4),
        (glow_x, home_highlight_glow.get_height() - 5)
    )
_font_cache = {}
_text_cache = {}
_ball_sprite_cache = {}
_tball_ring_cache = {}
_log_sprite_cache = {}
_laser_device_cache = {}
CROWN_IMAGE = pygame.transform.smoothscale(
    pygame.image.load(CROWN_IMAGE_PATH).convert_alpha(),
    (24, 24)
)


# ----------------------------------------------------------------------------
# 음악 반응 효과: 재생 위치에서 음높이·온셋·주파수 대역을 계산합니다.
# ----------------------------------------------------------------------------
def get_music_visual_features(playback_ms: int, level: int) -> Tuple[float, float, Tuple[float, ...]]:
    """현재 음악 시점의 음높이, 온셋, 주파수 대역을 부드럽게 보간합니다."""
    if not 1 <= level <= MAIN_RHYTHM_TRACK_COUNT:
        # 분석 데이터가 등록되지 않은 곡은 절차적 리듬으로 시각 효과를 유지합니다.
        seconds = max(0, playback_ms) / 1000.0
        beat_phase = math.tau * seconds * (1.7 + level * 0.035)
        onset = 255.0 if math.sin(beat_phase) > 0.94 else 0.0
        pitch = 60.0 + 8.0 * math.sin(beat_phase * 0.5)
        bands = tuple(
            max(
                0.0,
                44.0
                + 35.0 * math.sin(beat_phase * (0.2 + band * 0.027) + band)
                + (75.0 if onset else 0.0) * math.sin(band * 0.31) ** 2
            )
            for band in range(SPECTRUM_BAND_COUNT)
        )
        return pitch, onset, bands

    frames = MAIN_RHYTHM_TRACKS[level - 1]
    frame_count = MAIN_RHYTHM_FRAME_COUNTS[level - 1]
    sample_position = max(0, playback_ms) / (1000.0 * MAIN_RHYTHM_SAMPLE_INTERVAL)
    first_index = min(int(sample_position), frame_count - 1)
    first_offset = first_index * FEATURE_STRIDE
    if first_index == frame_count - 1:
        return (
            float(frames[first_offset]),
            min(255.0, float(frames[first_offset + 1]) * 1.15),
            tuple(
                float(value)
                for value in frames[first_offset + 2:first_offset + FEATURE_STRIDE]
            )
        )

    fraction = sample_position - first_index
    next_offset = first_offset + FEATURE_STRIDE
    return (
        frames[first_offset] + (frames[next_offset] - frames[first_offset]) * fraction,
        min(
            255.0,
            (
                frames[first_offset + 1]
                + (frames[next_offset + 1] - frames[first_offset + 1]) * fraction
            ) * 1.15
        ),
        tuple(
            frames[first_offset + index]
            + (frames[next_offset + index] - frames[first_offset + index]) * fraction
            for index in range(2, FEATURE_STRIDE)
        )
    )


def draw_main_rhythm_polygon(
    pitch: float,
    onset_strength: float,
    playback_ms: int,
    record_flash: float = 0.0
) -> None:
    """그리드가 비치는 채움과 푸른 기가 도는 선명한 윤곽의 정십이각형을 그립니다."""
    visual_effect_layer.fill((0, 0, 0, 0))
    pitch_amount = max(0.0, min(1.0, (pitch - 60.0) / 24.0))
    radius = (315.0 + pitch_amount * 58.0 + onset_strength / 255.0 * 28.0)
    rotation = playback_ms * 0.00004 + (pitch - 69.0) * 0.002
    center = (display_size[0] // 2, display_size[1] // 2)
    points = [
        (
            round(center[0] + math.cos(math.tau * index / 12 + rotation) * radius),
            round(center[1] + math.sin(math.tau * index / 12 + rotation) * radius)
        )
        for index in range(12)
    ]
    alpha = round(82 + onset_strength / 255.0 * 38)
    flash = max(0.0, min(1.0, record_flash))
    fill_color = (
        round(151 + (255 - 151) * flash),
        round(164 + (210 - 164) * flash),
        round(185 + (70 - 185) * flash),
        32
    )
    outline_color = (
        round(190 + (255 - 190) * flash),
        round(203 + (221 - 203) * flash),
        round(226 + (110 - 226) * flash),
        alpha
    )
    pygame.draw.polygon(visual_effect_layer, fill_color, points)
    pygame.draw.polygon(
        visual_effect_layer,
        outline_color,
        points,
        2
    )


def draw_spectrum_bars(levels: Sequence[float], record_flash: float = 0.0) -> None:
    """양옆에 색상이 순환하는 실버 막대를 밑줄 없이 그립니다."""
    flash = max(0.0, min(1.0, record_flash))
    for band, level in enumerate(levels):
        if level < 8:
            continue
        bar_length = max(2, round(level / 255.0 * SPECTRUM_BAR_MAX_LENGTH))
        y = SPECTRUM_BAR_TOP + band * SPECTRUM_BAR_SPACING
        energy = min(1.0, level / 255.0)
        color_index = SPECTRUM_BAR_PATTERN[band % len(SPECTRUM_BAR_PATTERN)]
        base_color = SPECTRUM_BAR_COLORS[color_index]
        color = (
            round(base_color[0] + (255 - base_color[0]) * flash),
            round(base_color[1] + (255 - base_color[1]) * flash),
            round(base_color[2] + (255 - base_color[2]) * flash),
            round(230 + energy * 25)
        )
        glow_color = (255, 255, 255, 52)
        pygame.draw.rect(
            visual_effect_layer,
            glow_color,
            (10, y - 1, bar_length + 4, SPECTRUM_BAR_HEIGHT + 2),
            border_radius=4
        )
        pygame.draw.rect(
            visual_effect_layer,
            color,
            (12, y, bar_length, SPECTRUM_BAR_HEIGHT),
            border_radius=3
        )
        pygame.draw.rect(
            visual_effect_layer,
            glow_color,
            (
                display_size[0] - 14 - bar_length,
                y - 1,
                bar_length + 4,
                SPECTRUM_BAR_HEIGHT + 2
            ),
            border_radius=4
        )
        pygame.draw.rect(
            visual_effect_layer,
            color,
            (display_size[0] - 12 - bar_length, y, bar_length, SPECTRUM_BAR_HEIGHT),
            border_radius=3
        )
    dis.blit(visual_effect_layer, (0, 0))


def update_spectrum_levels(
    targets: Sequence[float],
    levels: List[float],
    peak_levels: List[float],
    delta_time: float
) -> None:
    """대역별 피크를 천천히 추적해 자동 이득을 맞추고 표시값을 부드럽게 보간합니다."""
    for band, target in enumerate(targets):
        peak = peak_levels[band]
        peak_speed = (
            SPECTRUM_AGC_ATTACK_SPEED
            if target > peak
            else SPECTRUM_AGC_RELEASE_SPEED
        )
        peak_blend = 1.0 - math.exp(-peak_speed * delta_time)
        peak += (target - peak) * peak_blend
        peak_levels[band] = peak

        # 피크를 기준으로 크기를 보정하되, 조용한 대역의 과도한 증폭은 바닥값으로 제한합니다.
        normalized_target = min(
            SPECTRUM_AGC_MAX_LEVEL,
            target * SPECTRUM_AGC_TARGET_LEVEL
            / max(SPECTRUM_AGC_PEAK_FLOOR, peak)
        )
        level_speed = (
            SPECTRUM_ATTACK_SPEED
            if normalized_target > levels[band]
            else SPECTRUM_RELEASE_SPEED
        )
        level_blend = 1.0 - math.exp(-level_speed * delta_time)
        levels[band] += (normalized_target - levels[band]) * level_blend


# ----------------------------------------------------------------------------
# 레벨 진행·기록: 진행률, 보스 해금, 홈 화면 정보를 계산합니다.
# ----------------------------------------------------------------------------
def update_level_records(level_index: int, progress: float, current_score: int) -> bool:
    """현재 기록을 통산 최고 진행률/점수에 반영하고 진행률 신기록 여부를 반환합니다."""
    global save_dirty
    progress = max(0.0, min(100.0, progress))
    stats = level_stats[level_index]
    previous_progress = max(score_record[level_index], stats["best_progress"])
    new_progress_record = progress > previous_progress
    if new_progress_record:
        score_record[level_index] = progress
        stats["best_progress"] = progress
        save_dirty = True
    if current_score > stats["best_score"]:
        stats["best_score"] = current_score
        save_dirty = True
    return new_progress_record


def draw_board():
    """화면 중앙에 설정한 크기의 정사각형 보드를 그립니다."""
    center_x = display_size[0] // 2
    center_y = display_size[1] // 2
    board_start_x = center_x - BOARD_HALF_SIZE
    board_start_y = center_y - BOARD_HALF_SIZE
    for col in range(GRID_SIZE + 1):
        x = board_start_x + CELL_SIZE * col
        pygame.draw.line(dis, WHITE, (x, board_start_y), (x, board_start_y + GRID_SIZE * CELL_SIZE), 4)
    for row in range(GRID_SIZE + 1):
        y = board_start_y + CELL_SIZE * row
        pygame.draw.line(dis, WHITE, (board_start_x, y), (board_start_x + GRID_SIZE * CELL_SIZE, y), 4)


def get_best_level_progress(level_index: int) -> float:
    """저장 데이터의 구버전/신버전 기록 중 높은 진행률을 반환합니다."""
    return max(
        score_record[level_index],
        level_stats[level_index]["best_progress"]
    )


def is_boss_level_unlocked(level_index: int) -> bool:
    """현재 보스의 진행률 또는 선행 스테이지 클리어 조건을 검사합니다."""
    if level_index in debug_boss_unlock_overrides:
        return debug_boss_unlock_overrides[level_index]
    if level_index in BOSS_PROGRESS_REQUIREMENTS:
        required_levels, minimum_progress = BOSS_PROGRESS_REQUIREMENTS[level_index]
        return all(
            get_best_level_progress(required_level - 1) >= minimum_progress
            for required_level in required_levels
        )
    if level_index in BOSS_CLEAR_REQUIREMENTS:
        required_levels = BOSS_CLEAR_REQUIREMENTS[level_index]
        return all(
            level_stats[required_level - 1]["cleared"]
            for required_level in required_levels
        )
    return True


def is_level_locked(level_index: int) -> bool:
    """보스 단계라면 각 단계에 설정된 해금 조건을 적용합니다."""
    return (
        level_index in BOSS_LEVEL_INDICES
        and not is_boss_level_unlocked(level_index)
    )


def draw_selector_header(surface: Surface, title: str, subtitle: str) -> int:
    """맵 선택과 커스터마이징 화면에서 공유하는 우측 패널 헤더를 그립니다."""
    menu_text_x = display_size[0] - 260
    draw_ui_text(surface, title, (218, 223, 231, 220), (menu_text_x, 58), 27)
    draw_ui_text(surface, subtitle, LIGHT_GRAY, (menu_text_x, 91), 14)
    return menu_text_x


def draw_selector_row(
    surface: Surface,
    text: str,
    y: int,
    selected: bool,
    distance: int = 0,
    color: Optional[Tuple[int, ...]] = None
) -> None:
    """두 선택 화면이 공유하는 캐러셀 행과 포커스 표시를 렌더링합니다."""
    menu_text_x = display_size[0] - 260
    if selected:
        surface.blit(home_highlight_glow, (menu_text_x - 20, y - 29))
        pygame.draw.line(
            surface,
            (238, 243, 252, 208),
            (menu_text_x - 14, y - 19),
            (menu_text_x - 14, y + 19),
            2
        )
        draw_fitted_ui_text(
            surface,
            text,
            color or WHITE,
            (menu_text_x, y - 19),
            27,
            max_width=240,
            min_size=13
        )
        return

    alpha = max(38, round(178 * math.exp(-distance * 0.52)))
    row_color = color or (190, 195, 205, alpha)
    draw_fitted_ui_text(
        surface,
        text,
        row_color,
        (menu_text_x, y - max(8, 12 - distance)),
        max(14, 21 - distance),
        max_width=240,
        min_size=12
    )


def draw_home_menu(
    selected_level: int,
    fade_alpha: int,
    track_duration_seconds: float
) -> None:
    """음악 미리보기 위에 세로 레벨 캐러셀과 조작 안내를 표시합니다."""
    if fade_alpha > 0:
        home_fade_surface.fill((0, 0, 0, min(255, fade_alpha)))
        dis.blit(home_fade_surface, (0, 0))
    dis.blit(home_menu_gradient, (display_size[0] - home_menu_gradient.get_width(), 0))
    if selected_level == 0:
        stage_label = f"TUTORIAL  |  1 / {MAX_LEVEL}"
    elif selected_level in BOSS_LEVEL_INDICES:
        stage_label = f"BOSS STAGE  |  {selected_level + 1} / {MAX_LEVEL}"
    else:
        stage_label = f"STAGE  {selected_level + 1} / {MAX_LEVEL}"
    menu_text_x = draw_selector_header(dis, "SELECT A MAP", stage_label)

    for level_index, (name, creator) in enumerate(zip(LEVEL_NAMES, LEVEL_CREATORS)):
        offset = level_index - selected_level
        if abs(offset) > MAX_LEVEL // 2:
            continue
        y = display_size[1] // 2 + offset * 68
        if level_index == selected_level:
            locked_label = "  [LOCKED]" if is_level_locked(level_index) else ""
            draw_selector_row(
                dis,
                f"{name}{locked_label}",
                y,
                True,
                color=WHITE if not locked_label else (255, 206, 184)
            )
            draw_ui_text(dis, creator, (205, 211, 220, 210), (menu_text_x, y + 14), 14)
        else:
            distance = abs(offset)
            locked_label = " [LOCKED]" if is_level_locked(level_index) else ""
            draw_selector_row(
                dis,
                f"{name} ({creator}){locked_label}",
                y,
                False,
                distance
            )

    draw_ui_text(dis, "Created by", LIGHT_GRAY, (22, display_size[1] - 76), 16)
    draw_ui_text(
        dis,
        LEVEL_CREATORS[selected_level],
        WHITE,
        (22, display_size[1] - 54),
        18
    )
    selected_stats = level_stats[selected_level]
    clear_status = "CLEARED" if selected_stats["cleared"] else "NOT CLEARED"
    clear_color = GREEN if selected_stats["cleared"] else LIGHT_GRAY
    draw_ui_text(
        dis,
        f"{clear_status}  |  Best: {selected_stats['best_clear_rank']}",
        clear_color,
        (22, display_size[1] - 184),
        16
    )
    draw_ui_text(
        dis,
        f"Clears: {selected_stats['clear_count']}    Best: {selected_stats['best_progress']:.2f}%",
        LIGHT_GRAY,
        (22, display_size[1] - 158),
        15
    )
    draw_ui_text(
        dis,
        f"Best score: {selected_stats['best_score']}    Attempts: {selected_stats['total_attempts']}",
        LIGHT_GRAY,
        (22, display_size[1] - 132),
        14
    )
    draw_ui_text(
        dis,
        f"Track length: {format_track_time(track_duration_seconds)}",
        WHITE,
        (22, display_size[1] - 106),
        15
    )
    draw_ui_text(dis, "UP / DOWN  Select stage", LIGHT_GRAY, (menu_text_x, 790), 16)
    draw_ui_text(dis, "P  Player customize", LIGHT_GRAY, (menu_text_x, 842), 14)
    if is_level_locked(selected_level):
        if selected_level == 6:
            unlock_message = "LOCKED - CLEAR STAGES 1-6 AT 30%+"
            unlock_detail = "TO UNLOCK THE STAGE 7 BOSS"
        elif selected_level == 11:
            unlock_message = "LOCKED - CLEAR STAGES 10 AND 11"
            unlock_detail = "TO UNLOCK THE STAGE 12 BOSS"
        elif selected_level == 21:
            unlock_message = "LOCKED - CLEAR STAGES 17-21 AT 30%+"
            unlock_detail = "TO UNLOCK THE STAGE 22 BOSS"
        else:
            unlock_message = "LOCKED - CLEAR STAGES 1-22 AT 20%+"
            unlock_detail = "TO UNLOCK THE STAGE 23 BOSS"
        draw_ui_text(
            dis,
            unlock_message,
            (224, 228, 236, 220),
            (display_size[0] // 2, display_size[1] - 108),
            17,
            center=True
        )
        draw_ui_text(
            dis,
            unlock_detail,
            (174, 181, 192, 205),
            (display_size[0] // 2, display_size[1] - 82),
            14,
            center=True
        )
        draw_ui_text(dis, "[LOCKED]", (255, 174, 138, 235), (menu_text_x, 818), 18)
    else:
        draw_ui_text(dis, "ENTER  Start", WHITE, (menu_text_x, 818), 18)

def draw_customization_screen(
    selected_item: int,
    move_mode: bool,
    transition: float
) -> None:
    """맵 선택과 같은 우측 캐러셀, 타이포그래피 및 강조 스타일로 표시합니다."""
    customization_ui_layer.set_alpha(255)
    customization_ui_layer.fill((0, 0, 0, 0))
    ui = customization_ui_layer
    ui.blit(home_menu_gradient, (display_size[0] - home_menu_gradient.get_width(), 0))
    menu_text_x = draw_selector_header(
        ui,
        "CUSTOMIZE PLAYER",
        "COLOR / HIT EFFECT"
    )
    transition = max(0.0, min(1.0, transition))

    color_name = PLAYER_CUSTOMIZATION["color"]
    effect_name = PLAYER_CUSTOMIZATION["hit_effect"]
    values = (
        f"Color: {color_name.title()}",
        f"Hit Effect: {effect_name}"
    )
    selected_item = max(0, min(selected_item, len(values) - 1))
    descriptions = (
        "Player glow and hit particles use this color.",
        {
            "None": "No particles or flash appear when hit.",
            "Particles": "Small colored particles scatter on hit.",
            "Explosion": "A bright radial burst and ring on hit."
        }[effect_name]
    )
    center_y = display_size[1] // 2
    for item_index, value in enumerate(values):
        offset = item_index - selected_item
        y = center_y + offset * 68
        is_selected = item_index == selected_item
        draw_selector_row(
            ui,
            value,
            y,
            is_selected,
            abs(offset),
            WHITE if is_selected else None
        )

    description = descriptions[selected_item]
    draw_ui_text(
        ui,
        "SELECTED OPTION",
        LIGHT_GRAY,
        (22, display_size[1] - 184),
        16
    )
    draw_fitted_ui_text(
        ui,
        description,
        (218, 223, 231),
        (22, display_size[1] - 158),
        15,
        max_width=display_size[0] // 2,
        min_size=12
    )
    controls = (
        "ARROW KEYS  Move on grid"
        if move_mode
        else "UP / DOWN  Select option"
    )
    draw_ui_text(
        ui,
        controls,
        LIGHT_GRAY,
        (menu_text_x, 790),
        16
    )
    draw_ui_text(ui, "ESC  Toggle mode", LIGHT_GRAY, (menu_text_x, 818), 18)
    draw_ui_text(ui, "P  Map select", LIGHT_GRAY, (menu_text_x, 842), 14)

    if not move_mode:
        board_rect = pygame.Rect(
            display_size[0] // 2 - BOARD_HALF_SIZE,
            display_size[1] // 2 - BOARD_HALF_SIZE,
            BOARD_HALF_SIZE * 2,
            BOARD_HALF_SIZE * 2
        )
        customization_idle_layer.fill((0, 0, 0, 0))
        pygame.draw.rect(
            customization_idle_layer,
            (12, 15, 22, 52),
            board_rect
        )
        dis.blit(customization_idle_layer, (0, 0))

    ui.set_alpha(round(255 - 140 * transition))
    dis.blit(ui, (0, 0))

    customization_mode_indicator.fill((0, 0, 0, 0))
    indicator_color = (137, 255, 164) if move_mode else (238, 243, 252)
    pygame.draw.rect(
        customization_mode_indicator,
        (12, 15, 22, 220),
        customization_mode_indicator.get_rect(),
        border_radius=10
    )
    pygame.draw.rect(
        customization_mode_indicator,
        (*indicator_color, 190),
        customization_mode_indicator.get_rect(),
        width=1,
        border_radius=10
    )
    dis.blit(
        customization_mode_indicator,
        (
            display_size[0] // 2 - customization_mode_indicator.get_width() // 2,
            12
        )
    )
    mode_text = (
        "MODE: MOVE TEST  |  ESC: EDIT CUSTOMS"
        if move_mode
        else "MODE: CUSTOM SELECT  |  ESC: MOVE TEST"
    )
    draw_ui_text(
        dis,
        mode_text,
        indicator_color,
        (display_size[0] // 2, 33),
        15,
        center=True
    )


# ----------------------------------------------------------------------------
# 공통 텍스트·UI 도구: 폰트나 UI 위치를 바꿀 때 이 구역을 확인하세요.
# ----------------------------------------------------------------------------
class Text:
    """mining.py와 같은 데이터 형식으로 글자를 만들고 원하는 위치에 그립니다."""

    def __init__(self, text: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        # 같은 내용을 반복해서 그릴 때 글자 표면을 다시 만들지 않도록 캐시합니다.
        self.data = text if isinstance(text, list) else [text]
        self._lines = self._split_lines(self.data)
        cache_key = str(text)
        if cache_key in _text_cache:
            self._full_surface = _text_cache[cache_key]
            self._rect = self._full_surface.get_rect()
            return

        line_surfaces = [self._render_recursive(line) for line in self._lines]
        self._full_surface = self._combine_lines(line_surfaces)
        self._rect = self._full_surface.get_rect()
        _text_cache[cache_key] = self._full_surface

    @property
    def lines(self) -> list:
        return self._lines

    @property
    def width(self) -> int:
        return self._rect.width

    @property
    def height(self) -> int:
        return self._rect.height

    def _get_font(
        self,
        size: int,
        bold: bool,
        italic: bool,
        family: str = "game"
    ) -> pygame.font.Font:
        key = (size, bold, italic, family)
        if key not in _font_cache:
            if family == "monospace":
                font = pygame.font.SysFont("consolas", size, bold, italic)
            else:
                font = pygame.font.Font(FONT_PATH, size)
                font.set_bold(bold)
                font.set_italic(italic)
            _font_cache[key] = font
        return _font_cache[key]

    def _split_lines(self, data_list: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        lines: List[List[Dict[str, Any]]] = [[]]
        for item in data_list:
            display = item.get("display", {})
            content = display.get("text", "")
            if isinstance(content, dict):
                content = [content]

            if isinstance(content, list):
                nested_lines = self._split_lines(content)
                for index, line in enumerate(nested_lines):
                    new_item = item.copy()
                    new_item["display"] = display.copy()
                    new_item["display"]["text"] = line
                    lines[-1].append(new_item)
                    if index < len(nested_lines) - 1:
                        lines.append([])
            elif isinstance(content, str) and "\n" in content:
                parts = content.split("\n")
                for index, part in enumerate(parts):
                    new_item = item.copy()
                    new_item["display"] = display.copy()
                    new_item["display"]["text"] = part
                    lines[-1].append(new_item)
                    if index < len(parts) - 1:
                        lines.append([])
            else:
                lines[-1].append(item)
        return lines

    def _combine_lines(self, surfaces: List[Surface]) -> Surface:
        width = max((surface.get_width() for surface in surfaces), default=1)
        height = sum(surface.get_height() for surface in surfaces)
        combined = pygame.Surface((max(width, 1), max(height, 1)), pygame.SRCALPHA)
        current_y = 0
        for line_surface in surfaces:
            combined.blit(line_surface, (0, current_y))
            current_y += line_surface.get_height()
        return combined

    def _render_recursive(
        self,
        data_list: List[Dict[str, Any]],
        parent_style: Dict[str, Any] = None
    ) -> Surface:
        if parent_style is None:
            parent_style = {
                "color": WHITE,
                "font": {"size": 30, "bold": False, "italic": False},
                "angle": 0
            }

        rendered_items = []
        for item in data_list:
            display = item.get("display", {})
            current_font = parent_style["font"].copy()
            current_font.update(item.get("font", {}))
            current_style = {
                "color": display.get("color", parent_style["color"]),
                "font": current_font,
                "angle": parent_style["angle"] + item.get("angle", 0)
            }
            content = display.get("text", "")

            if isinstance(content, dict):
                content = [content]
            if isinstance(content, list):
                item_surface = self._render_recursive(content, current_style)
            else:
                font = self._get_font(
                    current_font["size"],
                    current_font.get("bold", False),
                    current_font.get("italic", False),
                    current_font.get("family", "game")
                )
                item_surface = font.render(str(content), True, current_style["color"][:3])
                if len(current_style["color"]) == 4:
                    item_surface.set_alpha(current_style["color"][3])

            if current_style["angle"]:
                item_surface = pygame.transform.rotate(item_surface, current_style["angle"])
            rendered_items.append(item_surface)

        if not rendered_items:
            return pygame.Surface((1, 1), pygame.SRCALPHA)

        line_width = sum(surface.get_width() for surface in rendered_items)
        line_height = max(surface.get_height() for surface in rendered_items)
        line_surface = pygame.Surface((max(line_width, 1), max(line_height, 1)), pygame.SRCALPHA)
        current_x = 0
        for item_surface in rendered_items:
            line_surface.blit(item_surface, (current_x, (line_height - item_surface.get_height()) // 2))
            current_x += item_surface.get_width()
        return line_surface

    def draw(
        self,
        surface: Surface,
        position: Tuple[int, int],
        locate: Tuple[str, str] = ("left", "top")
    ) -> None:
        """mining.py 호환 정렬명(left/center/right, top/middle/bottom)으로 표시합니다."""
        rect = self._rect.copy()
        horizontal = "centerx" if locate[0] == "center" else locate[0]
        vertical = "centery" if locate[1] == "middle" else locate[1]
        setattr(rect, horizontal, position[0])
        setattr(rect, vertical, position[1])
        surface.blit(self._full_surface, rect)


def draw_ui_text(
    surface: Surface,
    text: str,
    color: Union[Color, int, str, Tuple[int, int, int], Tuple[int, int, int, int], Sequence[int]],
    text_pos: Tuple[int, int],
    text_size: int = 20,
    text_angle: int = 0,
    center: bool = False,
    alignment: str = "left",
    font_family: str = "game"
):
    """JSON 스타일 명세를 Text 클래스로 렌더링해 화면에 표시합니다."""
    text_object = Text({
        "display": {"text": text, "color": color},
        "font": {"size": text_size, "family": font_family},
        "angle": text_angle
    })
    horizontal = "center" if center else alignment
    locate = (horizontal, "middle" if center else "top")
    text_object.draw(surface, text_pos, locate)


def draw_fitted_ui_text(
    surface: Surface,
    text: str,
    color: Union[Color, int, str, Tuple[int, int, int], Tuple[int, int, int, int], Sequence[int]],
    text_pos: Tuple[int, int],
    text_size: int,
    max_width: int,
    min_size: int = 10
) -> None:
    """같은 UI 폰트를 유지하면서 지정 폭 안에 들어오도록 글자 크기를 줄입니다."""
    fitted_size = text_size
    while fitted_size >= min_size:
        measured_text = Text({
            "display": {"text": text, "color": color},
            "font": {"size": fitted_size, "family": "game"}
        })
        if measured_text.width <= max_width:
            draw_ui_text(surface, text, color, text_pos, fitted_size)
            return
        fitted_size -= 1

    font = Text({"display": {"text": ""}})._get_font(
        min_size,
        False,
        False,
        "game"
    )
    fitted_text = text
    while fitted_text and font.size(f"{fitted_text}...")[0] > max_width:
        fitted_text = fitted_text[:-1]
    draw_ui_text(
        surface,
        f"{fitted_text.rstrip()}..." if fitted_text != text else text,
        color,
        text_pos,
        min_size
    )


def draw_hold_gauge(
    surface: Surface,
    label: str,
    progress: float,
    position: Tuple[int, int],
    color: Tuple[int, int, int],
    opaque: bool = False,
    right_aligned: bool = False
) -> None:
    """R 재시작과 ESC 홈 복귀에서 함께 사용하는 상단 홀드 게이지입니다."""
    x, y = position
    gauge_width, gauge_height = HOLD_GAUGE_SIZE
    progress = max(0.0, min(1.0, progress))
    gauge_x = x + 42
    if right_aligned:
        draw_ui_text(
            surface,
            label,
            color,
            (gauge_x - 8, y - 4),
            16,
            alignment="right"
        )
    else:
        draw_ui_text(surface, label, color, (x, y - 4), 16)
    background_color = (42, 46, 56, 255) if opaque else (210, 215, 225, 70)
    fill_alpha = 255 if opaque else 220
    pygame.draw.rect(
        surface,
        background_color,
        (gauge_x, y, gauge_width, gauge_height),
        border_radius=5
    )
    if progress > 0.0:
        pygame.draw.rect(
            surface,
            (*color, fill_alpha),
            (gauge_x, y, round(gauge_width * progress), gauge_height),
            border_radius=5
        )


def turn_brightness(
    color: Union[Color, int, str, Tuple[int, int, int], Tuple[int, int, int, int], Sequence[int]],
    factor: int = 1
    ) -> tuple[int, int, int]:
    """색상 각 채널의 밝기를 factor 비율로 조정합니다."""
    return tuple(min(255, max(0, round(c * factor))) for c in color)

def set_alpha(
    color: Union[Color, int, str, Tuple[int, int, int], Tuple[int, int, int, int], Sequence[int]],
    alpha: int = 255
    ) -> tuple[int, int, int, int]:
    """RGB 색상에 투명도 값을 더해 RGBA 색상으로 반환합니다."""
    return (color[0], color[1], color[2], min(255, max(0, int(alpha))))


# ----------------------------------------------------------------------------
# 장애물 업데이트: 이동 중 장애물 갱신, 삭제 및 충돌을 한 프레임 처리합니다.
# ----------------------------------------------------------------------------
def update_enemies():
    global enemies, hit_count, hit_stack
    if enemies:
        alive_enemies = []
        for enemy in enemies:
            hit_index = ENEMY_HIT_INDEX.get(type(enemy))
            if hit_index is not None:
                if not pause:
                    enemy.update()
                    if player is not None and player.hp_minus and not hit_stack:
                        hit_count[hit_index] += 1
                        hit_stack = True
            if not enemy.is_deleted():
                alive_enemies.append(enemy)
        enemies[:] = alive_enemies

        # 모든 궤도선을 먼저 그려 TBall 본체 뒤에 배치합니다.
        for enemy in enemies:
            if isinstance(enemy, TBall):
                enemy.draw_orbit()
        for enemy in enemies:
            if type(enemy) in ENEMY_HIT_INDEX and not isinstance(enemy, TBall):
                enemy.draw()
        for enemy in enemies:
            if isinstance(enemy, TBall):
                enemy.draw_body()




# ----------------------------------------------------------------------------
# 플레이어 이동·체력: 입력 이동, 무적 프레임, 피격 대기 시간을 관리합니다.
# ----------------------------------------------------------------------------
class Player(object):
    def __init__(
        self,
        position: Tuple[int, int] = (display_size[0]//2, display_size[1]//2),
        hp: int = 3,
        max_afterimage: int = 10,
        training_mode: bool = False
        ):
        # 이동 중 좌표를 수정할 수 있도록 전달받은 위치를 새 리스트로 복사합니다.
        self.pos = list(position)
        self.render_pos = [float(position[0]), float(position[1])]
        self.move_stack = 0
        self.move = [0, 0]
        self.move_rebound = [0.0, 0.0]
        self.hp = hp
        self.hp_minus = False
        self.hp_stack = 100
        self.color = PLAYER_COLOR_MAP[PLAYER_CUSTOMIZATION["color"]]
        self.invincible = False
        self.size = 50-(3-self.hp)*6
        self.afterimage = []
        self.afterimage_max = max_afterimage
        self.training_mode = training_mode
        self.hit_particles: List[List[float]] = []
        self.hit_flash_remaining = 0.0
        
        self.ai_dis = pygame.Surface((300, 300), pygame.SRCALPHA)
        self.dis = pygame.Surface((300, 300), pygame.SRCALPHA)
    
    def update(self, delta_time: Optional[float] = None):
        global pause, hit_stack
        if delta_time is None:
            delta_time = 1.0 / max(1, tps)
        delta_time = max(0.0, min(delta_time, 0.05))
        if self.move_stack != 0:
            movement = self.move_rebound if self.move_stack == 1 else self.move
            self.pos[0] += movement[0]
            self.pos[1] += movement[1]
            min_x = display_size[0] // 2 - GRID_EDGE_OFFSET
            max_x = display_size[0] // 2 + GRID_EDGE_OFFSET
            min_y = display_size[1] // 2 - GRID_EDGE_OFFSET
            max_y = display_size[1] // 2 + GRID_EDGE_OFFSET
            self.pos[0] = max(min_x, min(max_x, self.pos[0]))
            self.pos[1] = max(min_y, min(max_y, self.pos[1]))
            self.move_stack -= 1
            self.afterimage.append([self.pos.copy(), 128])
        if self.move_stack == 0:
            self.move = [0, 0]
            self.move_rebound = [0.0, 0.0]
        
        self.invincible = abs(self.move[0]) >= 30 or abs(self.move[1]) >= 30

        if self.hp_minus:
            if self.hp_stack == 100:
                self._start_hit_effect()
                if not self.training_mode:
                    self.hp -= 1
                    if self.hp == 0:
                        pause = True
            
            self.hp_stack -= 1/tps*50
        
        if self.hp_stack <= 0:
            self.hp_minus = False
            self.hp_stack = 100
            hit_stack = False

        self.size = 50-(3-max(self.hp, 0))*6
        self._update_hit_particles(delta_time)
        self.hit_flash_remaining = max(
            0.0,
            self.hit_flash_remaining - delta_time
        )
        # 논리 위치와 화면 위치를 분리해 작은 위치 변화도 매끄럽게 렌더링합니다.
        blend = 1.0 - math.exp(-PLAYER_RENDER_SMOOTHING_SPEED * delta_time)
        for axis in range(2):
            self.render_pos[axis] += (
                self.pos[axis] - self.render_pos[axis]
            ) * blend
            if abs(self.pos[axis] - self.render_pos[axis]) < 0.05:
                self.render_pos[axis] = float(self.pos[axis])

    def get_rect(self) -> pygame.Rect:
        hitbox_size = round((self.size - 10) * ELEMENT_SCALE)
        return pygame.Rect(
            round(self.pos[0] - hitbox_size / 2),
            round(self.pos[1] - hitbox_size / 2),
            hitbox_size,
            hitbox_size
        )

    def get_hitbox_radius(self) -> float:
        """복합 히트박스의 원형 영역 반지름을 반환합니다."""
        return max(0.0, (self.size - 10) * ELEMENT_SCALE / 2)

    def get_hitbox_square_half_size(self) -> float:
        """원형 영역과 함께 사용하는 정사각형 영역의 반쪽 길이입니다."""
        return self.get_hitbox_radius()

    def get_hitbox_square(self) -> pygame.Rect:
        """복합 히트박스의 정사각형 영역을 현재 플레이어 위치에 만듭니다."""
        half_size = self.get_hitbox_square_half_size()
        return pygame.Rect(
            round(self.pos[0] - half_size),
            round(self.pos[1] - half_size),
            max(1, round(half_size * 2)),
            max(1, round(half_size * 2))
        )

    def _start_hit_effect(self) -> None:
        """선택된 피격 효과에 맞춰 플레이어 주변에 파티클을 생성합니다."""
        effect = PLAYER_CUSTOMIZATION["hit_effect"]
        if effect == "None":
            return

        particle_count = 32 if effect == "Explosion" else 18
        speed_scale = 1.8 if effect == "Explosion" else 1.0
        if effect == "Explosion":
            self.hit_flash_remaining = 0.22
        for index in range(particle_count):
            angle = math.tau * index / particle_count + random.uniform(-0.15, 0.15)
            speed = random.uniform(90.0, 210.0) * speed_scale
            lifetime = random.uniform(0.35, 0.65) if effect == "Explosion" else 0.45
            self.hit_particles.append([
                float(self.pos[0]),
                float(self.pos[1]),
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                lifetime,
                lifetime,
                float(index % 2)
            ])

    def _update_hit_particles(self, delta_time: float) -> None:
        """파티클을 갱신하고 수명이 끝난 입자를 제거합니다."""
        for particle in self.hit_particles[:]:
            particle[0] += particle[2] * delta_time
            particle[1] += particle[3] * delta_time
            particle[3] += 180.0 * delta_time
            particle[4] -= delta_time
            if particle[4] <= 0:
                self.hit_particles.remove(particle)

    def draw(self):
        # 연두색 후광을 먼저 그리고, 흰색 코어를 별도 레이어로 겹칩니다.
        self.dis.fill((0, 0, 0, 0))
        glow_surface, core_surface = _get_player_vfx_surfaces(self.color)
        self.dis.blit(glow_surface, (0, 0))
        self.dis.blit(core_surface, (0, 0))
        if self.hit_flash_remaining > 0.0:
            flash_progress = 1.0 - self.hit_flash_remaining / 0.22
            flash_radius = round(86 + 58 * flash_progress)
            flash_alpha = round(150 * (1.0 - flash_progress))
            pygame.draw.circle(
                self.dis,
                (*self.color, flash_alpha),
                (150, 150),
                flash_radius,
                max(1, round(7 * (1.0 - flash_progress)))
            )
        if hitbox:
            hitbox_radius = round(
                self.get_hitbox_radius()
                * 300
                / max(1, self.size * 2 * ELEMENT_SCALE)
            )
            pygame.draw.circle(self.dis, BLUE, (150, 150), hitbox_radius, 3)
            square_half = round(
                self.get_hitbox_square_half_size()
                * 300
                / max(1, self.size * 2 * ELEMENT_SCALE)
            )
            pygame.draw.rect(
                self.dis,
                ORANGE,
                (
                    150 - square_half,
                    150 - square_half,
                    square_half * 2,
                    square_half * 2
                ),
                2
            )

        self.hp_stack_seq = 100-self.hp_stack
        if 0 < self.hp_stack_seq <= 20: player_alpha = 64
        elif 20 < self.hp_stack_seq <= 40: player_alpha = 255
        elif 40 < self.hp_stack_seq <= 60: player_alpha = 64
        elif 60 < self.hp_stack_seq <= 80: player_alpha = 255
        elif 80 < self.hp_stack_seq <= 100: player_alpha = 64
        else: player_alpha = 255

        render_size = max(1, round(self.size * 2 * ELEMENT_SCALE))
        self.player_painting = pygame.transform.smoothscale(
            self.dis,
            (render_size, render_size)
        )
        self.player_painting.set_alpha(player_alpha)

        for ai in self.afterimage:
            self.ai_dis = self.player_painting.copy()
            if not pause:
                ai[1] -= 128/self.afterimage_max
                if ai[1] <= 0: self.afterimage.remove(ai)
            self.ai_dis.set_alpha(ai[1])
            dis.blit(self.ai_dis, self.ai_dis.get_rect(center=(ai[0][0], ai[0][1])))

        for particle in self.hit_particles:
            remaining_ratio = max(0.0, particle[4] / particle[5])
            particle_size = max(1, round(5 * remaining_ratio))
            sprite = _get_hit_particle_sprite(
                self.color,
                bool(particle[6]),
                particle_size
            )
            sprite.set_alpha(round(255 * remaining_ratio))
            dis.blit(
                sprite,
                sprite.get_rect(
                    center=(round(particle[0]), round(particle[1]))
                )
            )

        dis.blit(
            self.player_painting,
            self.player_painting.get_rect(
                center=(round(self.render_pos[0]), round(self.render_pos[1]))
            )
        )


@lru_cache(maxsize=16)
def _get_player_vfx_surfaces(
    glow_color: Tuple[int, int, int]
) -> Tuple[Surface, Surface]:
    """색상별 연두빛 후광과 흰색 코어를 방사형 알파 표면으로 캐시합니다."""
    surface_size = 300
    center = (surface_size - 1) / 2
    face_radius = 84.0
    glow_radius = 142.0
    glow_surface = pygame.Surface(
        (surface_size, surface_size),
        pygame.SRCALPHA
    )
    core_surface = pygame.Surface(
        (surface_size, surface_size),
        pygame.SRCALPHA
    )

    for y in range(surface_size):
        for x in range(surface_size):
            distance = math.hypot(x - center, y - center)
            if distance < glow_radius:
                # 바깥 후광은 가장자리로 갈수록 알파가 빠르게 낮아집니다.
                glow_fade = 1.0 - (distance / glow_radius) ** 2
                glow_alpha = round(44 * glow_fade ** 2.4)
                if glow_alpha > 0:
                    glow_surface.set_at((x, y), (*glow_color, glow_alpha))

            if distance < face_radius:
                # 코어는 흰색을 유지하고 원의 테두리에서만 부드럽게 페이드됩니다.
                core_fade = 1.0 - (distance / face_radius) ** 2
                core_alpha = round(255 * core_fade ** 1.8)
                if core_alpha > 0:
                    core_surface.set_at(
                        (x, y),
                        (*WHITE, core_alpha)
                    )

    return glow_surface, core_surface


@lru_cache(maxsize=128)
def _get_hit_particle_sprite(
    color: Tuple[int, int, int],
    square: bool,
    size: int
) -> Surface:
    """색상·모양·크기별 작은 파티클 이미지를 재사용합니다."""
    side = size * 2 + 2
    surface = pygame.Surface((side, side), pygame.SRCALPHA)
    if square:
        pygame.draw.rect(surface, (*color, 255), (1, 1, size * 2, size * 2))
    else:
        pygame.draw.circle(surface, (*color, 255), (side // 2, side // 2), size)
    return surface


def _circles_overlap(
    center_a: Tuple[float, float],
    radius_a: float,
    center_b: Tuple[float, float],
    radius_b: float
) -> bool:
    """두 원의 중심 거리로 원형 충돌 여부를 판정합니다."""
    dx = center_a[0] - center_b[0]
    dy = center_a[1] - center_b[1]
    combined_radius = radius_a + radius_b
    return dx * dx + dy * dy <= combined_radius * combined_radius


def _circle_overlaps_rect(
    center: Tuple[float, float],
    radius: float,
    rect: pygame.Rect
) -> bool:
    """플레이어 원과 직사각형 레이저·통나무 사이의 가장 가까운 점을 검사합니다."""
    closest_x = max(rect.left, min(center[0], rect.right))
    closest_y = max(rect.top, min(center[1], rect.bottom))
    dx = center[0] - closest_x
    dy = center[1] - closest_y
    return dx * dx + dy * dy <= radius * radius


def _damage_player_for_circle(center: Tuple[float, float], radius: float) -> None:
    """원형 장애물과 플레이어의 원+정사각형 하이브리드 영역을 검사합니다."""
    if (
        player is None
        or player.hp <= 0
        or player.hp_minus
        or player.invincible
    ):
        return
    circle_hit = _circles_overlap(
        center, radius, player.pos, player.get_hitbox_radius()
    )
    square_hit = _circle_overlaps_rect(
        center, radius, player.get_hitbox_square()
    )
    if circle_hit or square_hit:
        player.hp_minus = True


def _damage_player_for_rect(rect: pygame.Rect) -> None:
    """직사각형 장애물과 플레이어의 원+정사각형 영역을 검사합니다."""
    if (
        player is None
        or player.hp <= 0
        or player.hp_minus
        or player.invincible
    ):
        return
    circle_hit = _circle_overlaps_rect(
        player.pos, player.get_hitbox_radius(), rect
    )
    square_hit = player.get_hitbox_square().colliderect(rect)
    if circle_hit or square_hit:
        player.hp_minus = True


def player_move(
    player: Player,
    keys
    ):
    """방향키 입력으로 플레이어를 한 칸 이동시키고 보드 경계에서 되돌립니다."""
    if player.move_stack != 0:
        return

    directions = (
        (pygame.K_UP, 1, -1),
        (pygame.K_DOWN, 1, 1),
        (pygame.K_LEFT, 0, -1),
        (pygame.K_RIGHT, 0, 1)
    )
    for key, axis, step in directions:
        if not keys[key]:
            continue

        min_position = display_size[axis] // 2 - GRID_EDGE_OFFSET
        max_position = display_size[axis] // 2 + GRID_EDGE_OFFSET
        current_index = round((player.pos[axis] - min_position) / CELL_SIZE)
        current_index = max(0, min(GRID_SIZE - 1, current_index))
        target_index = (current_index + step) % GRID_SIZE
        target_position = min_position + target_index * CELL_SIZE
        displacement = target_position - player.pos[axis]
        if displacement == 0:
            return

        direction = 1 if displacement > 0 else -1
        travel_distance = abs(displacement)
        is_wrap = abs(target_index - current_index) != 1
        # 보드 경계에 닿는 이동과 래핑 이동은 목표를 넘어가지 않도록 반동을 생략합니다.
        rebound_distance = (
            min(NORMAL_MOVE_SPEED, NORMAL_MOVE_SPEED * CELL_SIZE / travel_distance)
            if not is_wrap and 0 < target_index < GRID_SIZE - 1
            else 0.0
        )
        player.move = [0.0, 0.0]
        player.move_rebound = [0.0, 0.0]
        player.move_rebound[axis] = -direction * rebound_distance
        player.move[axis] = direction * (
            travel_distance + rebound_distance
        ) / (MOVE_DURATION - 1)
        player.move_stack = MOVE_DURATION
        return


# ----------------------------------------------------------------------------
# 장애물 종류별 동작: 각 클래스는 해당 장애물의 이동·그리기 로직을 담당합니다.
# 생성 주기와 레벨별 출현 빈도는 아래 spawn_level_N() 함수들에서 조절합니다.
# ----------------------------------------------------------------------------
class Ball(object):
    def configure(
        self,
        position: Tuple[int, int],
        speed: Tuple[float, float] = (5.0, 0.0)
        ):
        self.pos = position
        self.move = speed
        self.hitbox = pygame.Rect(0, 0, ENEMY_HITBOX_SIZE, ENEMY_HITBOX_SIZE)
        self.dis = ball_dis

    def update(self):
        self.pos = (self.pos[0]+self.move[0], self.pos[1]+self.move[1])
        self.hitbox.center = self.pos
        _damage_player_for_circle(self.pos, ENEMY_HITBOX_SIZE / 2)

    def is_deleted(
        self
        ) -> bool:
        if not -500 < self.pos[0] < display_size[0]+500 and not -400 < self.pos[1] < display_size[1]+400:
            return True
        return False

    def draw(
        self
        ):
        painting = _get_ball_sprite("white", hitbox)
        dis.blit(painting, painting.get_rect(center=self.pos))


def update_locked_preview_balls(
    balls: List[Ball],
    delta_time: float,
    spawn_timer: float,
    spawn_index: int
) -> Tuple[float, int]:
    """잠긴 보스 맵에서만 규칙적인 기본 공 패턴을 재생합니다."""
    spawn_timer += delta_time
    while spawn_timer >= 1.5:
        spawn_timer -= 1.5
        direction = 1 if spawn_index % 2 == 0 else -1
        board_left = display_size[0] // 2 - BOARD_HALF_SIZE
        board_right = display_size[0] // 2 + BOARD_HALF_SIZE
        lane_y = display_size[1] // 2
        spawn_x = board_left - 70 if direction > 0 else board_right + 70
        ball = Ball()
        ball.configure((spawn_x, lane_y), (direction * 2, 0))
        balls.append(ball)
        spawn_index += 1

    margin = ENEMY_HITBOX_SIZE
    for ball in balls[:]:
        ball.update()
        ball.draw()
        if (
            ball.pos[0] < -margin
            or ball.pos[0] > display_size[0] + margin
        ):
            balls.remove(ball)
    return spawn_timer, spawn_index


class TBall(object):
    def configure(
        self,
        position: Tuple[int, int, int],
        length: int,
        speed: int = 3,
        turn: float = 1,
        loop: bool = False
        ):
        self.position = position
        self.pos = position[0:2]
        self.angle = position[2]
        self.length = length
        self.speed = speed/length
        self.turn = turn
        self.loop = loop
        self.line_dis = _get_tball_ring(abs(length))
        self.stage = 0
        self.delay = tps*2
        self.delete = False
        self.hitbox = pygame.Rect(0, 0, ENEMY_HITBOX_SIZE, ENEMY_HITBOX_SIZE)
        self.dis = ball_dis

    def update(
        self
        ):
        if self.stage == 0:
            self.pos = [math.cos(self.angle)*self.length+self.position[0], math.sin(self.angle)*self.length+self.position[1]]
            self.delay -= 2
            if self.delay <= 0:
                self.stage = 1
        if self.stage == 1:
            self.pos = [math.cos(self.angle)*self.length+self.position[0], math.sin(self.angle)*self.length+self.position[1]]
            self.angle += self.speed
            if self.loop and abs(self.angle - self.position[2]) >= math.tau:
                self.angle = (
                    self.position[2]
                    + (self.angle - self.position[2]) % math.tau
                )
            elif not self.loop and abs(self.angle-self.position[2]) >= self.turn*2*math.pi:
                self.delete = True
            self.hitbox.center = self.pos
            _damage_player_for_circle(self.pos, ENEMY_HITBOX_SIZE / 2)
    
    def is_deleted(
        self
        ) -> bool:
        if self.delete:
            return True
        return False

    def draw(
        self
        ):
        self.draw_orbit()
        self.draw_body()

    def draw_orbit(self) -> None:
        dis.blit(self.line_dis, self.line_dis.get_rect(center=self.position[0:2]))

    def draw_body(self) -> None:
        if self.stage == 0:
            self.dis.fill(pygame.SRCALPHA)
            warning_size = round(66 * ELEMENT_SCALE)
            pygame.draw.arc(
                self.dis,
                RED,
                (50 - warning_size // 2, 50 - warning_size // 2, warning_size, warning_size),
                math.pi / 2,
                math.pi / 2 - self.delay / 100 * math.pi * 2,
                max(1, round(5 * ELEMENT_SCALE))
            )
            draw_ui_text(self.dis, "!", RED, (50, 50), round(50 * ELEMENT_SCALE), 0, True)
            dis.blit(self.dis, self.dis.get_rect(center=self.pos))
        else:
            painting = _get_ball_sprite("blue", hitbox)
            dis.blit(painting, painting.get_rect(center=self.pos))

class VBall(object):
    def configure(
        self,
        position: Tuple[int, int],
        face: int,
        target_cell: int,
        speed: Tuple[int, int]
        ):
        self.pos = position
        self.face = face
        axis = 1 if face in (0, 2) else 0
        target_coordinate = (
            display_size[axis] // 2
            - GRID_EDGE_OFFSET
            + target_cell * CELL_SIZE
        )
        start_coordinate = position[axis]
        displacement = target_coordinate - start_coordinate
        direction = 1 if displacement >= 0 else -1
        initial_speed = abs(speed[axis])
        self.apex_steps = max(
            2,
            round(2 * abs(displacement) / initial_speed) + 1
        )
        initial_speed = 2 * abs(displacement) / (self.apex_steps - 1)
        adjusted_speed = [0.0, 0.0]
        adjusted_speed[axis] = direction * initial_speed
        self.speed = tuple(adjusted_speed)
        self.spp = -initial_speed / self.apex_steps
        self.target_coordinate = target_coordinate
        self.delete = False
        self.hitbox = pygame.Rect(0, 0, ENEMY_HITBOX_SIZE, ENEMY_HITBOX_SIZE)
        self.dis = ball_dis

    def update(
        self
        ):
        if self.face == 0:
            self.speed = (self.speed[0], self.speed[1] + self.spp)
        elif self.face == 1:
            self.speed = (self.speed[0] - self.spp, self.speed[1])
        elif self.face == 2:
            self.speed = (self.speed[0], self.speed[1] - self.spp)
        else:
            self.speed = (self.speed[0] + self.spp, self.speed[1])

        self.pos = (
            self.pos[0] + self.speed[0],
            self.pos[1] + self.speed[1]
        )
        if self.apex_steps > 0:
            self.apex_steps -= 1
            if self.apex_steps == 0:
                axis = 1 if self.face in (0, 2) else 0
                if axis == 0:
                    self.pos = (self.target_coordinate, self.pos[1])
                    self.speed = (0.0, self.speed[1])
                else:
                    self.pos = (self.pos[0], self.target_coordinate)
                    self.speed = (self.speed[0], 0.0)
        self.hitbox.center = self.pos
        _damage_player_for_circle(self.pos, ENEMY_HITBOX_SIZE / 2)

    def is_deleted(
        self
        ) -> bool:
        margin = 500
        return (
            self.delete
            or self.pos[0] < -margin
            or self.pos[0] > display_size[0] + margin
            or self.pos[1] < -margin
            or self.pos[1] > display_size[1] + margin
        )

    def draw(
        self
        ):
        painting = _get_ball_sprite("pink", hitbox)
        dis.blit(painting, painting.get_rect(center=self.pos))


class Log(object):
    """여러 칸 길이로 보드를 가로질러 굴러오는 통나무 장애물입니다."""

    thickness = round(72 * ELEMENT_SCALE)
    speed = 3 * ELEMENT_SCALE

    def configure(self, position: Tuple[float, float], face: int, length_cells: int) -> None:
        self.pos = [float(position[0]), float(position[1])]
        self.face = face
        self.length_cells = length_cells
        self.length = length_cells * CELL_SIZE - LOG_END_INSET
        self.roll_angle = 0.0
        self.delete = False
        self.hitbox = pygame.Rect(0, 0, self.length, self.thickness)
        self._update_hitbox()

    def _update_hitbox(self) -> None:
        x, y = round(self.pos[0]), round(self.pos[1])
        if self.face in (0, 2):
            self.hitbox = pygame.Rect(
                x - self.length // 2,
                y - self.thickness // 2,
                self.length,
                self.thickness
            )
        else:
            self.hitbox = pygame.Rect(
                x - self.thickness // 2,
                y - self.length // 2,
                self.thickness,
                self.length
            )

    def update(self) -> None:
        direction = 1 if self.face in (0, 3) else -1
        if self.face in (0, 2):
            self.pos[1] += direction * self.speed
        else:
            self.pos[0] += direction * self.speed
        self.roll_angle += self.speed / (self.thickness / 2)
        self._update_hitbox()

        _damage_player_for_rect(self.hitbox)

        has_left_play_area = (
            (self.face == 0 and self.hitbox.top >= display_size[1])
            or (self.face == 1 and self.hitbox.right <= 0)
            or (self.face == 2 and self.hitbox.bottom <= 0)
            or (self.face == 3 and self.hitbox.left >= display_size[0])
        )
        if has_left_play_area:
            self.delete = True

    def is_deleted(self) -> bool:
        return self.delete

    def draw(self) -> None:
        roll_frame = int(self.roll_angle * 16 / (2 * math.pi)) % 16
        painting = _get_log_sprite(self.length_cells, roll_frame, self.face in (1, 3))
        self.surface = painting
        dis.blit(painting, painting.get_rect(center=(round(self.pos[0]), round(self.pos[1]))))
        if hitbox:
            pygame.draw.rect(dis, ORANGE, self.hitbox, 1)


class Laser(object):
    def configure(
        self,
        position: Tuple[int, int],
        face: int
        ):
        self.pos = position
        self.face = face
        self.stage = 0
        self.speed = 6.28
        self.delay = 0
        self.delete = False
        self.hitbox = pygame.Rect(0, 0, round(50 * ELEMENT_SCALE), LASER_LENGTH)

    def _get_beam_rect(self) -> pygame.Rect:
        """장치 앞에서 발사 방향으로 길게 뻗는 빔의 충돌 영역을 반환합니다."""
        x, y = self.pos
        beam_width = round(50 * ELEMENT_SCALE)
        beam_start = round(70 * ELEMENT_SCALE)
        beam_length = LASER_LENGTH - round(120 * ELEMENT_SCALE)
        if self.face == 0:
            return pygame.Rect(x - beam_width // 2, y + beam_start, beam_width, beam_length)
        if self.face == 1:
            return pygame.Rect(
                x - LASER_LENGTH + round(50 * ELEMENT_SCALE),
                y - beam_width // 2,
                beam_length,
                beam_width
            )
        if self.face == 2:
            return pygame.Rect(
                x - beam_width // 2,
                y - LASER_LENGTH + round(50 * ELEMENT_SCALE),
                beam_width,
                beam_length
            )
        return pygame.Rect(x + beam_start, y - beam_width // 2, beam_length, beam_width)
    
    def update(
        self
        ):
        if self.stage == 0:
            if self.face == 0:
                self.pos = [self.pos[0], self.pos[1]+self.speed]
                if self.pos[1] >= display_size[1]//2-BOARD_HALF_SIZE-CELL_SIZE:
                    self.stage = 1
            if self.face == 1:
                self.pos = [self.pos[0]-self.speed, self.pos[1]]
                if self.pos[0] <= display_size[0]//2+BOARD_HALF_SIZE+CELL_SIZE:
                    self.stage = 1
            if self.face == 2:
                self.pos = [self.pos[0], self.pos[1]-self.speed]
                if self.pos[1] <= display_size[1]//2+BOARD_HALF_SIZE+CELL_SIZE:
                    self.stage = 1
            if self.face == 3:
                self.pos = [self.pos[0]+self.speed, self.pos[1]]
                if self.pos[0] >= display_size[0]//2-BOARD_HALF_SIZE-CELL_SIZE:
                    self.stage = 1
            self.speed -= 0.1
            self.delay = tps
        
        if self.stage == 1:
            self.delay -= 1
            if self.delay <= 0:
                self.delay = max(1, round(tps * LASER_BEAM_DURATION_SECONDS))
                self.stage = 2

        if self.stage == 2:
            self.delay -= 1
            self.hitbox = self._get_beam_rect()
            _damage_player_for_rect(self.hitbox)
            if self.delay <= 0:
                self.stage = 3

        if self.stage == 3:
            if self.face == 0:
                self.pos = [self.pos[0], self.pos[1]-LASER_RETRACT_SPEED]
                if self.pos[1] <= display_size[1]//2-BOARD_HALF_SIZE-2*CELL_SIZE:
                    self.delete = True
            if self.face == 1:
                self.pos = [self.pos[0]+LASER_RETRACT_SPEED, self.pos[1]]
                if self.pos[0] >= display_size[0]//2+BOARD_HALF_SIZE+3*CELL_SIZE:
                    self.delete = True
            if self.face == 2:
                self.pos = [self.pos[0], self.pos[1]+LASER_RETRACT_SPEED]
                if self.pos[1] >= display_size[1]//2+BOARD_HALF_SIZE+2*CELL_SIZE:
                    self.delete = True
            if self.face == 3:
                self.pos = [self.pos[0]-LASER_RETRACT_SPEED, self.pos[1]]
                if self.pos[0] <= display_size[0]//2-BOARD_HALF_SIZE-3*CELL_SIZE:
                    self.delete = True
    
    def is_deleted(
        self
        ) -> bool:
        if self.delete:
            return True
        return False
    
    def draw(
        self
        ):
        x, y = round(self.pos[0]), round(self.pos[1])
        if self.stage in (1, 2):
            beam_offset = LASER_LENGTH // 2 - round(50 * ELEMENT_SCALE)
            beam_center_offsets = (
                (0, beam_offset),
                (-beam_offset, 0),
                (0, -beam_offset),
                (beam_offset, 0)
            )
            beam_center = (
                x + beam_center_offsets[self.face][0],
                y + beam_center_offsets[self.face][1]
            )
            beam_painting = _get_laser_beam(self.stage, self.delay, self.face)
            dis.blit(beam_painting, beam_painting.get_rect(center=beam_center))
            if hitbox and self.stage == 2:
                pygame.draw.rect(dis, RED, self.hitbox, 1)

        device_painting = _get_laser_device(self.face, hitbox)
        dis.blit(device_painting, device_painting.get_rect(center=(x, y)))


class Bomb:
    """맵에 직접 생성되어 충전한 뒤 서브 폭탄 파동을 시작하는 메인 폭탄입니다."""

    # 로마 숫자 인덱스와 chain_range(0~3)의 순서를 맞춥니다.
    ROMAN_RANGES = ("I", "II", "III", "IV")

    def configure(
        self,
        row: int,
        column: int,
        chain_range: int,
        diagonal_chain: bool
    ) -> None:
        self.row = row
        self.column = column
        self.chain_range = max(0, min(3, chain_range))
        self.diagonal_chain = diagonal_chain
        self.state = "charging"
        self.charge_seconds = BOMB_CHARGE_SECONDS
        self.charge_remaining = self.charge_seconds
        self.explosion_remaining = 0.0
        self.pos = self._get_cell_center(row, column)
        self.sub_bombs: List[SubBomb] = []
        self.visited_cells: Set[Tuple[int, int]] = {(row, column)}

    @staticmethod
    def _get_cell_center(row: int, column: int) -> Tuple[int, int]:
        left = display_size[0] // 2 - BOARD_HALF_SIZE
        top = display_size[1] // 2 - BOARD_HALF_SIZE
        return (
            left + column * CELL_SIZE + CELL_SIZE // 2,
            top + row * CELL_SIZE + CELL_SIZE // 2
        )

    @property
    def charge_progress(self) -> float:
        if self.charge_seconds <= 0:
            return 1.0
        return max(
            0.0,
            min(1.0, 1.0 - self.charge_remaining / self.charge_seconds)
        )

    def update(self, delta_time: float, target_player) -> None:
        """충전, 메인 폭발, 미리 정한 서브 폭탄 연쇄를 순서대로 처리합니다."""
        delta_time = max(0.0, delta_time)
        if self.state == "charging":
            self.charge_remaining -= delta_time
            if self.charge_remaining <= 1e-12:
                self.state = "exploding"
                self.explosion_remaining = BOMB_DAMAGE_WINDOW_SECONDS
                self._prepare_chain()

        elif self.state == "exploding":
            self._damage_player_in_blast_cell(target_player)
            self.explosion_remaining -= delta_time
            if self.explosion_remaining <= 1e-12:
                self.state = "chaining"

        elif self.state == "chaining":
            for sub_bomb in self.sub_bombs:
                sub_bomb.update(delta_time, target_player)
            self.sub_bombs = [
                sub_bomb for sub_bomb in self.sub_bombs
                if sub_bomb.state != "done"
            ]
        if self.state == "chaining" and not self.sub_bombs:
            self.state = "done"

    def _prepare_chain(self) -> None:
        """거리별 연쇄 타일을 미리 예약해 서브 폭탄의 무한 재연쇄를 막습니다."""
        chain_cells = get_bomb_chain_cells(
            self.row,
            self.column,
            self.chain_range,
            self.diagonal_chain
        )
        for target_row, target_column, distance in chain_cells:
            cell = (target_row, target_column)
            if cell in self.visited_cells:
                continue
            self.visited_cells.add(cell)
            self._add_sub_bomb(
                target_row,
                target_column,
                # 1칸 거리 웨이브는 즉시, 이후 웨이브는 설정 간격만큼 늦춥니다.
                (distance - 1) * BOMB_CHAIN_DELAY_SECONDS
            )

    def _add_sub_bomb(
        self,
        row: int,
        column: int,
        trigger_delay: float
    ) -> None:
        sub_bomb = SubBomb()
        sub_bomb.configure(
            row,
            column,
            self.diagonal_chain,
            trigger_delay
        )
        self.sub_bombs.append(sub_bomb)

    def _damage_player_in_blast_cell(self, target_player) -> None:
        if (
            target_player is None
            or target_player.hp <= 0
            or target_player.hp_minus
            or target_player.invincible
        ):
            return
        left = display_size[0] // 2 - BOARD_HALF_SIZE
        top = display_size[1] // 2 - BOARD_HALF_SIZE
        player_column = math.floor((target_player.pos[0] - left) / CELL_SIZE)
        player_row = math.floor((target_player.pos[1] - top) / CELL_SIZE)
        if player_row == self.row and player_column == self.column:
            target_player.hp_minus = True

    @staticmethod
    def _damage_player_on_cell(row: int, column: int, target_player) -> None:
        left = display_size[0] // 2 - BOARD_HALF_SIZE
        top = display_size[1] // 2 - BOARD_HALF_SIZE
        player_column = math.floor((target_player.pos[0] - left) / CELL_SIZE)
        player_row = math.floor((target_player.pos[1] - top) / CELL_SIZE)
        if player_row == row and player_column == column:
            target_player.hp_minus = True

    def get_occupied_cells(self) -> Set[Tuple[int, int]]:
        """현재 메인 폭탄과 활성 서브 폭탄이 차지한 보드 칸을 반환합니다."""
        occupied = {(self.row, self.column)}
        occupied.update(
            (sub_bomb.row, sub_bomb.column)
            for sub_bomb in self.sub_bombs
            if sub_bomb.state != "done"
        )
        return occupied


    def draw(self) -> None:
        if self.state == "charging":
            canvas = _draw_bomb_shape(
                self.diagonal_chain,
                self.charge_progress,
                self.ROMAN_RANGES[self.chain_range],
                fill_both=False
            )
            dis.blit(canvas, canvas.get_rect(center=self.pos))
        elif self.state == "exploding":
            canvas = _draw_bomb_shape(
                self.diagonal_chain,
                1.0,
                self.ROMAN_RANGES[self.chain_range],
                fill_both=False
            )
            _draw_bomb_explosion(canvas, self.pos, self.explosion_remaining)
        for sub_bomb in self.sub_bombs:
            sub_bomb.draw()


class SubBomb:
    """메인 폭탄의 연쇄 칸에서 대기·폭발·피격을 독립적으로 처리합니다."""

    def configure(
        self,
        row: int,
        column: int,
        diagonal_chain: bool,
        trigger_delay: float
    ) -> None:
        self.row = row
        self.column = column
        self.diagonal_chain = diagonal_chain
        # 이 지연은 폭발까지 남은 시간이며 같은 거리의 서브 폭탄에는 같은 값이 들어갑니다.
        self.trigger_delay = max(0.0, trigger_delay)
        self.state = "waiting"
        self.explosion_remaining = 0.0
        self.pos = Bomb._get_cell_center(row, column)

    def update(self, delta_time: float, target_player) -> None:
        """지연 후 폭발하고 정해진 짧은 시간 동안 해당 타일에 피해를 줍니다."""
        delta_time = max(0.0, delta_time)
        active_delta = delta_time
        if self.state == "waiting":
            if delta_time + 1e-12 < self.trigger_delay:
                self.trigger_delay -= delta_time
                return
            active_delta = max(0.0, delta_time - self.trigger_delay)
            self.trigger_delay = 0.0
            self.state = "exploding"
            self.explosion_remaining = BOMB_DAMAGE_WINDOW_SECONDS

        if self.state != "exploding":
            return

        self._damage_player_in_blast_cell(target_player)
        self.explosion_remaining -= active_delta
        if self.explosion_remaining <= 1e-12:
            self.state = "done"

    def _damage_player_in_blast_cell(self, target_player) -> None:
        if (
            target_player is None
            or target_player.hp <= 0
            or target_player.hp_minus
            or target_player.invincible
        ):
            return
        Bomb._damage_player_on_cell(self.row, self.column, target_player)

    def draw(self) -> None:
        if self.state != "exploding":
            return

        canvas = _draw_bomb_shape(
            self.diagonal_chain,
            1.0,
            fill_both=False
        )
        _draw_bomb_explosion(canvas, self.pos, self.explosion_remaining)


def _draw_bomb_shape(
    diagonal_chain: bool,
    fill_progress: float,
    label: Optional[str] = None,
    fill_both: bool = False
) -> Surface:
    """두 정사각형을 겹쳐 폭탄의 8각별 충전·폭발 모양을 그립니다."""
    side = BOMB_SHAPE_SIZE
    canvas = pygame.Surface((side, side), pygame.SRCALPHA)
    square_side = round(side * 0.62)

    def draw_square(angle: float, fill_square: bool, progress: float) -> None:
        square = pygame.Surface((square_side, square_side), pygame.SRCALPHA)
        if fill_square and progress > 0.0:
            fill_side = max(1, round(square_side * min(1.0, progress)))
            pygame.draw.rect(
                square,
                BLACK,
                (
                    (square_side - fill_side) // 2,
                    (square_side - fill_side) // 2,
                    fill_side,
                    fill_side
                )
            )
        pygame.draw.rect(square, BLACK, (0, 0, square_side, square_side), 2)
        if angle:
            square = pygame.transform.rotate(square, angle)
        canvas.blit(
            square,
            square.get_rect(center=(canvas.get_width() // 2, canvas.get_height() // 2))
        )

    # 메인 폭탄은 방향에 맞는 사각형만 충전하고 서브 폭탄은 둘 다 채웁니다.
    draw_square(
        0,
        fill_both or not diagonal_chain,
        fill_progress if not diagonal_chain else 1.0
    )
    draw_square(
        45,
        fill_both or diagonal_chain,
        fill_progress if diagonal_chain else 1.0
    )
    if label is not None:
        draw_ui_text(
            canvas,
            label,
            WHITE,
            (side // 2, side // 2),
            max(12, round(side * 0.24)),
            center=True
        )
    return canvas


def _draw_bomb_explosion(
    canvas: Surface,
    position: Tuple[int, int],
    remaining_seconds: float
) -> None:
    """폭발 표면을 천천히 시계 방향으로 돌리며 부풀렸다가 축소합니다."""
    progress = max(
        0.0,
        min(1.0, 1.0 - remaining_seconds / BOMB_DAMAGE_WINDOW_SECONDS)
    )
    # 전체 폭발 애니메이션의 앞 20% 동안 커지고, 나머지 80% 동안 작아집니다.
    swell_progress = 0.2
    if progress <= swell_progress:
        scale = 1.0 + 0.8 * progress / swell_progress
    else:
        shrink_progress = (progress - swell_progress) / (1.0 - swell_progress)
        scale = 1.8 * (1.0 - shrink_progress)
    if scale <= 0.02:
        return
    rotated = pygame.transform.rotate(
        canvas,
        -BOMB_EXPLOSION_ROTATION_DEGREES * progress
    )
    scaled_size = max(1, round(BOMB_SHAPE_SIZE * scale))
    scaled = pygame.transform.smoothscale(
        rotated,
        (scaled_size, scaled_size)
    )
    dis.blit(scaled, scaled.get_rect(center=position))


def get_bomb_chain_cells(
    row: int,
    column: int,
    chain_range: int,
    diagonal_chain: bool
) -> List[Tuple[int, int, int]]:
    """(행, 열, 거리) 목록을 거리순으로 반환해 같은 거리 웨이브를 동시에 처리합니다."""
    directions = (
        ((-1, -1), (-1, 1), (1, -1), (1, 1))
        if diagonal_chain
        else ((-1, 0), (1, 0), (0, -1), (0, 1))
    )
    cells = []
    for distance in range(1, max(0, min(3, chain_range)) + 1):
        for row_step, column_step in directions:
            target_row = row + row_step * distance
            target_column = column + column_step * distance
            if 0 <= target_row < GRID_SIZE and 0 <= target_column < GRID_SIZE:
                cells.append((target_row, target_column, distance))
    return cells


class BombManager:
    """메인 폭탄의 생성과 고정 간격 업데이트를 담당하는 얇은 관리자입니다."""

    def __init__(self) -> None:
        self.bombs: List[Bomb] = []
        self._simulation_accumulator = 0.0

    def reset_for_level(self) -> None:
        """새 플레이 시도의 폭탄 및 연쇄 상태를 초기화합니다."""
        self.bombs.clear()
        self._simulation_accumulator = 0.0

    def spawn(
        self,
        row: Optional[int] = None,
        column: Optional[int] = None,
        chain_count: Optional[int] = None,
        pattern: Optional[str] = None
    ) -> bool:
        """빈 보드 칸에 연쇄 범위와 십자/대각선 패턴을 지정해 폭탄을 생성합니다."""
        if (row is None) != (column is None):
            raise ValueError("폭탄 스폰 좌표는 행과 열을 함께 지정해야 합니다.")
        if row is not None and column is not None:
            if (
                not isinstance(row, int)
                or isinstance(row, bool)
                or not isinstance(column, int)
                or isinstance(column, bool)
                or not (0 <= row < GRID_SIZE and 0 <= column < GRID_SIZE)
            ):
                raise ValueError("폭탄 스폰 좌표가 보드 범위를 벗어났습니다.")
        if chain_count is None:
            chain_count = random.randint(0, 3)
        if (
            not isinstance(chain_count, int)
            or isinstance(chain_count, bool)
            or not 0 <= chain_count <= 3
        ):
            raise ValueError("폭탄 연쇄 수는 0부터 3 사이의 정수여야 합니다.")
        if pattern is None:
            pattern = random.choice(("+", "x"))
        if pattern not in ("+", "x"):
            raise ValueError("폭탄 패턴은 '+' 또는 'x'여야 합니다.")

        occupied_cells = {
            cell
            for bomb in self.bombs
            if bomb.state != "done"
            for cell in bomb.get_occupied_cells()
        }
        available_cells = [
            (row, column)
            for row in range(GRID_SIZE)
            for column in range(GRID_SIZE)
            if (row, column) not in occupied_cells
        ]
        if not available_cells:
            return False

        if row is None or column is None:
            row, column = random.choice(available_cells)
        elif (row, column) not in available_cells:
            return False

        bomb = Bomb()
        bomb.configure(
            row,
            column,
            chain_count,
            pattern == "x"
        )
        self.bombs.append(bomb)
        return True

    def update(self, delta_time: float, target_player) -> None:
        """dt 기반 고정 스텝으로 각 메인 폭탄과 내부 연쇄 파동을 갱신합니다."""
        self._simulation_accumulator += max(0.0, delta_time)
        while (
            self._simulation_accumulator + 1e-12
            >= BOMB_SIMULATION_STEP
        ):
            for bomb in self.bombs:
                bomb.update(BOMB_SIMULATION_STEP, target_player)
            self.bombs = [bomb for bomb in self.bombs if bomb.state != "done"]
            self._simulation_accumulator = max(
                0.0,
                self._simulation_accumulator - BOMB_SIMULATION_STEP
            )
        self.draw()

    def draw(self) -> None:
        """현재 활성 상태의 모든 폭탄을 그립니다."""
        for bomb in self.bombs:
            bomb.draw()


SPAWN_DIRECTIONS = ("top", "right", "bottom", "left")
SPAWN_FACE_BY_DIRECTION = dict(zip(SPAWN_DIRECTIONS, range(4)))
DEFAULT_LANES = tuple(range(1, GRID_SIZE + 1))
DEFAULT_DIRECTIONS = SPAWN_DIRECTIONS
DEFAULT_COORDINATES = tuple(range(GRID_SIZE))
DEFAULT_TBALL_LENGTHS = (1, 2, 3, 4, 5)
DEFAULT_TBALL_TURNS = (1, 2)
DEFAULT_TBALL_ROTATION_DIRECTIONS = ("+", "-")
DEFAULT_VBALL_DISTANCES = tuple(range(1, GRID_SIZE + 1))
DEFAULT_LOG_LENGTHS = (3, 5, 7)
DEFAULT_BOMB_CHAIN_COUNTS = (0, 1, 2, 3)
DEFAULT_BOMB_PATTERNS = ("+", "x")


def get_spawn_coordinates(direction: str, lane: int) -> Tuple[int, int]:
    """시계 방향의 1~7번 진입 레인을 보드의 (행, 열)로 바꿉니다."""
    if direction not in SPAWN_DIRECTIONS:
        raise ValueError(
            f"스폰 방향은 {', '.join(SPAWN_DIRECTIONS)} 중 하나여야 합니다."
        )
    if (
        not isinstance(lane, int)
        or isinstance(lane, bool)
        or not 1 <= lane <= GRID_SIZE
    ):
        raise ValueError(f"레인은 1부터 {GRID_SIZE} 사이여야 합니다.")

    lane_index = lane - 1
    if direction == "top":
        return 0, lane_index
    if direction == "right":
        return lane_index, GRID_SIZE - 1
    if direction == "bottom":
        return GRID_SIZE - 1, GRID_SIZE - 1 - lane_index
    return GRID_SIZE - 1 - lane_index, 0


def _get_grid_cell_center(row: int, column: int) -> Tuple[int, int]:
    """보드의 0부터 시작하는 행·열 인덱스를 화면 좌표 중심으로 바꿉니다."""
    if (
        not isinstance(row, int)
        or isinstance(row, bool)
        or not isinstance(column, int)
        or isinstance(column, bool)
        or not (0 <= row < GRID_SIZE and 0 <= column < GRID_SIZE)
    ):
        raise ValueError("스폰 좌표가 보드 범위를 벗어났습니다.")
    board_left = display_size[0] // 2 - BOARD_HALF_SIZE
    board_top = display_size[1] // 2 - BOARD_HALF_SIZE
    return (
        board_left + column * CELL_SIZE + CELL_SIZE // 2,
        board_top + row * CELL_SIZE + CELL_SIZE // 2
    )


def _get_spawn_edge_position(
    row: int,
    column: int,
    direction: str,
    outside_cells: int
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """진입 타일과 방향에 맞춘 화면 가장자리 좌표·기본 속도를 계산합니다."""
    lane_x, lane_y = _get_grid_cell_center(row, column)
    board_left = display_size[0] // 2 - BOARD_HALF_SIZE
    board_right = display_size[0] // 2 + BOARD_HALF_SIZE
    board_top = display_size[1] // 2 - BOARD_HALF_SIZE
    board_bottom = display_size[1] // 2 + BOARD_HALF_SIZE
    if direction == "top":
        return (lane_x, board_top - outside_cells * CELL_SIZE), (0, 1)
    if direction == "right":
        return (board_right + outside_cells * CELL_SIZE, lane_y), (-1, 0)
    if direction == "bottom":
        return (lane_x, board_bottom + outside_cells * CELL_SIZE), (0, -1)
    return (board_left - outside_cells * CELL_SIZE, lane_y), (1, 0)


def _choose_spawn_value(pool: tuple, name: str) -> Any:
    """필수 튜플 풀에서 가중치를 보존해 하나를 고릅니다."""
    if not isinstance(pool, tuple) or not pool:
        raise ValueError(f"{name}은(는) 하나 이상의 값을 가진 튜플이어야 합니다.")
    return random.choice(pool)


def _choose_spawn_lane(lane_pool: Tuple[int, ...]) -> int:
    """1~7 레인 튜플에서 한 레인을 고릅니다."""
    lane = _choose_spawn_value(lane_pool, "lane_pool")
    if (
        not isinstance(lane, int)
        or isinstance(lane, bool)
        or not 1 <= lane <= GRID_SIZE
    ):
        raise ValueError(f"선택된 레인은 1부터 {GRID_SIZE} 사이여야 합니다.")
    return lane


def _choose_spawn_direction(direction_pool: Tuple[str, ...]) -> str:
    """방향 튜플에서 한 방향을 고릅니다."""
    direction = _choose_spawn_value(direction_pool, "direction_pool")
    if not isinstance(direction, str) or direction not in SPAWN_DIRECTIONS:
        raise ValueError(
            f"선택된 방향은 {', '.join(SPAWN_DIRECTIONS)} 중 하나여야 합니다."
        )
    return direction


def spawn_ball(
    lane_pool: Tuple[int, ...],
    direction_pool: Tuple[str, ...]
) -> None:
    """레인·방향 풀로 위치를 정해 일반 공을 생성합니다."""
    lane = _choose_spawn_lane(lane_pool)
    direction = _choose_spawn_direction(direction_pool)
    row, col = get_spawn_coordinates(direction, lane)
    position, travel = _get_spawn_edge_position(row, col, direction, 3)
    speed = (
        travel[0] * 3 * BALL_SPEED_SCALE,
        travel[1] * 3 * BALL_SPEED_SCALE
    )
    for _ in range(20):
        ball = Ball()
        ball.configure(position, speed)
        if _try_add_enemy(ball):
            return

def spawn_tball(
    x_pool: Tuple[int, ...],
    y_pool: Tuple[int, ...],
    length_pool: Tuple[int, ...],
    turns_pool: Tuple[int, ...],
    rot_dir_pool: Tuple[str, ...],
    allow_same_type_overlap: bool = False
) -> None:
    """보드 좌표, 궤도 길이(칸), 회전 수 풀에서 TBall 속성을 뽑습니다."""
    x = _choose_spawn_value(x_pool, "x_pool")
    y = _choose_spawn_value(y_pool, "y_pool")
    if (
        not isinstance(x, int)
        or isinstance(x, bool)
        or not 0 <= x < GRID_SIZE
        or not isinstance(y, int)
        or isinstance(y, bool)
        or not 0 <= y < GRID_SIZE
    ):
        raise ValueError(f"TBall x_pool과 y_pool은 0부터 {GRID_SIZE - 1} 사이여야 합니다.")
    length = _choose_spawn_value(length_pool, "length_pool")
    if (
        not isinstance(length, int)
        or isinstance(length, bool)
        or not 1 <= length <= GRID_SIZE
    ):
        raise ValueError(f"TBall 길이는 1부터 {GRID_SIZE}칸 사이여야 합니다.")
    turns = _choose_spawn_value(turns_pool, "turns_pool")
    if not isinstance(turns, int) or isinstance(turns, bool) or turns < 1:
        raise ValueError("TBall 회전 수는 1 이상의 정수여야 합니다.")
    rotation_direction = _choose_spawn_value(rot_dir_pool, "rot_dir_pool")
    rotation_signs = {
        "+": 1,
        "-": -1,
        "CW": 1,
        "CCW": -1,
    }
    if not isinstance(rotation_direction, str):
        raise ValueError("TBall 회전 방향은 '+', '-', 'CW', 'CCW' 중 하나여야 합니다.")
    rotation_sign = rotation_signs.get(rotation_direction.upper())
    if rotation_sign is None:
        raise ValueError("TBall 회전 방향은 '+', '-', 'CW', 'CCW' 중 하나여야 합니다.")
    x, y = _get_grid_cell_center(y, x)
    angle = random.uniform(0.0, math.tau)
    orbit_length = CELL_SIZE * length
    speed = (length+3) * rotation_sign
    for _ in range(20):
        tball = TBall()
        tball.configure((x, y, angle), orbit_length, speed, turns)
        if _try_add_enemy(tball, allow_same_type_overlap):
            return

def spawn_vball(
    lane_pool: Tuple[int, ...],
    direction_pool: Tuple[str, ...],
    distance_pool: Tuple[int, ...]
) -> None:
    """진입 레인과 보드 안쪽 이동 거리를 지정해 VBall을 생성합니다."""
    lane = _choose_spawn_lane(lane_pool)
    direction = _choose_spawn_direction(direction_pool)
    row, col = get_spawn_coordinates(direction, lane)
    distance = _choose_spawn_value(distance_pool, "distance_pool")
    if (
        not isinstance(distance, int)
        or isinstance(distance, bool)
        or not 1 <= distance <= GRID_SIZE
    ):
        raise ValueError(f"VBall 이동 거리는 1부터 {GRID_SIZE}칸 사이여야 합니다.")
    position, travel = _get_spawn_edge_position(row, col, direction, 3)
    speed = (travel[0] * 10, travel[1] * 10)
    target_cell = distance - 1
    if direction in ("right", "bottom"):
        target_cell = GRID_SIZE - distance
    for _ in range(20):
        vball = VBall()
        vball.configure(
            position,
            SPAWN_FACE_BY_DIRECTION[direction],
            target_cell,
            speed
        )
        if _try_add_enemy(vball):
            return

def spawn_laser(
    lane_pool: Tuple[int, ...],
    direction_pool: Tuple[str, ...]
) -> None:
    """레인·방향 풀로 위치를 정해 안쪽으로 발사되는 레이저를 생성합니다."""
    lane = _choose_spawn_lane(lane_pool)
    direction = _choose_spawn_direction(direction_pool)
    row, col = get_spawn_coordinates(direction, lane)
    position, _ = _get_spawn_edge_position(row, col, direction, 3)
    for _ in range(20):
        laser = Laser()
        laser.configure(position, SPAWN_FACE_BY_DIRECTION[direction])
        if _try_add_enemy(laser):
            return


def spawn_log(
    lane_pool: Tuple[int, ...],
    direction_pool: Tuple[str, ...],
    length_pool: Tuple[int, ...]
) -> None:
    """레인·방향과 길이(칸)를 지정해 통나무를 생성합니다."""
    lane = _choose_spawn_lane(lane_pool)
    direction = _choose_spawn_direction(direction_pool)
    row, col = get_spawn_coordinates(direction, lane)
    length = _choose_spawn_value(length_pool, "length_pool")
    if (
        not isinstance(length, int)
        or isinstance(length, bool)
        or not 1 <= length <= GRID_SIZE
    ):
        raise ValueError(f"통나무 길이는 1부터 {GRID_SIZE}칸 사이여야 합니다.")
    board_left = display_size[0] // 2 - BOARD_HALF_SIZE
    board_right = display_size[0] // 2 + BOARD_HALF_SIZE
    board_top = display_size[1] // 2 - BOARD_HALF_SIZE
    board_bottom = display_size[1] // 2 + BOARD_HALF_SIZE
    lane_x, lane_y = _get_grid_cell_center(row, col)
    log_radius = Log.thickness // 2
    if direction == "top":
        position = (lane_x, board_top - 3 * CELL_SIZE - log_radius)
    elif direction == "right":
        position = (board_right + 3 * CELL_SIZE + log_radius, lane_y)
    elif direction == "bottom":
        position = (lane_x, board_bottom + 3 * CELL_SIZE + log_radius)
    else:
        position = (board_left - 3 * CELL_SIZE - log_radius, lane_y)

    for _ in range(20):
        log = Log()
        log.configure(position, SPAWN_FACE_BY_DIRECTION[direction], length)
        if _try_add_enemy(log):
            return


def spawn_bomb(
    x_pool: Tuple[int, ...],
    y_pool: Tuple[int, ...],
    chain_count_pool: Tuple[int, ...],
    pattern_pool: Tuple[str, ...]
) -> bool:
    """보드 좌표(x=열, y=행), 연쇄 범위, 패턴 풀에서 폭탄 속성을 뽑습니다."""
    x = _choose_spawn_value(x_pool, "x_pool")
    y = _choose_spawn_value(y_pool, "y_pool")
    chain_count = _choose_spawn_value(chain_count_pool, "chain_count_pool")
    pattern = _choose_spawn_value(pattern_pool, "pattern_pool")
    for coordinate, name in ((x, "x_pool"), (y, "y_pool")):
        if (
            not isinstance(coordinate, int)
            or isinstance(coordinate, bool)
            or not 0 <= coordinate < GRID_SIZE
        ):
            raise ValueError(f"{name}은(는) 0부터 {GRID_SIZE - 1} 사이여야 합니다.")
    return bomb_manager.spawn(
        y,
        x,
        chain_count=chain_count,
        pattern=pattern
    )


class SpawnState:
    """레벨별 스폰 함수가 공유하는 장애물 타이머 상태입니다."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.ball_delay = 0.0
        self.tball_delay = 0.0
        self.vball_delay = 0.0
        self.laser_delay = 0.0
        self.log_delay = 0.0
        self.bomb_delay = 0.0


SPAWN_DELAY_SCALE = 10


# 타이머 값은 기존과 같이 100/tps 단위로 감소합니다.
# 각 함수에서 해당 레벨의 장애물과 확률을 직접 수정할 수 있습니다.
def spawn_level_1(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = random.randint(10, 30) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(1, 4)):
            spawn_ball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS
            )
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = random.randint(40, 70) * SPAWN_DELAY_SCALE
        if random.random() < 1 / 3:
            spawn_tball(
                x_pool=DEFAULT_COORDINATES,
                y_pool=DEFAULT_COORDINATES,
                length_pool=DEFAULT_TBALL_LENGTHS,
                turns_pool=DEFAULT_TBALL_TURNS,
                rot_dir_pool=DEFAULT_TBALL_ROTATION_DIRECTIONS,
            )
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = random.randint(20, 30) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(1, 3)):
            spawn_vball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS,
                distance_pool=DEFAULT_VBALL_DISTANCES,
            )


def spawn_level_2(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = random.randint(30, 50) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(1, 4)):
            spawn_ball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS
            )
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = 20 * SPAWN_DELAY_SCALE
        for _ in range(3):
            spawn_vball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS,
                distance_pool=DEFAULT_VBALL_DISTANCES,
            )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = random.randint(100, 150) * SPAWN_DELAY_SCALE
        if random.random() < 1 / 5:
            state.laser_delay = 0
        for _ in range(random.randint(1, 3)):
            spawn_laser(
                lane_pool=DEFAULT_LANES,
                direction_pool=('left', 'right')
            )


def spawn_level_3(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = random.randint(20, 50) * SPAWN_DELAY_SCALE
        spawn_ball(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS
        )
        if random.random() < 1 / 3:
            state.ball_delay = 0
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = random.randint(50, 80) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(2, 3)):
            spawn_tball(
                x_pool=DEFAULT_COORDINATES,
                y_pool=DEFAULT_COORDINATES,
                length_pool=DEFAULT_TBALL_LENGTHS,
                turns_pool=DEFAULT_TBALL_TURNS,
                rot_dir_pool=DEFAULT_TBALL_ROTATION_DIRECTIONS,
            )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = 20 * SPAWN_DELAY_SCALE
        for _ in range(random.randint(3, 5)):
            spawn_laser(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS
            )


def spawn_level_4(state: SpawnState, dt: float) -> None:
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = 30 * SPAWN_DELAY_SCALE
        for _ in range(3):
            spawn_tball(
                x_pool=DEFAULT_COORDINATES,
                y_pool=DEFAULT_COORDINATES,
                length_pool=DEFAULT_TBALL_LENGTHS,
                turns_pool=DEFAULT_TBALL_TURNS,
                rot_dir_pool=DEFAULT_TBALL_ROTATION_DIRECTIONS,
            )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = random.randint(50, 100) * SPAWN_DELAY_SCALE
        spawn_log(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS,
            length_pool=DEFAULT_LOG_LENGTHS,
        )
        if random.random() < 1 / 4:
            state.log_delay = 100


def spawn_level_5(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = random.randint(20, 30) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(3, 6)):
            spawn_ball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS
            )
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = random.randint(10, 30) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(2, 4)):
            spawn_vball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS,
                distance_pool=DEFAULT_VBALL_DISTANCES,
            )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = random.randint(30, 60) * SPAWN_DELAY_SCALE
        for _ in range(2):
            spawn_laser(
                lane_pool=(1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7),
                direction_pool=DEFAULT_DIRECTIONS,
            )
        if random.random() < 1 / 5:
            spawn_laser(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS
            )


def spawn_level_6(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = 10 * SPAWN_DELAY_SCALE
        for _ in range(random.randint(1, 2)):
            spawn_ball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS
            )
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = random.randint(70, 100) * SPAWN_DELAY_SCALE
        spawn_tball(
            x_pool=DEFAULT_COORDINATES,
            y_pool=DEFAULT_COORDINATES,
            length_pool=DEFAULT_TBALL_LENGTHS,
            turns_pool=DEFAULT_TBALL_TURNS,
            rot_dir_pool=DEFAULT_TBALL_ROTATION_DIRECTIONS,
        )
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = random.randint(10, 20) * SPAWN_DELAY_SCALE
        spawn_vball(
            lane_pool=DEFAULT_LANES,
            direction_pool=('left', 'right'),
            distance_pool=DEFAULT_VBALL_DISTANCES,
        )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = random.randint(20, 30) * SPAWN_DELAY_SCALE
        spawn_laser(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS
        )


def spawn_level_7(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = 10 * SPAWN_DELAY_SCALE
        for _ in range(random.randint(0, 1)):
            spawn_ball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS
            )
        if random.random() < 1 / 4:
            state.ball_delay = 0
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = random.randint(20, 40) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(1, 2)):
            spawn_tball(
                x_pool=DEFAULT_COORDINATES,
                y_pool=DEFAULT_COORDINATES,
                length_pool=DEFAULT_TBALL_LENGTHS,
                turns_pool=DEFAULT_TBALL_TURNS,
                rot_dir_pool=DEFAULT_TBALL_ROTATION_DIRECTIONS,
            )
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = random.randint(10, 30) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(2, 3)):
            spawn_vball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS,
                distance_pool=DEFAULT_VBALL_DISTANCES,
            )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = random.randint(20, 30) * SPAWN_DELAY_SCALE
        if random.random() < 1 / 2:
            state.laser_delay = 100
        spawn_laser(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS
        )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = random.randint(30, 60) * SPAWN_DELAY_SCALE
        spawn_log(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS,
            length_pool=DEFAULT_LOG_LENGTHS,
        )
        if random.random() < 1 / 2:
            state.log_delay = 100


def spawn_level_8(state: SpawnState, dt: float) -> None:
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = random.randint(50, 80) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(3, 4)):
            spawn_tball(
                x_pool=DEFAULT_COORDINATES,
                y_pool=DEFAULT_COORDINATES,
                length_pool=DEFAULT_TBALL_LENGTHS,
                turns_pool=DEFAULT_TBALL_TURNS,
                rot_dir_pool=DEFAULT_TBALL_ROTATION_DIRECTIONS,
            )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = random.randint(20, 40) * SPAWN_DELAY_SCALE
        spawn_laser(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS
        )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = random.randint(50, 70) * SPAWN_DELAY_SCALE
        spawn_log(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS,
            length_pool=DEFAULT_LOG_LENGTHS,
        )
        if random.random() < 1 / 5:
            state.log_delay = 200
    state.bomb_delay -= dt
    if state.bomb_delay <= 0:
        state.bomb_delay = random.randint(50, 70) * SPAWN_DELAY_SCALE
        spawn_bomb(
            x_pool=DEFAULT_COORDINATES,
            y_pool=DEFAULT_COORDINATES,
            chain_count_pool=DEFAULT_BOMB_CHAIN_COUNTS,
            pattern_pool=DEFAULT_BOMB_PATTERNS,
        )


def spawn_level_9(state: SpawnState, dt: float) -> None:
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = random.randint(5, 10) * SPAWN_DELAY_SCALE
        spawn_vball(
            lane_pool=DEFAULT_LANES,
            direction_pool=('left',),
            distance_pool=(1, 2, 3, 4, 4, 5, 5, 6, 7, 7, 7),
        )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = random.randint(30, 50) * SPAWN_DELAY_SCALE
        spawn_laser(
            lane_pool=DEFAULT_LANES,
            direction_pool=('top', 'bottom')
        )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = random.randint(20, 50) * SPAWN_DELAY_SCALE
        spawn_log(
            lane_pool=DEFAULT_LANES,
            direction_pool=('top', 'bottom'),
            length_pool=DEFAULT_LOG_LENGTHS,
        )


def spawn_level_10(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = random.randint(10, 50) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(1, 4)):
            spawn_ball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS
            )
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = 50 * SPAWN_DELAY_SCALE
        spawn_tball(
            x_pool=DEFAULT_COORDINATES,
            y_pool=DEFAULT_COORDINATES,
            length_pool=DEFAULT_TBALL_LENGTHS,
            turns_pool=DEFAULT_TBALL_TURNS,
            rot_dir_pool=DEFAULT_TBALL_ROTATION_DIRECTIONS,
        )
    state.bomb_delay -= dt
    if state.bomb_delay <= 0:
        state.bomb_delay = random.randint(20, 40) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(1, 3)):
            spawn_bomb(
                x_pool=DEFAULT_COORDINATES,
                y_pool=DEFAULT_COORDINATES,
                chain_count_pool=DEFAULT_BOMB_CHAIN_COUNTS,
                pattern_pool=DEFAULT_BOMB_PATTERNS,
            )


def spawn_level_11(state: SpawnState, dt: float) -> None:
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = 20 * SPAWN_DELAY_SCALE
        if random.random() < 1 / 3:
            spawn_tball(
                x_pool=DEFAULT_COORDINATES,
                y_pool=DEFAULT_COORDINATES,
                length_pool=DEFAULT_TBALL_LENGTHS,
                turns_pool=DEFAULT_TBALL_TURNS,
                rot_dir_pool=DEFAULT_TBALL_ROTATION_DIRECTIONS,
            )
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = 10 * SPAWN_DELAY_SCALE
        for _ in range(random.randint(0, 2)):
            spawn_vball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS,
                distance_pool=DEFAULT_VBALL_DISTANCES,
            )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = random.randint(40, 60) * SPAWN_DELAY_SCALE
        spawn_log(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS,
            length_pool=DEFAULT_LOG_LENGTHS,
        )
        if random.random() < 1 / 5:
            state.log_delay = 200
    state.bomb_delay -= dt
    if state.bomb_delay <= 0:
        state.bomb_delay = 40 * SPAWN_DELAY_SCALE
        spawn_bomb(
            x_pool=DEFAULT_COORDINATES,
            y_pool=DEFAULT_COORDINATES,
            chain_count_pool=DEFAULT_BOMB_CHAIN_COUNTS,
            pattern_pool=DEFAULT_BOMB_PATTERNS,
        )


def spawn_level_12(state: SpawnState, dt: float) -> None:
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = SPAWN_DELAY_SCALE
        if random.random() < 1 / 7:
            spawn_laser(
                lane_pool=(1, 1, 1, 2, 3, 4, 5, 6, 7, 7, 7),
                direction_pool=DEFAULT_DIRECTIONS
            )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = random.randint(30, 50) * SPAWN_DELAY_SCALE
        if random.random() < 1 / 7:
            state.log_delay = SPAWN_DELAY_SCALE
        if random.random() < 1 / 3:
            spawn_log(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS,
                length_pool=DEFAULT_LOG_LENGTHS,
            )
    state.bomb_delay -= dt
    if state.bomb_delay <= 0:
        state.bomb_delay = SPAWN_DELAY_SCALE
        if random.random() < 1 / 7:
            spawn_bomb(
                x_pool=DEFAULT_COORDINATES,
                y_pool=DEFAULT_COORDINATES,
                chain_count_pool=DEFAULT_BOMB_CHAIN_COUNTS,
                pattern_pool=('+',),
            )


def spawn_level_13(state: SpawnState, dt: float) -> None:
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = random.randint(10, 50) * SPAWN_DELAY_SCALE
        spawn_tball(
            x_pool=DEFAULT_COORDINATES,
            y_pool=DEFAULT_COORDINATES,
            length_pool=DEFAULT_TBALL_LENGTHS,
            turns_pool=DEFAULT_TBALL_TURNS,
            rot_dir_pool=DEFAULT_TBALL_ROTATION_DIRECTIONS,
        )
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = random.randint(10, 20) * SPAWN_DELAY_SCALE
        spawn_vball(
            lane_pool=DEFAULT_LANES,
            direction_pool=('bottom',),
            distance_pool=DEFAULT_VBALL_DISTANCES,
        )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = random.randint(20, 50) * SPAWN_DELAY_SCALE
        spawn_log(
            lane_pool=(4, 5, 6),
            direction_pool=('left',),
            length_pool=(3, 5)
        )
    state.bomb_delay -= dt
    if state.bomb_delay <= 0:
        state.bomb_delay = 100 * SPAWN_DELAY_SCALE
        spawn_bomb(
            x_pool=DEFAULT_COORDINATES,
            y_pool=DEFAULT_COORDINATES,
            chain_count_pool=DEFAULT_BOMB_CHAIN_COUNTS,
            pattern_pool=DEFAULT_BOMB_PATTERNS,
        )


def spawn_level_14(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = SPAWN_DELAY_SCALE
        if random.random() < 1 / 2:
            spawn_ball(
                lane_pool=(1, 1, 2, 3, 4, 5, 6, 7, 7),
                direction_pool=DEFAULT_DIRECTIONS
            )


def spawn_level_15(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = random.randint(1, 5) * SPAWN_DELAY_SCALE
        spawn_ball(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS
        )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = random.randint(20, 50) * SPAWN_DELAY_SCALE
        spawn_log(
            lane_pool=(2, 6),
            direction_pool=DEFAULT_DIRECTIONS,
            length_pool=(3,),
        )


def spawn_level_16(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = random.randint(1, 5) * SPAWN_DELAY_SCALE
        spawn_ball(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS
        )
    state.bomb_delay -= dt
    if state.bomb_delay <= 0:
        state.bomb_delay = random.randint(10, 30) * SPAWN_DELAY_SCALE
        spawn_bomb(
            x_pool=DEFAULT_COORDINATES,
            y_pool=DEFAULT_COORDINATES,
            chain_count_pool=(0,),
            pattern_pool=DEFAULT_BOMB_PATTERNS,
        )


def spawn_level_17(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = random.randint(10, 30) * SPAWN_DELAY_SCALE
        spawn_ball(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS
        )
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = random.randint(10, 30) * SPAWN_DELAY_SCALE
        spawn_vball(
            lane_pool=(1, 2, 3, 5, 6, 7),
            direction_pool=DEFAULT_DIRECTIONS,
            distance_pool=(1, 2, 3),
        )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = 3 * SPAWN_DELAY_SCALE
        spawn_laser(
            lane_pool=(4,),
            direction_pool=('top', 'bottom')
            )
        spawn_laser(
            lane_pool=(4,),
            direction_pool=('left', 'right')
        )
    state.bomb_delay -= dt
    if state.bomb_delay <= 0:
        state.bomb_delay = 40 * SPAWN_DELAY_SCALE
        spawn_bomb(
            x_pool=DEFAULT_COORDINATES,
            y_pool=DEFAULT_COORDINATES,
            chain_count_pool=DEFAULT_BOMB_CHAIN_COUNTS,
            pattern_pool=DEFAULT_BOMB_PATTERNS,
        )


def spawn_level_18(state: SpawnState, dt: float) -> None:
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = 2 * SPAWN_DELAY_SCALE
        spawn_laser(
            lane_pool=(3, 4, 4, 4, 5),
            direction_pool=DEFAULT_DIRECTIONS
        )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = random.randint(100, 150) * SPAWN_DELAY_SCALE
        spawn_log(
            lane_pool=(2, 6),
            direction_pool=DEFAULT_DIRECTIONS,
            length_pool=(3,),
        )
    state.bomb_delay -= dt
    if state.bomb_delay <= 0:
        state.bomb_delay = 20 * SPAWN_DELAY_SCALE
        spawn_bomb(
            x_pool=DEFAULT_COORDINATES,
            y_pool=DEFAULT_COORDINATES,
            chain_count_pool=DEFAULT_BOMB_CHAIN_COUNTS,
            pattern_pool=DEFAULT_BOMB_PATTERNS,
        )


def spawn_level_19(state: SpawnState, dt: float) -> None:
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = 4 * SPAWN_DELAY_SCALE
        spawn_tball(
            x_pool=(3,),
            y_pool=(3,),
            length_pool=(1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 6, 7),
            turns_pool=(1,),
            rot_dir_pool=DEFAULT_TBALL_ROTATION_DIRECTIONS,
        )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = 30 * SPAWN_DELAY_SCALE
        spawn_log(
            lane_pool=(4,),
            direction_pool=DEFAULT_DIRECTIONS,
            length_pool=(3,),
        )


def spawn_level_20(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = 10 * SPAWN_DELAY_SCALE
        spawn_ball(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS
        )
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = random.randint(10, 20) * SPAWN_DELAY_SCALE
        spawn_vball(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS,
            distance_pool=DEFAULT_VBALL_DISTANCES,
        )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = 10 * SPAWN_DELAY_SCALE
        spawn_laser(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS
        )
    state.bomb_delay -= dt
    if state.bomb_delay <= 0:
        state.bomb_delay = random.randint(10, 30) * SPAWN_DELAY_SCALE
        for _ in range(random.randint(1, 3)):
            spawn_bomb(
                x_pool=DEFAULT_COORDINATES,
                y_pool=DEFAULT_COORDINATES,
                chain_count_pool=DEFAULT_BOMB_CHAIN_COUNTS,
                pattern_pool=DEFAULT_BOMB_PATTERNS,
            )


def spawn_level_21(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = random.randint(10, 20) * SPAWN_DELAY_SCALE
        spawn_ball(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS
        )
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = 50 * SPAWN_DELAY_SCALE
        spawn_tball(
            x_pool=(0,), y_pool=(0,),
            length_pool=(2,),
            turns_pool=(3,), rot_dir_pool=('+',), allow_same_type_overlap=True
        )
        spawn_tball(
            x_pool=(0,), y_pool=(6,),
            length_pool=(4,),
            turns_pool=(3,), rot_dir_pool=('-',), allow_same_type_overlap=True
        )
        spawn_tball(
            x_pool=(6,), y_pool=(6,),
            length_pool=(2,),
            turns_pool=(3,), rot_dir_pool=('+',), allow_same_type_overlap=True
        )
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = random.randint(10, 20) * SPAWN_DELAY_SCALE
        spawn_vball(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS,
            distance_pool=DEFAULT_VBALL_DISTANCES,
        )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = random.randint(20, 30) * SPAWN_DELAY_SCALE
        spawn_laser(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS
        )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = random.randint(30, 50) * SPAWN_DELAY_SCALE
        spawn_log(
            lane_pool=DEFAULT_LANES,
            direction_pool=('right',),
            length_pool=DEFAULT_LOG_LENGTHS
        )


def spawn_level_22(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = 7 * SPAWN_DELAY_SCALE
        for _ in range(random.randint(1, 3)):
            spawn_ball(
                lane_pool=(1, 2, 3, 5, 6, 7),
                direction_pool=('left',)
            )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = 5 * SPAWN_DELAY_SCALE
        spawn_laser(
            lane_pool=(4,),
            direction_pool=('right',)
        )
    state.bomb_delay -= dt
    if state.bomb_delay <= 0:
        state.bomb_delay = random.randint(20, 30) * SPAWN_DELAY_SCALE
        spawn_bomb(
            x_pool=DEFAULT_COORDINATES,
            y_pool=DEFAULT_COORDINATES,
            chain_count_pool=DEFAULT_BOMB_CHAIN_COUNTS,
            pattern_pool=DEFAULT_BOMB_PATTERNS,
        )


def spawn_level_23(state: SpawnState, dt: float) -> None:
    state.ball_delay -= dt
    if state.ball_delay <= 0:
        state.ball_delay = 10 * SPAWN_DELAY_SCALE
        for _ in range(random.randint(0, 2)):
            spawn_ball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS
            )
    state.tball_delay -= dt
    if state.tball_delay <= 0:
        state.tball_delay = 20 * SPAWN_DELAY_SCALE
        if random.random() < 1 / 2:
            spawn_tball(
                x_pool=DEFAULT_COORDINATES,
                y_pool=DEFAULT_COORDINATES,
                length_pool=DEFAULT_TBALL_LENGTHS,
                turns_pool=DEFAULT_TBALL_TURNS,
                rot_dir_pool=DEFAULT_TBALL_ROTATION_DIRECTIONS,
            )
    state.vball_delay -= dt
    if state.vball_delay <= 0:
        state.vball_delay = 10 * SPAWN_DELAY_SCALE
        if random.random() < 1 / 2:
            spawn_vball(
                lane_pool=DEFAULT_LANES,
                direction_pool=DEFAULT_DIRECTIONS,
                distance_pool=DEFAULT_VBALL_DISTANCES,
            )
    state.laser_delay -= dt
    if state.laser_delay <= 0:
        state.laser_delay = 10 * SPAWN_DELAY_SCALE
        spawn_laser(
            lane_pool=(1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7),
            direction_pool=DEFAULT_DIRECTIONS
        )
    state.log_delay -= dt
    if state.log_delay <= 0:
        state.log_delay = random.randint(20, 50) * SPAWN_DELAY_SCALE
        spawn_log(
            lane_pool=DEFAULT_LANES,
            direction_pool=DEFAULT_DIRECTIONS,
            length_pool=DEFAULT_LOG_LENGTHS,
        )
    state.bomb_delay -= dt
    if state.bomb_delay <= 0:
        state.bomb_delay = random.randint(5, 30) * SPAWN_DELAY_SCALE
        spawn_bomb(
            x_pool=DEFAULT_COORDINATES,
            y_pool=DEFAULT_COORDINATES,
            chain_count_pool=DEFAULT_BOMB_CHAIN_COUNTS,
            pattern_pool=DEFAULT_BOMB_PATTERNS,
        )


SPAWN_FUNCTIONS_BY_LEVEL: Tuple[
    Callable[[SpawnState, float], None], ...
] = (
    spawn_level_1,
    spawn_level_2,
    spawn_level_3,
    spawn_level_4,
    spawn_level_5,
    spawn_level_6,
    spawn_level_7,
    spawn_level_8,
    spawn_level_9,
    spawn_level_10,
    spawn_level_11,
    spawn_level_12,
    spawn_level_13,
    spawn_level_14,
    spawn_level_15,
    spawn_level_16,
    spawn_level_17,
    spawn_level_18,
    spawn_level_19,
    spawn_level_20,
    spawn_level_21,
    spawn_level_22,
    spawn_level_23
)


def spawn_enemies_by_level(state: SpawnState, dt: float) -> None:
    """현재 스테이지의 개별 스폰 함수를 호출합니다."""
    if 1 <= game_level <= len(SPAWN_FUNCTIONS_BY_LEVEL):
        SPAWN_FUNCTIONS_BY_LEVEL[game_level - 1](state, dt)


def is_collision(
    pos1: Tuple[Tuple[int, int], Tuple[int, int]],
    pos2: Tuple[Tuple[int, int], Tuple[int, int]]
    ) -> bool:
    for pos in pos1:
        if pos2[0][0] <= pos[0] <= pos2[1][0] and pos2[0][1] <= pos[1] <= pos2[1][1]:
            return True
    return False




# 보드, 플레이어, 적에게 공통으로 사용하는 색상 팔레트입니다.
WHITE = (255, 255, 255)
LIGHT_GRAY = (192, 192, 192)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BLACK = (0, 0, 0)
RED = (255, 10, 10)
ORANGE = (255, 150, 10)
YELLOW = (255, 255, 10)
LIME = (128, 255, 128)
GREEN = (10, 255, 10)
SKY = (0, 200, 255)
BLUE = (10, 10, 255)
PURPLE = (128, 0, 255)
PINK = (255, 0, 255)
BROWN = (70, 40, 20)
FLESH = (255, 190, 150)

PLAYER_COLOR_MAP = {
    "red": RED,
    "orange": ORANGE,
    "yellow": YELLOW,
    "lime": LIME,
    "green": GREEN,
    "sky": SKY,
    "blue": BLUE,
    "purple": PURPLE,
    "pink": PINK,
    "brown": BROWN,
    "flesh": FLESH
}
PLAYER_COLOR_OPTIONS = tuple(PLAYER_COLOR_MAP)
HIT_EFFECT_OPTIONS = ("None", "Particles", "Explosion")
PLAYER_CUSTOMIZATION = {
    "color": "lime",
    "hit_effect": "Explosion"
}



def _get_ball_sprite(style: str, show_hitbox: bool) -> Surface:
    """반복되는 공 그림을 종류별·충돌 상자 표시별로 한 번만 만듭니다."""
    key = (style, show_hitbox)
    if key not in _ball_sprite_cache:
        sprite_size = round(100 * ELEMENT_SCALE)
        surface = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        colors = {
            "white": WHITE,
            "blue": (100, 100, 255),
            "pink": (255, 150, 200)
        }
        color = colors[style]
        for radius in range(10):
            pygame.draw.circle(
                surface,
                (color[0], color[1], color[2], radius / 9 * 255),
                (sprite_size // 2, sprite_size // 2),
                round(33 * ELEMENT_SCALE) - round(radius * ELEMENT_SCALE)
            )
        if show_hitbox:
            inset = round(30 * ELEMENT_SCALE)
            far_edge = sprite_size - inset
            pygame.draw.lines(
                surface,
                RED,
                True,
                ((inset, inset), (far_edge, inset), (far_edge, far_edge), (inset, far_edge)),
                1
            )
        _ball_sprite_cache[key] = surface
    return _ball_sprite_cache[key]


def _get_tball_ring(radius: int) -> Surface:
    """화면 전체 크기 대신 궤도 원에 꼭 맞는 캐시 표면을 반환합니다."""
    if radius not in _tball_ring_cache:
        diameter = radius * 2 + 6
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(
            surface,
            (82, 82, 255, 150),
            (diameter // 2, diameter // 2),
            radius,
            3
        )
        _tball_ring_cache[radius] = surface
    return _tball_ring_cache[radius]


def _get_laser_device(face: int, show_hitbox: bool) -> Surface:
    """레이저 장치의 고정 그림과 방향 회전을 재사용합니다."""
    key = (face, show_hitbox)
    if key not in _laser_device_cache:
        sprite_size = round(100 * ELEMENT_SCALE)
        surface = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        center = sprite_size // 2
        for radius in range(10):
            color = (230, 255, 200, round(radius / 9 * 255))
            pygame.draw.circle(
                surface,
                color,
                (center, center),
                round((40 - radius) * ELEMENT_SCALE),
                max(1, round((35 - radius * 2) * ELEMENT_SCALE))
            )
            inset = round((20 + radius) * ELEMENT_SCALE)
            pygame.draw.rect(
                surface,
                color,
                (
                    inset,
                    round((65 + radius) * ELEMENT_SCALE),
                    round((60 - radius * 2) * ELEMENT_SCALE),
                    round((30 - radius * 2) * ELEMENT_SCALE)
                )
            )
        if show_hitbox:
            inset = round(30 * ELEMENT_SCALE)
            far_edge = sprite_size - inset
            pygame.draw.lines(
                surface,
                BLACK,
                True,
                ((inset, inset), (far_edge, inset), (far_edge, far_edge), (inset, far_edge)),
                1
            )
        _laser_device_cache[key] = pygame.transform.rotate(surface, -90 * face)
    return _laser_device_cache[key]


def _get_log_sprite(length_cells: int, roll_frame: int, vertical: bool) -> Surface:
    """통나무의 정적인 프레임과 방향 회전을 캐시해 매 프레임 다시 그리지 않습니다."""
    key = (length_cells, roll_frame, vertical)
    if key not in _log_sprite_cache:
        length = length_cells * CELL_SIZE - LOG_END_INSET
        thickness = Log.thickness
        surface = pygame.Surface((length, thickness), pygame.SRCALPHA)
        edge = round(8 * ELEMENT_SCALE)
        pygame.draw.rect(surface, (125, 76, 42), (0, edge, length, thickness - edge * 2))
        pygame.draw.line(
            surface,
            (153, 98, 55),
            (0, round(14 * ELEMENT_SCALE)),
            (length, round(14 * ELEMENT_SCALE)),
            max(1, round(4 * ELEMENT_SCALE))
        )
        pygame.draw.line(
            surface,
            (78, 45, 27),
            (0, thickness - round(14 * ELEMENT_SCALE)),
            (length, thickness - round(14 * ELEMENT_SCALE)),
            max(1, round(5 * ELEMENT_SCALE))
        )

        stripe_spacing = round(64 * ELEMENT_SCALE)
        stripe_offset = roll_frame * stripe_spacing // 16
        for stripe_x in range(stripe_offset, length, stripe_spacing):
            stripe_edge = round(11 * ELEMENT_SCALE)
            pygame.draw.rect(
                surface,
                (82, 48, 29),
                (
                    stripe_x,
                    stripe_edge,
                    max(1, round(8 * ELEMENT_SCALE)),
                    thickness - stripe_edge * 2
                )
            )

        if vertical:
            surface = pygame.transform.rotate(surface, 90)
        _log_sprite_cache[key] = surface
    return _log_sprite_cache[key]


def _get_laser_beam(stage: int, delay: int, face: int) -> Surface:
    """레이저의 단계별 빔 이미지를 제한된 캐시에 저장합니다."""
    progress = 20 - delay // 3 if stage == 1 else max(20 - delay, 0)
    progress = max(0, min(20, progress))
    return _build_laser_beam(stage, progress, face)


@lru_cache(maxsize=64)
def _build_laser_beam(stage: int, progress: int, face: int) -> Surface:
    """레이저 빔을 한 번만 그려 제한된 캐시에 보관합니다."""
    beam_width = round(100 * ELEMENT_SCALE)
    beam_origin = round(120 * ELEMENT_SCALE)
    surface = pygame.Surface((beam_width, LASER_LENGTH), pygame.SRCALPHA)
    first_radius = 20 - progress if stage == 1 else progress
    for radius in range(first_radius, 20):
        scaled_radius = round(radius * ELEMENT_SCALE)
        if stage == 2:
            pygame.draw.rect(
                surface,
                (255, 50, 50, round(radius / 19 * 255)),
                (
                    round(28 * ELEMENT_SCALE) + scaled_radius,
                    beam_origin,
                    max(1, round((44 - radius * 2) * ELEMENT_SCALE)),
                    LASER_LENGTH - beam_origin
                )
            )
        pygame.draw.circle(
            surface,
            (255, 50, 50, round(radius / 19 * 255)),
            (beam_width // 2, beam_origin),
            max(1, round((22 - radius) * ELEMENT_SCALE))
        )
    return pygame.transform.rotate(surface, -90 * face)


ENEMY_HIT_INDEX = {
    Ball: 0,
    TBall: 1,
    VBall: 2,
    Laser: 3,
    Log: 4
}


def _get_enemy_spawn_rect(enemy) -> pygame.Rect:
    """장애물의 최초 위치를 비교할 충돌 영역을 반환합니다."""
    if isinstance(enemy, Log):
        return enemy.hitbox.copy()
    if isinstance(enemy, Laser):
        device_size = round(64 * ELEMENT_SCALE)
        return pygame.Rect(0, 0, device_size, device_size).move(
            enemy.pos[0] - device_size // 2,
            enemy.pos[1] - device_size // 2
        )

    spawn_rect = enemy.hitbox.copy()
    spawn_rect.center = (round(enemy.pos[0]), round(enemy.pos[1]))
    return spawn_rect


def _try_add_enemy(enemy, allow_same_type_overlap: bool = False) -> bool:
    """겹치는 장애물이 없을 때만 생성 목록에 추가합니다."""
    candidate_rect = _get_enemy_spawn_rect(enemy)
    for existing_enemy in enemies:
        if existing_enemy.is_deleted():
            continue
        if allow_same_type_overlap and type(existing_enemy) is type(enemy):
            continue
        if candidate_rect.colliderect(_get_enemy_spawn_rect(existing_enemy)):
            return False
    enemies.append(enemy)
    return True


def award_score_for_ticks(
    current_score: int,
    tick_accumulator: float,
    hp: int,
    delta_time: float,
    ticks_per_second: int
) -> Tuple[int, float]:
    """경과한 게임 틱마다 남은 HP만큼 점수를 더합니다."""
    tick_accumulator += max(0.0, delta_time) * ticks_per_second
    while tick_accumulator >= 1.0:
        current_score += max(0, hp)
        tick_accumulator -= 1.0
    return current_score, tick_accumulator


CLEAR_RANKS = ("Perfect", "Great", "Good", "Passed")


def get_clear_rank(hp: int, clear_score: float) -> str:
    """클리어 점수와 남은 체력으로 이번 클리어 등급을 계산합니다."""
    if clear_score < 100 or hp <= 0:
        return "Not cleared"
    if hp >= 3:
        return "Perfect"
    if hp == 2:
        return "Great"
    return "Good"


def save_game_data() -> bool:
    """진행률, 점수, 시도 횟수와 클리어 통계를 JSON에 저장합니다."""
    global save_dirty, last_save_time
    data = {
        "version": GAME_DATA_VERSION,
        "game_level": game_level,
        "track_ids": TRACK_IDS,
        "score_record": score_record,
        "level_stats": level_stats,
        "player_customization": PLAYER_CUSTOMIZATION
    }
    temp_path = f"{SAVE_FILE_PATH}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as save_file:
            json.dump(data, save_file, indent=4, ensure_ascii=False)
        os.replace(temp_path, SAVE_FILE_PATH)
    except (OSError, TypeError, ValueError) as error:
        print(f"게임 저장 중 오류가 발생했습니다: {error}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError as cleanup_error:
                print(f"임시 저장 파일을 정리하지 못했습니다: {cleanup_error}")
        return False
    save_dirty = False
    last_save_time = pygame.time.get_ticks() if pygame.get_init() else 0
    print("게임 기록을 저장했습니다.")
    return True


def load_game_data() -> None:
    """저장 파일에서 이전 최고 기록과 신규 클리어 통계를 검증해 불러옵니다."""
    global game_level, score_record, level_stats
    if not os.path.exists(SAVE_FILE_PATH):
        return

    try:
        with open(SAVE_FILE_PATH, "r", encoding="utf-8") as save_file:
            data = json.load(save_file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"게임 저장 파일을 불러오지 못했습니다: {error}")
        return

    if not isinstance(data, dict):
        print("게임 저장 파일 형식이 올바르지 않습니다. 새 기록으로 시작합니다.")
        return

    customization = data.get("player_customization")
    if isinstance(customization, dict):
        color_name = customization.get("color")
        hit_effect = customization.get("hit_effect")
        if isinstance(color_name, str) and color_name in PLAYER_COLOR_MAP:
            PLAYER_CUSTOMIZATION["color"] = color_name
        if isinstance(hit_effect, str) and hit_effect in HIT_EFFECT_OPTIONS:
            PLAYER_CUSTOMIZATION["hit_effect"] = hit_effect

    loaded_track_ids = data.get("track_ids")
    if loaded_track_ids is None:
        source_track_ids = LEGACY_TRACK_IDS
    elif (
        isinstance(loaded_track_ids, list)
        and all(isinstance(track_id, str) for track_id in loaded_track_ids)
    ):
        source_track_ids = tuple(loaded_track_ids)
    else:
        print("저장된 곡 목록 형식이 올바르지 않아 기록을 불러오지 않습니다.")
        return
    current_track_indices = {
        track_id: index for index, track_id in enumerate(TRACK_IDS)
    }

    loaded_level = data.get("game_level", 1)
    if isinstance(loaded_level, int) and not isinstance(loaded_level, bool):
        source_level_index = loaded_level - 1
        if 0 <= source_level_index < len(source_track_ids):
            track_id = source_track_ids[source_level_index]
            if track_id in current_track_indices:
                game_level = current_track_indices[track_id] + 1
            else:
                print(f"저장된 현재 스테이지 곡을 찾을 수 없습니다: {track_id}")

    loaded_records = data.get("score_record", [])
    if isinstance(loaded_records, list):
        for source_index, record in enumerate(loaded_records[:len(source_track_ids)]):
            if source_track_ids[source_index] not in current_track_indices:
                continue
            index = current_track_indices[source_track_ids[source_index]]
            if isinstance(record, int) and not isinstance(record, bool):
                score_record[index] = max(0, min(100, record))
            elif isinstance(record, float) and math.isfinite(record):
                score_record[index] = max(0, min(100, record))

    loaded_stats = data.get("level_stats", [])
    if isinstance(loaded_stats, list):
        for source_index, stats in enumerate(loaded_stats[:len(source_track_ids)]):
            if source_track_ids[source_index] not in current_track_indices:
                continue
            index = current_track_indices[source_track_ids[source_index]]
            if not isinstance(stats, dict):
                continue
            clear_count = stats.get("clear_count", 0)
            if isinstance(clear_count, int) and not isinstance(clear_count, bool):
                level_stats[index]["clear_count"] = max(0, clear_count)
            for key in ("best_progress", "best_score", "last_score", "total_attempts"):
                value = stats.get(key, 0)
                if key == "total_attempts":
                    if isinstance(value, int) and not isinstance(value, bool):
                        level_stats[index][key] = max(0, value)
                elif key in ("best_score", "last_score"):
                    if isinstance(value, int) and not isinstance(value, bool):
                        level_stats[index][key] = max(0, value)
                elif (
                    isinstance(value, (int, float))
                    and not isinstance(value, bool)
                    and math.isfinite(value)
                ):
                    level_stats[index][key] = max(0, min(100, value))
            level_stats[index]["best_progress"] = max(
                level_stats[index]["best_progress"],
                score_record[index]
            )
            level_stats[index]["cleared"] = (
                level_stats[index]["clear_count"] > 0
                or stats.get("cleared") is True
            )
            rank = stats.get("best_clear_rank", "Not cleared")
            if rank in CLEAR_RANKS:
                level_stats[index]["best_clear_rank"] = rank
            elif level_stats[index]["cleared"]:
                level_stats[index]["best_clear_rank"] = "Passed"
    for index in range(MAX_LEVEL):
        level_stats[index]["best_progress"] = max(
            level_stats[index]["best_progress"],
            score_record[index]
        )


score_record = [0] * MAX_LEVEL
level_stats = [
    {
        "cleared": False,
        "clear_count": 0,
        "best_clear_rank": "Not cleared",
        "best_progress": 0.0,
        "best_score": 0,
        "last_score": 0,
        "total_attempts": 0
    }
    for _ in range(MAX_LEVEL)
]
game_level = 1
save_dirty = False
last_save_time = 0
load_game_data()


# 게임이 끝나거나 재시작될 때까지 레벨별 상태를 초기화합니다.
session_attempt_count = 0
session_best_score = 0
session_best_progress = 0.0
attempt_best_progress = 0.0
score_tick_accumulator = 0.0
record_flash_remaining = 0.0
session_record_flash_triggered = False
attempt_record_baseline = 0.0
show_home = True
game_state = STATE_HOME
clock = pygame.time.Clock()
tps = 60
player = None
enemies = []
bomb_manager = BombManager()
spawn_state = SpawnState()
pause = False
hit_count = [0, 0, 0, 0, 0]
hit_stack = False
music_endevent = pygame.USEREVENT + 1
should_restart = True
_shutdown_save_completed = False


def _save_game_data_on_exit() -> None:
    """정상 종료와 예외 종료에서 마지막 게임 상태를 보존합니다."""
    global _shutdown_save_completed
    if not _shutdown_save_completed:
        _shutdown_save_completed = save_game_data()


atexit.register(_save_game_data_on_exit)


while should_restart:
    if show_home:
        game_state = STATE_HOME
        player = None
        pause = False
        hitbox = False
        score = 0
        game_level = max(1, min(MAX_LEVEL, game_level))
        selected_level = game_level - 1
        preview_level = selected_level
        preview_track_duration_seconds = get_track_duration_seconds(preview_level)
        enemies = []
        bomb_manager.reset_for_level()
        spawn_state.reset()
        hit_count = [0, 0, 0, 0, 0]
        hit_stack = False
        preview_spectrum = [0.0] * SPECTRUM_BAND_COUNT
        preview_spectrum_peaks = [
            SPECTRUM_AGC_INITIAL_PEAK
        ] * SPECTRUM_BAND_COUNT
        customization_spectrum = [0.0] * SPECTRUM_BAND_COUNT
        customization_spectrum_peaks = [
            SPECTRUM_AGC_INITIAL_PEAK
        ] * SPECTRUM_BAND_COUNT
        customization_visualizer_time = 0.0
        preview_onset = 0.0
        locked_preview_balls = []
        locked_preview_timer = 0.0
        locked_preview_index = 0
        transition_duration = 0.48
        transition_elapsed = transition_duration
        transition_switched = True
        menu_running = True
        start_game = False
        customization_active = False
        customization_move_mode = False
        customization_item = 0
        customization_transition = 0.0
        customization_test_ball = None
        pygame.mixer.music.set_endevent()
        pygame.mixer.music.stop()
        preview_was_locked = is_level_locked(preview_level)
        if not preview_was_locked:
            pygame.mixer.music.load(MUSIC_TRACKS[preview_level])
            pygame.mixer.music.play()

        while menu_running:
            delta_time = min(clock.tick(tps) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                    should_restart = False
                elif event.type == pygame.KEYDOWN:
                    if customization_active:
                        if event.key == pygame.K_p:
                            customization_active = False
                            customization_move_mode = False
                            player = None
                            enemies.clear()
                            preview_was_locked = is_level_locked(preview_level)
                            if not preview_was_locked:
                                pygame.mixer.music.load(MUSIC_TRACKS[preview_level])
                                pygame.mixer.music.play(fade_ms=120)
                        elif event.key == pygame.K_ESCAPE:
                            customization_move_mode = not customization_move_mode
                        elif customization_move_mode and event.key in (
                            pygame.K_UP,
                            pygame.K_DOWN,
                            pygame.K_LEFT,
                            pygame.K_RIGHT
                        ):
                            player_move(player, pygame.key.get_pressed())
                        elif not customization_move_mode and event.key in (
                            pygame.K_UP,
                            pygame.K_DOWN
                        ):
                            customization_item = 1 - customization_item
                        elif not customization_move_mode and event.key in (
                            pygame.K_LEFT,
                            pygame.K_RIGHT
                        ):
                            step = -1 if event.key == pygame.K_LEFT else 1
                            if customization_item == 0:
                                options = PLAYER_COLOR_OPTIONS
                                current = options.index(PLAYER_CUSTOMIZATION["color"])
                                PLAYER_CUSTOMIZATION["color"] = options[
                                    (current + step) % len(options)
                                ]
                                player.color = PLAYER_COLOR_MAP[
                                    PLAYER_CUSTOMIZATION["color"]
                                ]
                            else:
                                options = HIT_EFFECT_OPTIONS
                                current = options.index(
                                    PLAYER_CUSTOMIZATION["hit_effect"]
                                )
                                PLAYER_CUSTOMIZATION["hit_effect"] = options[
                                    (current + step) % len(options)
                                ]
                            save_dirty = True
                            save_game_data()
                    elif event.key == pygame.K_p:
                        customization_active = True
                        customization_move_mode = False
                        customization_item = 0
                        customization_transition = 0.0
                        customization_spectrum = [0.0] * SPECTRUM_BAND_COUNT
                        customization_spectrum_peaks = [
                            SPECTRUM_AGC_INITIAL_PEAK
                        ] * SPECTRUM_BAND_COUNT
                        customization_visualizer_time = 0.0
                        pygame.mixer.music.stop()
                        enemies.clear()
                        bomb_manager.reset_for_level()
                        player = Player(training_mode=True)
                        test_center = (
                            display_size[0] // 2,
                            display_size[1] // 2
                        )
                        customization_test_ball = TBall()
                        customization_test_ball.configure(
                            (test_center[0], test_center[1], 0),
                            CELL_SIZE,
                            speed=4,
                            turn=1,
                            loop=True
                        )
                        customization_test_ball.stage = 1
                        enemies.append(customization_test_ball)
                    # 테스트 시 F6으로 선택된 보스의 잠금 상태를 임시 전환합니다.
                    elif event.key == pygame.K_F6:
                        debug_level_index = (
                            selected_level
                            if selected_level in BOSS_LEVEL_INDICES
                            else BOSS_LEVEL_INDICES[0]
                        )
                        debug_boss_unlock_overrides[debug_level_index] = (
                            not is_boss_level_unlocked(debug_level_index)
                        )
                    elif event.key == pygame.K_UP:
                        if selected_level > 0:
                            selected_level -= 1
                            transition_elapsed = 0.0
                            transition_switched = False
                    elif event.key == pygame.K_DOWN:
                        if selected_level < MAX_LEVEL - 1:
                            selected_level += 1
                            transition_elapsed = 0.0
                            transition_switched = False
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if (
                            transition_elapsed >= transition_duration
                            and not is_level_locked(selected_level)
                        ):
                            game_level = selected_level + 1
                            session_attempt_count = 0
                            session_best_score = 0
                            session_best_progress = 0.0
                            attempt_best_progress = 0.0
                            session_record_flash_triggered = False
                            record_flash_remaining = 0.0
                            save_dirty = True
                            save_game_data()
                            start_game = True
                            menu_running = False

            if not should_restart:
                break

            if customization_active:
                customization_target = (
                    1.0 if customization_move_mode else 0.0
                )
                customization_transition += (
                    customization_target - customization_transition
                ) * (1.0 - math.exp(-12.0 * delta_time))
                customization_visualizer_time += delta_time
                customization_targets = tuple(
                    90.0
                    + 55.0 * (
                        math.sin(customization_visualizer_time * 2.7 + band * 0.52)
                        + 1.0
                    )
                    + 30.0 * (
                        math.sin(customization_visualizer_time * 1.35 - band * 0.19)
                        + 1.0
                    )
                    for band in range(SPECTRUM_BAND_COUNT)
                )
                update_spectrum_levels(
                    customization_targets,
                    customization_spectrum,
                    customization_spectrum_peaks,
                    delta_time
                )
                if customization_move_mode:
                    player_move(player, pygame.key.get_pressed())
                player.update(delta_time)
                dis.fill(DARK_GRAY)
                visual_effect_layer.fill((0, 0, 0, 0))
                draw_spectrum_bars(customization_spectrum)
                draw_board()
                update_enemies()
                player.draw()
                draw_customization_screen(
                    customization_item,
                    customization_move_mode,
                    customization_transition
                )
                pygame.display.update()
                continue

            if transition_elapsed < transition_duration:
                transition_elapsed = min(
                    transition_duration,
                    transition_elapsed + delta_time
                )
                if not transition_switched and transition_elapsed >= transition_duration / 2:
                    preview_level = selected_level
                    preview_track_duration_seconds = get_track_duration_seconds(preview_level)
                    game_level = preview_level + 1
                    pygame.mixer.music.stop()
                    preview_was_locked = is_level_locked(preview_level)
                    if not preview_was_locked:
                        pygame.mixer.music.load(MUSIC_TRACKS[preview_level])
                        pygame.mixer.music.play(fade_ms=120)
                    enemies.clear()
                    locked_preview_balls.clear()
                    locked_preview_timer = 0.0
                    locked_preview_index = 0
                    bomb_manager.reset_for_level()
                    spawn_state.reset()
                    preview_spectrum = [0.0] * SPECTRUM_BAND_COUNT
                    preview_spectrum_peaks = [
                        SPECTRUM_AGC_INITIAL_PEAK
                    ] * SPECTRUM_BAND_COUNT
                    preview_onset = 0.0
                    transition_switched = True

            preview_locked = is_level_locked(preview_level)
            if preview_locked != preview_was_locked:
                pygame.mixer.music.stop()
                enemies.clear()
                locked_preview_balls.clear()
                locked_preview_timer = 0.0
                locked_preview_index = 0
                bomb_manager.reset_for_level()
                if not preview_locked:
                    pygame.mixer.music.load(MUSIC_TRACKS[preview_level])
                    pygame.mixer.music.play(fade_ms=120)
                preview_was_locked = preview_locked

            if not preview_locked and not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
            if preview_locked:
                preview_music_ms = 0
                preview_pitch = 60.0
                preview_onset_target = 0.0
                preview_targets = (0.0,) * SPECTRUM_BAND_COUNT
            else:
                preview_music_ms = max(0, pygame.mixer.music.get_pos())
                preview_pitch, preview_onset_target, preview_targets = get_music_visual_features(
                    preview_music_ms,
                    preview_level + 1
                )
            update_spectrum_levels(
                preview_targets,
                preview_spectrum,
                preview_spectrum_peaks,
                delta_time
            )
            preview_onset += (
                preview_onset_target / 255.0 - preview_onset
            ) * (1.0 - math.exp(-18.0 * delta_time))

            if not preview_locked:
                # 스폰 함수의 dt는 기존 타이머 단위에 맞춘 프레임 보정값입니다.
                delay_step = 100.0 / tps
                spawn_enemies_by_level(spawn_state, delay_step)

            dis.fill(DARK_GRAY)
            draw_main_rhythm_polygon(
                preview_pitch,
                preview_onset * 255.0,
                preview_music_ms
            )
            draw_spectrum_bars(preview_spectrum)
            draw_board()
            if not preview_locked:
                bomb_manager.update(delta_time, None)
            if preview_locked:
                locked_preview_timer, locked_preview_index = update_locked_preview_balls(
                    locked_preview_balls,
                    delta_time,
                    locked_preview_timer,
                    locked_preview_index
                )
            else:
                update_enemies()
            fade_alpha = 0
            if transition_elapsed < transition_duration:
                fade_alpha = round(
                    255 * math.sin(math.pi * transition_elapsed / transition_duration)
                )
            draw_home_menu(
                selected_level,
                fade_alpha,
                preview_track_duration_seconds
            )
            pygame.display.update()

        pygame.mixer.music.stop()
        if not start_game:
            if not should_restart:
                break
            continue
        show_home = False

    player = Player()

    enemies = [Ball(), TBall(), VBall(), Laser()]
    bomb_manager.reset_for_level()
    spawn_state.reset()

    hit_count = [0, 0, 0, 0, 0]
    hit_stack = False

    enemies.clear()


    pause = False
    game_state = STATE_PLAY
    hitbox = False
    score = 0
    progress = 0.0
    clock = pygame.time.Clock()
    tps = 60
    restart_hold_seconds = 0.0
    attempt_finalized = False


    music_finish = False
    game_level = max(1, min(MAX_LEVEL, game_level))
    level_index = game_level - 1
    attempt_record_baseline = max(
        score_record[level_index],
        level_stats[level_index]["best_progress"]
    )
    session_id = uuid.uuid4().hex[:12].upper()
    session_attempt_count += 1
    attempt_best_progress = 0.0
    score_tick_accumulator = 0.0
    record_flash_remaining = 0.0
    session_record_flash_triggered = False
    level_stats[game_level - 1]["total_attempts"] += 1
    save_dirty = True
    music_path = MUSIC_TRACKS[game_level - 1]
    pygame.mixer.music.load(music_path)
    game_sound = pygame.mixer.Sound(music_path)
    pygame.mixer.music.play()
    pygame.mixer.music.set_endevent(music_endevent)
    spectrum_levels = [0.0] * SPECTRUM_BAND_COUNT
    spectrum_peak_levels = [
        SPECTRUM_AGC_INITIAL_PEAK
    ] * SPECTRUM_BAND_COUNT
    onset_envelope = 0.0
    esc_hold_seconds = 0.0
    esc_pressed_while_paused = False


    is_running = True
    should_restart = False
    # 한 판의 게임 진행과 화면 갱신을 처리하는 메인 루프입니다.
    while is_running:
        frame_delta_time = min(clock.get_time() / 1000.0, 0.05)
        record_flash_remaining = max(
            0.0,
            record_flash_remaining - frame_delta_time
        )
        if pause:
            game_state = STATE_PAUSE
        keys = pygame.key.get_pressed()
        # ESC를 눌렀다 놓으면 일시정지, 1초 유지하면 홈으로 돌아갑니다.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    esc_pressed_while_paused = pause
                    if not pause:
                        pause = True
                        game_state = STATE_PAUSE
                    esc_hold_seconds = 0.0
                if event.key == pygame.K_h:
                    hitbox = not hitbox
            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                if (
                    esc_pressed_while_paused
                    and esc_hold_seconds <= ESC_PAUSE_TAP_SECONDS
                    and not music_finish
                ):
                    pause = False
                    game_state = STATE_PLAY
                esc_hold_seconds = 0.0
                esc_pressed_while_paused = False
            
            if event.type == music_endevent:
                music_finish = True
                pause = True
                game_state = STATE_PAUSE
                level_index = game_level - 1
                if player.hp > 0:
                    progress = 100.0
                    attempt_best_progress = max(attempt_best_progress, progress)
                    session_best_progress = max(session_best_progress, progress)
                    level_stats[level_index]["cleared"] = True
                    level_stats[level_index]["clear_count"] += 1
                    clear_rank = get_clear_rank(player.hp, progress)
                    previous_rank = level_stats[level_index]["best_clear_rank"]
                    if (
                        previous_rank not in CLEAR_RANKS
                        or CLEAR_RANKS.index(clear_rank) < CLEAR_RANKS.index(previous_rank)
                    ):
                        level_stats[level_index]["best_clear_rank"] = clear_rank
                    save_dirty = True
                    if update_level_records(level_index, progress, score):
                        if not session_record_flash_triggered:
                            record_flash_remaining = RECORD_FLASH_DURATION
                            session_record_flash_triggered = True
                level_stats[level_index]["last_score"] = score
                attempt_finalized = True
                save_game_data()

        if pause:
            if keys[pygame.K_ESCAPE]:
                esc_hold_seconds = min(
                    ESC_HOME_HOLD_SECONDS,
                    esc_hold_seconds + frame_delta_time
                )
            else:
                esc_hold_seconds = 0.0
            if esc_hold_seconds >= ESC_HOME_HOLD_SECONDS:
                show_home = True
                game_state = STATE_HOME
                if not attempt_finalized:
                    level_stats[game_level - 1]["last_score"] = score
                    attempt_finalized = True
                    save_dirty = True
                save_game_data()
                is_running = False
                should_restart = True

        if pause and player.hp <= 0 and not attempt_finalized:
            level_stats[game_level - 1]["last_score"] = score
            attempt_finalized = True
            save_dirty = True

        if game_state == STATE_PLAY:
            player_move(player, keys)

        if keys[pygame.K_r] or keys[pygame.K_SPACE]:
            restart_hold_seconds = min(
                RESTART_HOLD_SECONDS,
                restart_hold_seconds + frame_delta_time
            )
            if restart_hold_seconds >= RESTART_HOLD_SECONDS:
                if not attempt_finalized:
                    level_stats[game_level - 1]["last_score"] = score
                    attempt_finalized = True
                    save_dirty = True
                is_running = False
                should_restart = True
        else:
            restart_hold_seconds = 0.0
        if game_state == STATE_PAUSE:
            pygame.mixer.music.pause()
            dis.fill(DARK_GRAY)
            draw_board()
            player.draw()
            update_enemies()
            bomb_manager.draw()

            # 어두운 바탕 위에 터미널 로그 패널을 좌우 정렬합니다.
            pause_dis.fill(pygame.SRCALPHA)
            pygame.draw.rect(pause_dis, (0, 0, 0, 192), (0, 0, display_size[0], display_size[1]))
            pygame.draw.line(
                pause_dis,
                (65, 78, 91, 210),
                (16, 154),
                (display_size[0] - 16, 154),
                1
            )
            draw_ui_text(
                pause_dis,
                "[ SESSION CONSOLE // PAUSED ]",
                (174, 218, 191),
                (display_size[0] // 2, 56),
                27,
                center=True,
                font_family="monospace"
            )
            level_index = game_level - 1
            current_stats = level_stats[level_index]
            current_rank = (
                get_clear_rank(max(player.hp, 0), progress)
                if music_finish
                else "Not cleared" if player.hp <= 0
                else "In progress"
            )
            left_x = 18
            right_x = display_size[0] - 18
            terminal_color = (205, 215, 220)
            label_color = (139, 180, 157)
            run_log_lines = (
                (f"[SESSION_ID] {session_id}", terminal_color),
                ("[STATE]      PAUSED", (236, 196, 112)),
                ("[SESSION_DATA] ------------------------------", label_color),
                (f"[SCORE]      {score:07d}", terminal_color),
                (f"[PROGRESS]   {progress:06.2f}% -> {attempt_best_progress:06.2f}%", terminal_color),
                (f"[TIME]       {format_track_time(game_sound.get_length())}", terminal_color),
                (f"[RUN_BEST]   {session_best_progress:06.2f}%", terminal_color),
                (f"[ATTEMPT]    {session_attempt_count:04d}", terminal_color),
                (f"[HP]         {max(player.hp, 0)} / 3", terminal_color),
                (f"[DAMAGE]     {max(0, 3 - player.hp)}", terminal_color),
                (f"[COLLISIONS] {sum(hit_count)}", terminal_color),
                (f"[HIT_BY]     BALL:{hit_count[0]:02d}  TBALL:{hit_count[1]:02d}", terminal_color),
                (f"             VBALL:{hit_count[2]:02d} LASER:{hit_count[3]:02d}", terminal_color),
                (f"             LOG:{hit_count[4]:02d}", terminal_color),
                ("[JUDGEMENT]  N/A (not tracked)", (155, 164, 170)),
                ("[COMBO]      N/A (not tracked)", (155, 164, 170)),
                (f"[FPS]        {clock.get_fps():05.1f}", terminal_color),
                (f"[FRAME_TIME] {clock.get_time():04d} ms", terminal_color),
            )
            track_hash = hashlib.sha256(
                f"{LEVEL_NAMES[level_index]}|{LEVEL_CREATORS[level_index]}|{MUSIC_TRACKS[level_index]}".encode("utf-8")
            ).hexdigest()[:12].upper()
            mixer_info = pygame.mixer.get_init()
            run_status = (
                "CLEARED" if current_stats["cleared"]
                else "FAILED" if player.hp <= 0
                else "IN_PROGRESS"
            )
            right_log_lines = (
                ("[TRACK_METADATA]", label_color),
                (f"[MAP]       {LEVEL_NAMES[level_index]}", terminal_color),
                (f"[ARTIST]    {LEVEL_CREATORS[level_index]}", terminal_color),
                (f"[DURATION]  {format_track_time(game_sound.get_length())}", terminal_color),
                (f"[TRACK_ID]  {track_hash}", terminal_color),
                ("[RECORDS]   ------------------------------", label_color),
                (f"[ALL_BEST]  {current_stats['best_progress']:06.2f}%", terminal_color),
                (f"[BEST_SCORE] {current_stats['best_score']:07d}", terminal_color),
                (f"[FINAL_SCORE] {current_stats['last_score']:07d}", terminal_color),
                (f"[TOTAL_ATTEMPT] {current_stats['total_attempts']:04d}", terminal_color),
                (f"[CLEARS]    {current_stats['clear_count']:04d}", terminal_color),
                (f"[STATUS]    {run_status}", GREEN if current_stats["cleared"] else terminal_color),
                (f"[RUN_RANK]  {current_rank.upper()}", terminal_color),
                (f"[BEST_RANK] {current_stats['best_clear_rank'].upper()}", terminal_color),
                ("[AUDIO_DEBUG] ------------------------------", label_color),
                (f"[MIX_RATE]  {mixer_info[0] if mixer_info else 'N/A'} Hz", terminal_color),
                (
                    f"[ONSETS]    "
                    f"{len(MAIN_RHYTHM_ONSETS[level_index]) if level_index < MAIN_RHYTHM_TRACK_COUNT else 0:06d}",
                    terminal_color
                ),
                ("[MEMORY]    sampler=disabled", (155, 164, 170)),
            )
            for row, (line, color) in enumerate(run_log_lines):
                draw_ui_text(
                    pause_dis,
                    line,
                    color,
                    (left_x, 174 + row * 30),
                    15,
                    font_family="monospace"
                )
            for row, (line, color) in enumerate(right_log_lines):
                draw_ui_text(
                    pause_dis,
                    line,
                    color,
                    (right_x, 174 + row * 30),
                    15,
                    alignment="right",
                    font_family="monospace"
                )
            draw_ui_text(
                pause_dis,
                "[ESC] HOLD 1.0s -> MAP SELECT  |  [ESC] TAP -> RESUME",
                (180, 193, 203),
                (display_size[0] // 2, display_size[1] - 44),
                13,
                center=True,
                font_family="monospace"
            )
            draw_hold_gauge(
                pause_dis,
                "ESC",
                esc_hold_seconds / ESC_HOME_HOLD_SECONDS,
                (display_size[0] - 244, 36),
                WHITE,
                opaque=True,
                right_aligned=True
            )
            if player.hp <= 0:
                draw_ui_text(
                    pause_dis,
                    "GAME OVER",
                    RED,
                    (display_size[0] // 2, 122),
                    40,
                    center=True
                )
            elif music_finish:
                draw_ui_text(
                    pause_dis,
                    "GAME CLEAR",
                    GREEN,
                    (display_size[0] // 2, 122),
                    40,
                    center=True
                )
            restart_hold_progress = restart_hold_seconds / RESTART_HOLD_SECONDS
            if restart_hold_progress > 0.0:
                draw_hold_gauge(
                    pause_dis,
                    "R",
                    restart_hold_progress,
                    (display_size[0] - 244, 12),
                    RED,
                    opaque=True,
                    right_aligned=True
                )
            pause_painting = pygame.transform.rotate(pause_dis, 0)
            dis.blit(pause_painting, pause_painting.get_rect(center=(display_size[0]//2, display_size[1]//2)))

        if game_state == STATE_PLAY:
            pygame.mixer.music.unpause()

            music_position_ms = max(0, pygame.mixer.music.get_pos())
            melody_pitch, onset_strength, target_spectrum = get_music_visual_features(
                music_position_ms,
                game_level
            )
            delta_time = min(clock.get_time() / 1000.0, 0.05)
            update_spectrum_levels(
                target_spectrum,
                spectrum_levels,
                spectrum_peak_levels,
                delta_time
            )
            onset_blend = 1.0 - math.exp(-18.0 * delta_time)
            onset_envelope += (onset_strength / 255.0 - onset_envelope) * onset_blend

            score, score_tick_accumulator = award_score_for_ticks(
                score,
                score_tick_accumulator,
                player.hp,
                delta_time,
                tps
            )
            session_best_score = max(session_best_score, score)

            track_duration = max(game_sound.get_length(), 0.001)
            progress = min(100.0, music_position_ms / (track_duration * 10.0))
            level_index = game_level - 1
            is_beating_all_best = (
                player.hp > 0
                and progress > attempt_record_baseline
            )
            if player.hp > 0:
                attempt_best_progress = max(attempt_best_progress, progress)
                session_best_progress = max(session_best_progress, progress)
                new_progress_record = update_level_records(
                    level_index,
                    progress,
                    score
                )
                if new_progress_record and not session_record_flash_triggered:
                    record_flash_remaining = RECORD_FLASH_DURATION
                    session_record_flash_triggered = True
            flash_strength = (
                record_flash_remaining / RECORD_FLASH_DURATION
            ) ** 2
            if not is_beating_all_best:
                flash_strength = 0.0

            # 배경, 음높이·온셋 반응 도형, 좌우 스펙트럼, 보드 순서로 그립니다.
            dis.fill(DARK_GRAY)
            draw_main_rhythm_polygon(
                melody_pitch,
                onset_envelope * 255.0,
                music_position_ms,
                flash_strength
            )
            draw_spectrum_bars(spectrum_levels, flash_strength)
            draw_board()
            
            draw_ui_text(dis, f"{progress:.2f}%", WHITE, (10, 10))
            draw_ui_text(dis, f"SCORE {score}", WHITE, (10, 34), 16)
            elapsed_seconds = min(
                track_duration,
                max(0.0, music_position_ms / 1000.0)
            )
            draw_ui_text(
                dis,
                f"TIME {format_track_time(elapsed_seconds)} / {format_track_time(track_duration)}",
                LIGHT_GRAY,
                (10, 54),
                15
            )
            if is_beating_all_best:
                dis.blit(CROWN_IMAGE, (94, 8))
            restart_hold_progress = restart_hold_seconds / RESTART_HOLD_SECONDS
            if restart_hold_progress > 0.0:
                draw_hold_gauge(
                    dis,
                    "R",
                    restart_hold_progress,
                    (display_size[0] - 244, 12),
                    RED,
                    right_aligned=True
                )
            if esc_hold_seconds > 0.0:
                draw_hold_gauge(
                    dis,
                    "ESC",
                    esc_hold_seconds / ESC_HOME_HOLD_SECONDS,
                    (display_size[0] - 244, 36),
                    WHITE,
                    right_aligned=True
                )

            # 플레이어를 이동시키고 화면에 그립니다.
            player.update(frame_delta_time)
            player.draw()

            # 생성 대기 시간을 줄이고 적을 생성한 뒤 움직입니다.
            # 스폰 타이머는 설정한 delay 값을 100/tps만큼 매 프레임 감소시킵니다.
            spawn_enemies_by_level(spawn_state, 100.0 / tps)
            update_enemies()
            bomb_manager.update(delta_time, player)

        # 디스크에 매 프레임 쓰지 않도록 변경된 기록은 5초마다 자동 저장합니다.
        if save_dirty and pygame.time.get_ticks() - last_save_time >= 5000:
            save_game_data()

        pygame.display.update()
        clock.tick(tps)
    if not attempt_finalized:
        level_stats[game_level - 1]["last_score"] = score
        attempt_finalized = True
        save_dirty = True
    pygame.mixer.music.set_endevent()
    pygame.mixer.music.stop()
    save_game_data()
_save_game_data_on_exit()
pygame.quit()
