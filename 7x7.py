import pygame
from pygame.surface import Surface
from pygame.color import Color
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Sequence
import random
import math
import base64
import json
import os
import hashlib
import uuid
from functools import lru_cache


pygame.init()

# 보드 크기만 줄이고 창 해상도는 1200x900으로 유지합니다.
GRID_SIZE = 7
ELEMENT_SCALE = 0.88
CELL_SIZE = round(100 * ELEMENT_SCALE)
BOARD_HALF_SIZE = GRID_SIZE * CELL_SIZE // 2
GRID_EDGE_OFFSET = (GRID_SIZE - 1) * CELL_SIZE // 2
# 이동 마지막 프레임에 속도를 반전하므로 실제 이동량은 속도 × (프레임 수 - 2)입니다.
MOVE_DURATION = 12
NORMAL_MOVE_SPEED = CELL_SIZE / (MOVE_DURATION - 2)
WRAP_MOVE_SPEED = CELL_SIZE * (GRID_SIZE - 1) / (MOVE_DURATION - 2)
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
dis = pygame.display.set_mode(display_size, pygame.SRCALPHA)
pygame.display.set_caption("7x7")
pygame.mixer.music.load("music/Sunburst_NCS.mp3")
pygame.mixer.music.set_volume(1)


MUSIC_1 = "music/Sunburst_NCS.mp3"
MUSIC_2 = "music/MintParfait.mp3"
MUSIC_3 = "music/SmokedTurkeyRag.mp3"
MUSIC_4 = "music/DaDiDuDonut.mp3"
MUSIC_5 = "music/Butterfly.mp3"
MUSIC_6 = "music/MyLittleHero.mp3"
MUSIC_7 = "music/PixelPig.mp3"
MUSIC_8 = "music/NyanCat.mp3"
MUSIC_9 = "music/TheWorldRevolvong.mp3"
MUSIC_10 = "music/Megalovania.mp3"
MAX_LEVEL = 10
GAME_DATA_VERSION = 1
MAIN_RHYTHM_DATA_VERSION = 1
BOSS_LEVEL_INDICES = (5, MAX_LEVEL - 1)
BOSS_6_UNLOCK_REQUIRED_PROGRESS = 30.0
BOSS_10_UNLOCK_REQUIRED_LEVEL_INDEX = 8
MUSIC_TRACKS = (MUSIC_1, MUSIC_2, MUSIC_3, MUSIC_4, MUSIC_5, MUSIC_6, MUSIC_7, MUSIC_8, MUSIC_9, MUSIC_10)
LEVEL_NAMES = (
    "Sunburst",
    "MintParfait",
    "SmokedTurkeyRag",
    "DaDiDuDonut",
    "Butterfly",
    "MyLittleHero",
    "PixelPig",
    "NyanCat",
    "TheWorldRevolving",
    "Megalovania",
)
LEVEL_CREATORS = (
    "NCS",
    "a_hisa",
    "a_hisa",
    "a_hisa",
    "a_hisa",
    "a_hisa",
    "Di Young",
    "?",
    "Toby Fox",
    "Toby Fox",
)
STATE_HOME = "home"
STATE_PLAY = "play"
STATE_PAUSE = "pause"
debug_boss_unlock_overrides = {}
game_sound = pygame.mixer.Sound(MUSIC_1)
TRACK_DURATION_SECONDS = {0: game_sound.get_length()}


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
if (
    main_rhythm_data.get("version") != MAIN_RHYTHM_DATA_VERSION
    or not isinstance(MAIN_RHYTHM_SAMPLE_INTERVAL, (int, float))
    or not math.isfinite(MAIN_RHYTHM_SAMPLE_INTERVAL)
    or MAIN_RHYTHM_SAMPLE_INTERVAL <= 0
    or SPECTRUM_BAND_COUNT != 24
    or main_rhythm_data.get("feature_stride") != FEATURE_STRIDE
    or not 0 < MAIN_RHYTHM_TRACK_COUNT <= MAX_LEVEL
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

SPECTRUM_BAR_MAX_LENGTH = 92
SPECTRUM_BAR_HEIGHT = 7
SPECTRUM_BAR_TOP = 148
SPECTRUM_BAR_SPACING = 25
SPECTRUM_ATTACK_SPEED = 22.0
SPECTRUM_RELEASE_SPEED = 9.0
SPECTRUM_BAR_COLORS = (
    (255, 255, 255),
    (205, 205, 205),
    (235, 235, 235)
)
ESC_HOME_HOLD_SECONDS = 1.0
RESTART_HOLD_SECONDS = ESC_HOME_HOLD_SECONDS
ESC_PAUSE_TAP_SECONDS = 0.2
HOLD_GAUGE_SIZE = (190, 9)
RECORD_FLASH_DURATION = 1.0
BOMB_CHARGE_SECONDS = 1.8
BOMB_CHAIN_DELAY_SECONDS = 0.3
BOMB_DAMAGE_WINDOW_SECONDS = 0.3
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


def get_music_visual_features(playback_ms: int, level: int) -> Tuple[float, float, Tuple[float, ...]]:
    """현재 음악 시점의 음높이, 온셋, 주파수 대역을 부드럽게 보간합니다."""
    if level > MAIN_RHYTHM_TRACK_COUNT:
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
            float(frames[first_offset + 1]),
            tuple(float(value) for value in frames[first_offset + 2:first_offset + FEATURE_STRIDE])
        )

    fraction = sample_position - first_index
    next_offset = first_offset + FEATURE_STRIDE
    return (
        frames[first_offset] + (frames[next_offset] - frames[first_offset]) * fraction,
        frames[first_offset + 1] + (frames[next_offset + 1] - frames[first_offset + 1]) * fraction,
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
    pitch_amount = max(0.0, min(1.0, (pitch - 60.0) / 30.0))
    radius = (315.0 + pitch_amount * 52.0 + onset_strength / 255.0 * 18.0)
    rotation = playback_ms * 0.00004 + (pitch - 69.0) * 0.002
    center = (display_size[0] // 2, display_size[1] // 2)
    points = [
        (
            round(center[0] + math.cos(math.tau * index / 12 + rotation) * radius),
            round(center[1] + math.sin(math.tau * index / 12 + rotation) * radius)
        )
        for index in range(12)
    ]
    alpha = round(76 + onset_strength / 255.0 * 24)
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
    """주파수별 회백색 막대를 효과 레이어에 합성해 한 번에 표시합니다."""
    flash = max(0.0, min(1.0, record_flash))
    for band, level in enumerate(levels):
        if level < 8:
            continue
        bar_length = max(2, round(level / 255.0 * SPECTRUM_BAR_MAX_LENGTH))
        y = SPECTRUM_BAR_TOP + band * SPECTRUM_BAR_SPACING
        energy = min(1.0, level / 255.0)
        base_color = SPECTRUM_BAR_COLORS[band % len(SPECTRUM_BAR_COLORS)]
        color = (
            round(base_color[0] + (255 - base_color[0]) * flash),
            round(base_color[1] + (220 - base_color[1]) * flash),
            round(base_color[2] + (80 - base_color[2]) * flash),
            round(230 + energy * 25)
        )
        glow_color = (
            min(255, color[0] + 8),
            min(255, color[1] + 8),
            min(255, color[2] + 8),
            76
        )
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
    """각 보스 단계의 해금 조건을 검사합니다."""
    if level_index in debug_boss_unlock_overrides:
        return debug_boss_unlock_overrides[level_index]
    if level_index == 5:
        return all(
            get_best_level_progress(required_level) >= BOSS_6_UNLOCK_REQUIRED_PROGRESS
            for required_level in range(5)
        )
    if level_index == MAX_LEVEL - 1:
        return level_stats[BOSS_10_UNLOCK_REQUIRED_LEVEL_INDEX]["cleared"]
    return True


def is_level_locked(level_index: int) -> bool:
    """두 보스 단계에만 해금 조건을 적용합니다."""
    return (
        level_index in BOSS_LEVEL_INDICES
        and not is_boss_level_unlocked(level_index)
    )


def draw_home_menu(
    selected_level: int,
    fade_alpha: int,
    track_duration_seconds: float
) -> None:
    """음악 미리보기 위에 세로 레벨 캐러셀과 조작 안내를 표시합니다."""
    dis.blit(home_menu_gradient, (display_size[0] - home_menu_gradient.get_width(), 0))
    menu_text_x = display_size[0] - 260
    draw_ui_text(dis, "SELECT A MAP", (218, 223, 231, 220), (menu_text_x, 58), 27)
    if selected_level == 0:
        stage_label = f"TUTORIAL  |  1 / {MAX_LEVEL}"
    elif selected_level in BOSS_LEVEL_INDICES:
        stage_label = f"BOSS STAGE  |  {selected_level + 1} / {MAX_LEVEL}"
    else:
        stage_label = f"STAGE  {selected_level + 1} / {MAX_LEVEL}"
    draw_ui_text(dis, stage_label, LIGHT_GRAY, (menu_text_x, 91), 14)

    for level_index, (name, creator) in enumerate(zip(LEVEL_NAMES, LEVEL_CREATORS)):
        offset = level_index - selected_level
        if abs(offset) > MAX_LEVEL // 2:
            continue
        y = display_size[1] // 2 + offset * 68
        if level_index == selected_level:
            dis.blit(home_highlight_glow, (menu_text_x - 20, y - 29))
            pygame.draw.line(
                dis,
                (238, 243, 252, 208),
                (menu_text_x - 14, y - 19),
                (menu_text_x - 14, y + 19),
                2
            )
            draw_ui_text(dis, name, WHITE, (menu_text_x, y - 19), 27)
            if is_level_locked(level_index):
                draw_ui_text(
                    dis,
                    "[LOCKED]",
                    (255, 174, 138, 235),
                    (menu_text_x + 184, y - 13),
                    14
                )
            draw_ui_text(dis, creator, (205, 211, 220, 210), (menu_text_x, y + 14), 14)
        else:
            distance = abs(offset)
            alpha = max(38, round(178 * math.exp(-distance * 0.52)))
            color = (190, 195, 205, alpha)
            locked_label = " [LOCKED]" if is_level_locked(level_index) else ""
            draw_ui_text(
                dis,
                f"{name} ({creator}){locked_label}",
                color,
                (menu_text_x, y - max(8, 12 - distance)),
                max(14, 21 - distance)
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
    if is_level_locked(selected_level):
        if selected_level == 5:
            unlock_message = "LOCKED - CLEAR STAGES 1-5 AT 30%+"
            unlock_detail = "TO UNLOCK THE STAGE 6 BOSS"
        else:
            unlock_message = "LOCKED - CLEAR STAGE 9"
            unlock_detail = "TO UNLOCK THE STAGE 10 BOSS"
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

    if fade_alpha > 0:
        home_fade_surface.fill((0, 0, 0, min(255, fade_alpha)))
        dis.blit(home_fade_surface, (0, 0))


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


def update_enemies():
    global enemies, hit_count, hit_stack
    if enemies:
        alive_count = 0
        for enemy in enemies:
            hit_index = ENEMY_HIT_INDEX.get(type(enemy))
            if hit_index is not None:
                if not pause:
                    enemy.update()
                    if player is not None and player.hp_minus and not hit_stack:
                        hit_count[hit_index] += 1
                        hit_stack = True
                enemy.draw()
            if not enemy.is_deleted():
                enemies[alive_count] = enemy
                alive_count += 1
        del enemies[alive_count:]




class Player(object):
    def __init__(
        self,
        position: Tuple[int, int] = (display_size[0]//2, display_size[1]//2),
        hp: int = 3,
        max_afterimage: int = 10
        ):
        # 이동 중 좌표를 수정할 수 있도록 전달받은 위치를 새 리스트로 복사합니다.
        self.pos = list(position)
        self.move_stack = 0
        self.move = [0, 0]
        self.move_rebound = [0.0, 0.0]
        self.hp = hp
        self.hp_minus = False
        self.hp_stack = 100
        self.color = WHITE
        self.invincible = False
        self.size = 50-(3-self.hp)*6
        self.afterimage = []
        self.afterimage_max = max_afterimage
        
        self.ai_dis = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.dis = pygame.Surface((100, 100), pygame.SRCALPHA)
    
    def update(self):
        global pause, hit_stack
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
                self.hp -= 1
                if self.hp == 0:
                    pause = True
            
            self.hp_stack -= 1/tps*50
        
        if self.hp_stack <= 0:
            self.hp_minus = False
            self.hp_stack = 100
            hit_stack = False

        self.size = 50-(3-max(self.hp, 0))*6

    def get_rect(self) -> pygame.Rect:
        hitbox_size = round((self.size - 10) * ELEMENT_SCALE)
        return pygame.Rect(
            round(self.pos[0] - hitbox_size / 2),
            round(self.pos[1] - hitbox_size / 2),
            hitbox_size,
            hitbox_size
        )

    def draw(self):
        for r in range(10): pygame.draw.circle(self.dis, set_alpha(self.color, r/9*255), (50, 50), 33-r)
        if hitbox: pygame.draw.lines(self.dis, BLUE, True, ((30, 30), (70, 30), (70, 70), (30, 70)), 1)

        self.hp_stack_seq = 100-self.hp_stack
        if 0 < self.hp_stack_seq <= 20: self.dis.set_alpha(64)
        elif 20 < self.hp_stack_seq <= 40: self.dis.set_alpha(255)
        elif 40 < self.hp_stack_seq <= 60: self.dis.set_alpha(64)
        elif 60 < self.hp_stack_seq <= 80: self.dis.set_alpha(255)
        elif 80 < self.hp_stack_seq <= 100: self.dis.set_alpha(64)
        else: self.dis.set_alpha(255)

        render_size = max(1, round(self.size * 2 * ELEMENT_SCALE))
        self.player_painting = pygame.transform.scale(
            self.dis,
            (render_size, render_size)
        )

        for ai in self.afterimage:
            self.ai_dis = self.player_painting.copy()
            if not pause:
                ai[1] -= 128/self.afterimage_max
                if ai[1] <= 0: self.afterimage.remove(ai)
            self.ai_dis.set_alpha(ai[1])
            dis.blit(self.ai_dis, self.ai_dis.get_rect(center=(ai[0][0], ai[0][1])))

        dis.blit(self.player_painting, self.player_painting.get_rect(center=(self.pos[0], self.pos[1])))

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


class Ball(object):
    def configure(
        self,
        position: Tuple[int, int],
        speed: Tuple[int, int] = 5
        ):
        self.pos = position
        self.move = speed
        self.hitbox = pygame.Rect(0, 0, ENEMY_HITBOX_SIZE, ENEMY_HITBOX_SIZE)
        self.dis = ball_dis

    def update(self):
        self.pos = (self.pos[0]+self.move[0], self.pos[1]+self.move[1])
        self.hitbox.center = self.pos
        if player is not None and player.get_rect().colliderect(self.hitbox):
            if not player.hp_minus and not player.invincible:
                player.hp_minus = True

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
        turn: float = 1
        ):
        self.position = position
        self.pos = position[0:2]
        self.angle = position[2]
        self.length = length
        self.speed = speed/length
        self.turn = turn
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
            if abs(self.angle-self.position[2]) >= self.turn*2*math.pi:
                self.delete = True
            self.hitbox.center = self.pos
            if player is not None and player.get_rect().colliderect(self.hitbox):
                if not player.hp_minus and not player.invincible:
                    player.hp_minus = True
    
    def is_deleted(
        self
        ) -> bool:
        if self.delete:
            return True
        return False

    def draw(
        self
        ):
        dis.blit(self.line_dis, self.line_dis.get_rect(center=self.position[0:2]))
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
        apex_steps = max(2, round(2 * abs(displacement) / initial_speed) + 1)
        initial_speed = 2 * abs(displacement) / (apex_steps - 1)
        adjusted_speed = [0.0, 0.0]
        adjusted_speed[axis] = direction * initial_speed
        self.speed = tuple(adjusted_speed)
        self.spp = -initial_speed / apex_steps
        self.apex_steps = apex_steps
        self.target_coordinate = target_coordinate
        self.hitbox = pygame.Rect(0, 0, ENEMY_HITBOX_SIZE, ENEMY_HITBOX_SIZE)
        self.dis = ball_dis

    def update(
        self
        ):
        if self.face == 0:
            self.speed = (self.speed[0], self.speed[1]+self.spp)
        if self.face == 1:
            self.speed = (self.speed[0]-self.spp, self.speed[1])
        if self.face == 2:
            self.speed = (self.speed[0], self.speed[1]-self.spp)
        if self.face == 3:
            self.speed = (self.speed[0]+self.spp, self.speed[1])
        self.pos = (self.pos[0]+self.speed[0], self.pos[1]+self.speed[1])
        if self.apex_steps > 0:
            self.apex_steps -= 1
            if self.apex_steps == 0:
                axis = 1 if self.face in (0, 2) else 0
                self.pos = (
                    (self.target_coordinate, self.pos[1])
                    if axis == 0
                    else (self.pos[0], self.target_coordinate)
                )
                self.speed = (
                    (0.0, self.speed[1])
                    if axis == 0
                    else (self.speed[0], 0.0)
                )
        self.hitbox.center = self.pos
        if player is not None and player.get_rect().colliderect(self.hitbox):
            if not player.hp_minus and not player.invincible:
                player.hp_minus = True

    def is_deleted(
        self
        ) -> bool:
        if not -500 < self.pos[0] < display_size[0]+500 and not -500 < self.pos[1] < display_size[1]+500:
            return True
        return False

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

        if player is not None and player.get_rect().colliderect(self.hitbox):
            if not player.hp_minus and not player.invincible:
                player.hp_minus = True

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
                self.delay = tps
                self.stage = 2
        
        if self.stage == 2:
            self.delay -= 1
            self.hitbox = self._get_beam_rect()
            if player is not None and player.get_rect().colliderect(self.hitbox):
                if not player.hp_minus and not player.invincible:
                    player.hp_minus = True
            if self.delay <= 0:
                self.stage = 3
        
        if self.stage == 3:
            if self.face == 0:
                self.pos = [self.pos[0], self.pos[1]-self.speed]
                if self.pos[1] <= display_size[1]//2-BOARD_HALF_SIZE-2*CELL_SIZE:
                    self.delete = True
            if self.face == 1:
                self.pos = [self.pos[0]+self.speed, self.pos[1]]
                if self.pos[0] >= display_size[0]//2+BOARD_HALF_SIZE+3*CELL_SIZE:
                    self.delete = True
            if self.face == 2:
                self.pos = [self.pos[0], self.pos[1]+self.speed]
                if self.pos[1] >= display_size[1]//2+BOARD_HALF_SIZE+2*CELL_SIZE:
                    self.delete = True
            if self.face == 3:
                self.pos = [self.pos[0]-self.speed, self.pos[1]]
                if self.pos[0] <= display_size[0]//2-BOARD_HALF_SIZE-3*CELL_SIZE:
                    self.delete = True
            self.speed += 0.1
    
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
            self._damage_player_in_blast_cell(target_player)
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
        """모든 연쇄 타일을 거리순으로 한 번만 계산해 메인 폭탄에 저장합니다."""
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
    """폭발 표면을 시계 방향으로 회전시키며 0.5초 동안 완전히 축소합니다."""
    progress = max(
        0.0,
        min(1.0, 1.0 - remaining_seconds / BOMB_DAMAGE_WINDOW_SECONDS)
    )
    swell_progress = 0.2
    if progress <= swell_progress:
        scale = 1.0 + 0.45 * progress / swell_progress
    else:
        shrink_progress = (progress - swell_progress) / (1.0 - swell_progress)
        scale = 1.45 * (1.0 - shrink_progress)
    if scale <= 0.02:
        return
    rotated = pygame.transform.rotate(canvas, -1080.0 * progress)
    scaled_size = max(1, round(BOMB_SHAPE_SIZE * scale))
    rotated = pygame.transform.smoothscale(
        rotated,
        (scaled_size, scaled_size)
    )
    dis.blit(rotated, rotated.get_rect(center=position))


def get_bomb_chain_cells(
    row: int,
    column: int,
    chain_range: int,
    diagonal_chain: bool
) -> List[Tuple[int, int, int]]:
    """중심을 제외하고 십자 또는 대각 십자 방향의 유효 칸만 반환합니다."""
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

    def spawn(self) -> bool:
        """폭탄이 없는 무작위 보드 칸에 메인 폭탄을 생성합니다."""
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

        row, column = random.choice(available_cells)
        bomb = Bomb()
        bomb.configure(
            row,
            column,
            random.randint(0, 3),
            bool(random.getrandbits(1))
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


def spawn_ball():
    """보드 가장자리 바깥에서 직선으로 들어오는 공을 생성합니다."""
    for _ in range(20):
        ball = Ball()
        ball_position = random.randint(0, GRID_SIZE - 1)
        lane_offset = -GRID_EDGE_OFFSET + CELL_SIZE * ball_position
        move_rotate = random.randint(0, 1)
        if random.randint(0, 1):
            position = (
                display_size[0] // 2
                - (BOARD_HALF_SIZE + 3 * CELL_SIZE) * (2 * move_rotate - 1),
                display_size[1] // 2 + lane_offset
            )
            speed = (3 * (2 * move_rotate - 1), 0)
        else:
            position = (
                display_size[0] // 2 + lane_offset,
                display_size[1] // 2
                - (BOARD_HALF_SIZE + 3 * CELL_SIZE) * (2 * move_rotate - 1)
            )
            speed = (0, 3 * (2 * move_rotate - 1))
        ball.configure(position, speed)
        if _try_add_enemy(ball):
            return

def spawn_tball():
    """무작위 칸을 중심으로 회전하는 TBall을 생성합니다."""
    for _ in range(20):
        tball = TBall()
        # TBall은 보드 안의 칸 중심 중 하나에서 원형 궤적을 시작합니다.
        tball_pos = [
            display_size[0] // 2 - GRID_EDGE_OFFSET
            + CELL_SIZE * random.randint(0, GRID_SIZE - 1),
            display_size[1] // 2 - GRID_EDGE_OFFSET
            + CELL_SIZE * random.randint(0, GRID_SIZE - 1),
            random.randint(0, 7) / 4 * math.pi
        ]
        tball_length = CELL_SIZE * random.randint(1, 5)
        tball_speed = random.randint(5, 7) * (2 * random.randint(0, 1) - 1)
        tball_turn = random.randint(1, 2)
        tball.configure(tball_pos, tball_length, tball_speed, tball_turn)
        if _try_add_enemy(tball):
            return

def spawn_vball():
    """보드 바깥에서 진입하며 궤적이 휘는 VBall을 생성합니다."""
    for _ in range(20):
        vball = VBall()
        vb_face = random.randint(0, 3)
        vb_pos = -GRID_EDGE_OFFSET + CELL_SIZE * random.randint(0, GRID_SIZE - 1)
        # 궤도의 정점은 이동 방향을 따라 선택한 한 칸의 중앙에 놓습니다.
        vb_target_cell = random.randint(0, GRID_SIZE - 1)
        if vb_face == 0:
            position, speed = (
                (display_size[0] // 2 + vb_pos, display_size[1] // 2 - BOARD_HALF_SIZE - 2 * CELL_SIZE),
                (0, 10)
            )
        elif vb_face == 1:
            position, speed = (
                (display_size[0] // 2 + BOARD_HALF_SIZE + 3 * CELL_SIZE, display_size[1] // 2 + vb_pos),
                (-10, 0)
            )
        elif vb_face == 2:
            position, speed = (
                (display_size[0] // 2 + vb_pos, display_size[1] // 2 + BOARD_HALF_SIZE + 2 * CELL_SIZE),
                (0, -10)
            )
        else:
            position, speed = (
                (display_size[0] // 2 - BOARD_HALF_SIZE - 3 * CELL_SIZE, display_size[1] // 2 + vb_pos),
                (10, 0)
            )
        vball.configure(position, vb_face, vb_target_cell, speed)
        if _try_add_enemy(vball):
            return

def spawn_laser():
    """보드 바깥에서 안쪽으로 발사되는 레이저를 생성합니다."""
    for _ in range(20):
        laser = Laser()
        laser_face = random.randint(0, 3)
        laser_pos = -GRID_EDGE_OFFSET + CELL_SIZE * random.randint(0, GRID_SIZE - 1)
        if laser_face == 0:
            position = (
                display_size[0] // 2 + laser_pos,
                display_size[1] // 2 - BOARD_HALF_SIZE - 3 * CELL_SIZE
            )
        elif laser_face == 1:
            position = (
                display_size[0] // 2 + BOARD_HALF_SIZE + 3 * CELL_SIZE,
                display_size[1] // 2 + laser_pos
            )
        elif laser_face == 2:
            position = (
                display_size[0] // 2 + laser_pos,
                display_size[1] // 2 + BOARD_HALF_SIZE + 3 * CELL_SIZE
            )
        else:
            position = (
                display_size[0] // 2 - BOARD_HALF_SIZE - 3 * CELL_SIZE,
                display_size[1] // 2 + laser_pos
            )
        laser.configure(position, laser_face)
        if _try_add_enemy(laser):
            return


def spawn_log():
    """3~7칸 길이의 통나무를 보드 밖에서 무작위 행 또는 열로 굴립니다."""
    board_left = display_size[0] // 2 - BOARD_HALF_SIZE
    board_right = display_size[0] // 2 + BOARD_HALF_SIZE
    board_top = display_size[1] // 2 - BOARD_HALF_SIZE
    board_bottom = display_size[1] // 2 + BOARD_HALF_SIZE
    log_radius = Log.thickness // 2
    for _ in range(20):
        log_length = random.randint(3, GRID_SIZE)
        first_lane = random.randint(0, GRID_SIZE - log_length)
        log_face = random.randint(0, 3)
        lane_start = board_left if log_face in (0, 2) else board_top
        lane_center = lane_start + (first_lane + log_length / 2) * CELL_SIZE

        if log_face == 0:
            position = (lane_center, board_top - 3 * CELL_SIZE - log_radius)
        elif log_face == 1:
            position = (board_right + 3 * CELL_SIZE + log_radius, lane_center)
        elif log_face == 2:
            position = (lane_center, board_bottom + 3 * CELL_SIZE + log_radius)
        else:
            position = (board_left - 3 * CELL_SIZE - log_radius, lane_center)

        log = Log()
        log.configure(position, log_face, log_length)
        if _try_add_enemy(log):
            return


def spawn_bomb() -> bool:
    """메인 폭탄 하나를 생성합니다. 보드 타일이 가득 차면 생성하지 않습니다."""
    return bomb_manager.spawn()


def spawn_enemies_by_level() -> None:
    """현재 레벨의 장애물 생성 규칙과 폭탄 지연 스폰을 처리합니다."""
    global ball_delay, tball_delay, vball_delay, laser_delay, log_delay, bomb_delay
    if game_level == 1:
        if ball_delay <= 0 and False:
            spawn_ball()
            ball_delay = 10*random.randint(10, 30)
            for i in range(random.randint(0, 3)): spawn_ball()
        if tball_delay <= 0 and False:
            spawn_tball()
            tball_delay = 10*random.randint(40, 70)
            for i in range(random.randint(0, 0)): spawn_tball()
        if vball_delay <= 0 and False:
            spawn_vball()
            vball_delay = 10*random.randint(20, 30)
            for i in range(random.randint(0, 2)): spawn_vball()
        if laser_delay <= 0 and False:
            spawn_laser()
            laser_delay = 10*random.randint(80, 150)
            if random.randint(1, 20) == 1: spawn_laser()
        if log_delay <= 0 and False:
            spawn_log()
            log_delay = 10*random.randint(10, 20)
            for i in range(random.randint(0, 0)): spawn_log()
        if bomb_delay <= 0:
            spawn_bomb()
            bomb_delay = 10*random.randint(40, 40)
    if game_level == 2:
        if ball_delay <= 0:
            spawn_ball()
            ball_delay = 10*random.randint(30, 50)
            for i in range(random.randint(0, 3)): spawn_ball()
        if tball_delay <= 0 and False:
            spawn_tball()
            tball_delay = 10*random.randint(200, 200)
        if vball_delay <= 0:
            spawn_vball()
            vball_delay = 10*random.randint(20, 20)
            for i in range(random.randint(2, 2)): spawn_vball()
        if laser_delay <= 0:
            spawn_laser()
            laser_delay = 10*random.randint(100, 150)
            for i in range(random.randint(0, 2)): spawn_laser()
            if random.randint(1, 5) == 1: laser_delay = 0
        if log_delay <= 0 and False:
            spawn_log()
            log_delay = 10*random.randint(10, 20)
            for i in range(random.randint(0, 0)): spawn_log()
        if bomb_delay <= 0:
            spawn_bomb()
            bomb_delay = 10*random.randint(300, 400)
    if game_level == 3:
        if ball_delay <= 0:
            spawn_ball()
            ball_delay = 10*random.randint(20, 50)
            for i in range(random.randint(0, 0)): spawn_ball()
            if random.randint(1, 3) == 1: ball_delay = 0
        if tball_delay <= 0:
            spawn_tball()
            tball_delay = 10*random.randint(50, 80)
            for i in range(random.randint(1, 2)): spawn_tball()
        if vball_delay <= 0 and False:
            spawn_vball()
            vball_delay = 10*random.randint(100, 200)
        if laser_delay <= 0:
            laser_delay = 10*random.randint(20, 20)
            for i in range(random.randint(4, 5)): spawn_laser()
        if log_delay <= 0 and False:
            spawn_log()
            log_delay = 10*random.randint(10, 20)
            for i in range(random.randint(0, 0)): spawn_log()
        if bomb_delay <= 0:
            spawn_bomb()
            bomb_delay = 10*random.randint(250, 350)
    if game_level == 4:
        if ball_delay <= 0 and False:
            spawn_ball()
            ball_delay = 10*random.randint(100, 150)
            for i in range(random.randint(0, 0)): spawn_ball()
        if tball_delay <= 0:
            tball_delay = 10*random.randint(30, 30)
            for i in range(random.randint(3, 3)): spawn_tball()
        if vball_delay <= 0 and False:
            spawn_vball()
            vball_delay = 10*random.randint(50, 150)
            for i in range(random.randint(0, 0)): spawn_vball()
        if laser_delay <= 0 and False:
            spawn_laser()
            laser_delay = 10*random.randint(10, 20)
            for i in range(random.randint(0, 0)): spawn_laser()
        if log_delay <= 0:
            spawn_log()
            log_delay = 10*random.randint(50, 100)
            for i in range(random.randint(0, 0)): spawn_log()
            if random.randint(1, 4) == 1: log_delay = 10*10
        if bomb_delay <= 0:
            spawn_bomb()
            bomb_delay = 10*random.randint(220, 300)
    if game_level == 5:
        if ball_delay <= 0:
            ball_delay = 10*random.randint(20, 30)
            for i in range(random.randint(3, 6)): spawn_ball()
        if tball_delay <= 0 and False:
            spawn_tball()
            tball_delay = 10*random.randint(70, 150)
            for i in range(random.randint(0, 0)): spawn_tball()
        if vball_delay <= 0:
            vball_delay = 10*random.randint(10, 30)
            for i in range(random.randint(2, 4)): spawn_vball()
        if laser_delay <= 0:
            laser_delay = 10*random.randint(30, 60)
            for i in range(random.randint(2, 2)): spawn_laser()
            if random.randint(1, 5) == 1: spawn_laser()
        if log_delay <= 0 and False:
            spawn_log()
            log_delay = 10*random.randint(10, 20)
            for i in range(random.randint(0, 0)): spawn_log()
        if bomb_delay <= 0:
            spawn_bomb()
            bomb_delay = 10*random.randint(180, 250)
    if game_level == 6:  # 보스맵
        if ball_delay <= 0:
            ball_delay = 10*random.randint(10, 10)
            for i in range(random.randint(0, 1)): spawn_ball()
            if random.randint(1, 4) == 1: ball_delay = 0
        if tball_delay <= 0:
            tball_delay = 10*random.randint(20, 40)
            for i in range(random.randint(1, 2)): spawn_tball()
        if vball_delay <= 0:
            vball_delay = 10*random.randint(10, 30)
            for i in range(random.randint(2, 3)): spawn_vball()
        if laser_delay <= 0:
            laser_delay = 10*random.randint(20, 30)
            for i in range(random.randint(1, 1)): spawn_laser()
            if random.randint(1, 2) == 1: laser_delay = 10*10
        if log_delay <= 0:
            spawn_log()
            log_delay = 10*random.randint(30, 60)
            for i in range(random.randint(0, 0)): spawn_log()
            if random.randint(1, 2) == 1: log_delay = 10*10
        if bomb_delay <= 0:
            spawn_bomb()
            bomb_delay = 10*random.randint(100, 150)
    
    if game_level == 7:
        if ball_delay <= 0 and False:
            ball_delay = 10*random.randint(10, 20)
            for i in range(random.randint(1, 2)): spawn_ball()
        if tball_delay <= 0:
            tball_delay = 10*random.randint(50, 100)
            for i in range(random.randint(3, 4)): spawn_tball()
        if vball_delay <= 0 and False:
            vball_delay = 10*random.randint(10, 30)
            for i in range(random.randint(1, 2)): spawn_vball()
        if laser_delay <= 0:
            laser_delay = 10*random.randint(10, 10)
            for i in range(random.randint(1, 1)): spawn_laser()
        if log_delay <= 0:
            log_delay = 10*random.randint(50, 200)
            for i in range(random.randint(1, 1)): spawn_log()
            if random.randint(1, 5) == 1: log_delay = 10*20
        if bomb_delay <= 0:
            spawn_bomb()
            bomb_delay = 10*random.randint(180, 240)
    if game_level == 8:
        if ball_delay <= 0:
            ball_delay = 10*random.randint(1, 1)
            for i in range(random.randint(0, 0)): spawn_ball()
            if random.randint(1, 3) == 1: spawn_ball()
        if tball_delay <= 0 and False:
            tball_delay = 10*random.randint(50, 100)
            for i in range(random.randint(3, 4)): spawn_tball()
        if vball_delay <= 0 and False:
            vball_delay = 10*random.randint(50, 100)
            for i in range(random.randint(0, 1)): spawn_vball()
        if laser_delay <= 0 and False:
            laser_delay = 10*random.randint(1, 1)
            for i in range(random.randint(0, 0)): spawn_laser()
            if random.randint(1, 3) == 1: spawn_laser()
        if log_delay <= 0 and False:
            log_delay = 10*random.randint(50, 200)
            for i in range(random.randint(1, 1)): spawn_log()
        if bomb_delay <= 0:
            spawn_bomb()
            bomb_delay = 10*random.randint(160, 220)
    if game_level == 9:
        if ball_delay <= 0 and False:
            ball_delay = 10*random.randint(1, 1)
            for i in range(random.randint(0, 0)): spawn_ball()
            if random.randint(1, 3) == 1: spawn_ball()
        if tball_delay <= 0:
            tball_delay = 10*random.randint(20, 20)
            for i in range(random.randint(0, 0)): spawn_tball()
            if random.randint(1, 3) == 1: spawn_tball()
        if vball_delay <= 0:
            vball_delay = 10*random.randint(10, 10)
            for i in range(random.randint(0, 2)): spawn_vball()
        if laser_delay <= 0 and False:
            laser_delay = 10*random.randint(1, 1)
            for i in range(random.randint(0, 0)): spawn_laser()
            if random.randint(1, 3) == 1: spawn_laser()
        if log_delay <= 0:
            log_delay = 10*random.randint(40, 60)
            for i in range(random.randint(1, 1)): spawn_log()
            if random.randint(1, 4) == 1: log_delay = 10*20
        if bomb_delay <= 0:
            spawn_bomb()
            bomb_delay = 10*random.randint(120, 180)
    if game_level == 10:  # 보스맵
        if ball_delay <= 0 and False:
            ball_delay = 10*random.randint(1, 1)
            for i in range(random.randint(0, 0)): spawn_ball()
            if random.randint(1, 3) == 1: spawn_ball()
        if tball_delay <= 0 and False:
            tball_delay = 10*random.randint(50, 100)
            for i in range(random.randint(3, 4)): spawn_tball()
        if vball_delay <= 0 and False:
            vball_delay = 10*random.randint(50, 100)
            for i in range(random.randint(2, 3)): spawn_vball()
        if laser_delay <= 0:
            laser_delay = 10*random.randint(1, 1)
            for i in range(random.randint(0, 0)): spawn_laser()
            if random.randint(1, 7) == 1: spawn_laser()
        if log_delay <= 0:
            log_delay = 10*random.randint(10, 30)
            for i in range(random.randint(1, 1)): spawn_log()
            if random.randint(1, 5) == 1: log_delay = 10*1
        if bomb_delay <= 0:
            spawn_bomb()
            bomb_delay = 10*random.randint(30, 60)

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


def _try_add_enemy(enemy) -> bool:
    """겹치는 장애물이 없을 때만 생성 목록에 추가합니다."""
    candidate_rect = _get_enemy_spawn_rect(enemy)
    for existing_enemy in enemies:
        if existing_enemy.is_deleted():
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


def save_game_data() -> None:
    """진행률, 점수, 시도 횟수와 클리어 통계를 JSON에 저장합니다."""
    global save_dirty, last_save_time
    data = {
        "version": GAME_DATA_VERSION,
        "game_level": game_level,
        "score_record": score_record,
        "level_stats": level_stats
    }
    temp_path = f"{SAVE_FILE_PATH}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as save_file:
            json.dump(data, save_file, indent=4, ensure_ascii=False)
        os.replace(temp_path, SAVE_FILE_PATH)
    except (OSError, TypeError, ValueError) as error:
        print(f"게임 저장 중 오류가 발생했습니다: {error}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return
    save_dirty = False
    last_save_time = pygame.time.get_ticks()
    print("게임 기록을 저장했습니다.")


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

    loaded_level = data.get("game_level", 1)
    if isinstance(loaded_level, int) and not isinstance(loaded_level, bool):
        game_level = max(1, min(MAX_LEVEL, loaded_level))

    loaded_records = data.get("score_record", [])
    if isinstance(loaded_records, list):
        for index, record in enumerate(loaded_records[:MAX_LEVEL]):
            if isinstance(record, int) and not isinstance(record, bool):
                score_record[index] = max(0, min(100, record))
            elif isinstance(record, float) and math.isfinite(record):
                score_record[index] = max(0, min(100, record))

    loaded_stats = data.get("level_stats", [])
    if isinstance(loaded_stats, list):
        for index, stats in enumerate(loaded_stats[:MAX_LEVEL]):
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
bomb_delay = 0.0
pause = False
hit_count = [0, 0, 0, 0, 0]
hit_stack = False
music_endevent = pygame.USEREVENT + 1
should_restart = True
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
        bomb_delay = 0.0
        ball_delay = tball_delay = vball_delay = laser_delay = log_delay = 0
        hit_count = [0, 0, 0, 0, 0]
        hit_stack = False
        preview_spectrum = [0.0] * SPECTRUM_BAND_COUNT
        preview_onset = 0.0
        locked_preview_balls = []
        locked_preview_timer = 0.0
        locked_preview_index = 0
        transition_duration = 0.48
        transition_elapsed = transition_duration
        transition_switched = True
        menu_running = True
        start_game = False
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
                    # 테스트 시 F6으로 선택된 보스의 잠금 상태를 임시 전환합니다.
                    if event.key == pygame.K_F6:
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
                    bomb_delay = 0.0
                    ball_delay = tball_delay = vball_delay = laser_delay = log_delay = 0
                    preview_spectrum = [0.0] * SPECTRUM_BAND_COUNT
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
                bomb_delay = 0.0
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
            attack_blend = 1.0 - math.exp(-SPECTRUM_ATTACK_SPEED * delta_time)
            release_blend = 1.0 - math.exp(-SPECTRUM_RELEASE_SPEED * delta_time)
            for band, target in enumerate(preview_targets):
                blend = attack_blend if target > preview_spectrum[band] else release_blend
                preview_spectrum[band] += (target - preview_spectrum[band]) * blend
            preview_onset += (
                preview_onset_target / 255.0 - preview_onset
            ) * (1.0 - math.exp(-18.0 * delta_time))

            if not preview_locked:
                delay_step = 100.0 / tps
                ball_delay -= delay_step
                tball_delay -= delay_step
                vball_delay -= delay_step
                laser_delay -= delay_step
                log_delay -= delay_step
                bomb_delay -= delay_step
                spawn_enemies_by_level()

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
    bomb_delay = 0
    ball_delay = 0
    tball_delay = 0
    vball_delay = 0
    laser_delay = 0
    log_delay = 0

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
            attack_blend = 1.0 - math.exp(-SPECTRUM_ATTACK_SPEED * delta_time)
            release_blend = 1.0 - math.exp(-SPECTRUM_RELEASE_SPEED * delta_time)
            for band, target in enumerate(target_spectrum):
                blend = attack_blend if target > spectrum_levels[band] else release_blend
                spectrum_levels[band] += (target - spectrum_levels[band]) * blend
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
            player.update()
            player.draw()

            # 생성 대기 시간을 줄이고 적을 생성한 뒤 움직입니다.
            ball_delay -= 1/tps*100
            tball_delay -= 1/tps*100
            vball_delay -= 1/tps*100
            laser_delay -= 1/tps*100
            log_delay -= 1/tps*100
            bomb_delay -= 1/tps*100
            spawn_enemies_by_level()
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
pygame.quit()
