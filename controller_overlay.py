from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

# SDL normally stops sending joystick events while another application has
# focus.  Set this before pygame initializes SDL so the overlay can continue
# polling the controller in the background.
os.environ.setdefault("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1")

try:
    import pygame
except ImportError:
    print("pygame is required. Install it with: py -m pip install pygame", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parent
SETTINGS_FILE = ROOT / "gp2040_settings.json"
PANEL_W, PANEL_H = 640, 360

DEFAULT_LABELS = {
    "back": "LS", "left": "L", "down": "D", "right": "R", "ls": "M2",
    "lb": "LB", "up1": "U", "up2": "M1", "lt": "LT", "x": "X",
    "y": "Y", "rb": "RB", "a": "A", "b": "B", "rt": "RT", "rs": "RS",
}

# key, x, y, width, height, shape, rotation (same coordinates as layout.js)
BUTTON_LAYOUT = [
    ("back", 30, 120, 52, 86, "pill", 0),
    ("left", 96, 120, 50, 50, "circle", 0),
    ("down", 156, 120, 50, 50, "circle", 0),
    ("right", 216, 140, 50, 50, "circle", 0),
    ("ls", 280, 150, 52, 52, "circle", 0),
    ("lb", 205, 236, 50, 50, "circle", 0),
    ("up1", 270, 236, 64, 82, "pill", -15),
    ("up2", 342, 236, 64, 82, "pill", 15),
    ("lt", 414, 236, 50, 50, "circle", 0),
    ("x", 356, 125, 46, 46, "circle", 0),
    ("y", 408, 98, 46, 46, "circle", 0),
    ("rb", 460, 84, 46, 46, "circle", 0),
    ("a", 370, 178, 46, 46, "circle", 0),
    ("b", 422, 150, 46, 46, "circle", 0),
    ("rt", 474, 132, 46, 46, "circle", 0),
    ("rs", 536, 120, 52, 86, "pill", 0),
]

# GP2040, XInput, and SDL button numbering differ slightly. Each tuple is an
# accepted raw button index; accepting both layouts keeps LT/RT/LS/RS/D-pad
# usable across GP2040 firmware and pygame's SDL mapping.
BUTTON_MAP = {
    "a": (0,), 
    "b": (1,),
    "x": (2,), 
    "y": (3,), 
    "lb": (4,), 
    "rb": (5,),
    "lt": (6,), 
    "rt": (7,),
    "back": (8,), 
    "ls": (9,), 
    "rs":(9,),
    "up2": (8,),
    "up1": (11, 12), 
    "down": (12, 13), 
    "left": (13, 14), 
    "right": (14, 15),
}


def load_settings() -> dict[str, Any]:
    defaults = {"labels": dict(DEFAULT_LABELS), "bg": "", "bg_x": 0, "bg_y": 0, "bg_scale": 1.0}
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        defaults.update(data if isinstance(data, dict) else {})
        labels = dict(DEFAULT_LABELS)
        labels.update(defaults.get("labels", {}))
        defaults["labels"] = labels
    except (OSError, ValueError, TypeError):
        pass
    return defaults


def save_settings(settings: dict[str, Any]) -> None:
    try:
        SETTINGS_FILE.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"設定を保存できません: {exc}")


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    for name in ("Meiryo", "Yu Gothic", "Noto Sans CJK JP", "Arial"):
        font = pygame.font.SysFont(name, size, bold=bold)
        if font:
            return font
    return pygame.font.Font(None, size)


def ask_text(title: str, initial: str) -> str | None:
    """Use the standard-library Tk dialog only while editing a label."""
    try:
        import tkinter as tk
        from tkinter import simpledialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        value = simpledialog.askstring(title, "ボタン名:", initialvalue=initial, parent=root)
        root.destroy()
        return value
    except Exception:
        return None


def choose_background() -> str | None:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        value = filedialog.askopenfilename(
            title="背景画像を選択",
            filetypes=[("画像", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"), ("すべて", "*.*")],
        )
        root.destroy()
        return value or None
    except Exception:
        return None


def load_image(path: str | Path | None) -> pygame.Surface | None:
    if not path:
        return None
    try:
        return pygame.image.load(str(path)).convert_alpha()
    except (pygame.error, OSError):
        return None


def read_joysticks() -> list[pygame.joystick.Joystick]:
    result = []
    for index in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(index)
        joystick.init()
        result.append(joystick)
    return result


def safe_button(joystick: pygame.joystick.Joystick, index: int) -> bool:
    try:
        return index < joystick.get_numbuttons() and bool(joystick.get_button(index))
    except pygame.error:
        return False


def safe_buttons(joystick: pygame.joystick.Joystick, indices: tuple[int, ...]) -> bool:
    return any(safe_button(joystick, index) for index in indices)


def safe_axis(joystick: pygame.joystick.Joystick, index: int) -> float:
    try:
        return float(joystick.get_axis(index)) if index < joystick.get_numaxes() else 0.0
    except pygame.error:
        return 0.0


def trigger_pressed(joystick: pygame.joystick.Joystick, axis_index: int) -> bool:
    """Handle SDL triggers whose idle value is either 0.0 or -1.0."""
    value = safe_axis(joystick, axis_index)
    if abs(value + 1.0) < 0.25:
        return value > -0.25
    if abs(value) < 0.25:
        return value > 0.5
    return value > 0.2


def hat_value(joystick: pygame.joystick.Joystick) -> tuple[int, int]:
    try:
        return joystick.get_hat(0) if joystick.get_numhats() else (0, 0)
    except pygame.error:
        return (0, 0)


def raw_input_signature(joystick: pygame.joystick.Joystick) -> tuple[tuple[int, ...], tuple[float, ...], tuple[int, int]]:
    """Return raw SDL input values for mapping controllers with custom firmware."""
    buttons = tuple(index for index in range(joystick.get_numbuttons()) if safe_button(joystick, index))
    axes = tuple(round(safe_axis(joystick, index), 2) for index in range(joystick.get_numaxes()))
    return buttons, axes, hat_value(joystick)


def pressed_states(joystick: pygame.joystick.Joystick) -> dict[str, bool]:
    states = {key: safe_buttons(joystick, indices) for key, indices in BUTTON_MAP.items()}
    axis_x, axis_y = safe_axis(joystick, 0), safe_axis(joystick, 1)
    hat_x, hat_y = hat_value(joystick)
    states["left"] |= axis_x < -0.5
    states["right"] |= axis_x > 0.5
    states["up1"] |= axis_y < -0.5 or hat_y > 0
    states["down"] |= axis_y > 0.5 or hat_y < 0
    states["left"] |= hat_x < 0
    states["right"] |= hat_x > 0
    states["lt"] |= trigger_pressed(joystick, 4)
    states["rt"] |= trigger_pressed(joystick, 5)
    return states


def transformed_background(image: pygame.Surface, settings: dict[str, Any]) -> tuple[pygame.Surface, tuple[int, int]]:
    scale = max(0.1, min(10.0, float(settings.get("bg_scale", 1.0))))
    fit = min(PANEL_W / image.get_width(), PANEL_H / image.get_height())
    size = (max(1, round(image.get_width() * fit * scale)), max(1, round(image.get_height() * fit * scale)))
    return pygame.transform.smoothscale(image, size), (int(settings.get("bg_x", 0)), int(settings.get("bg_y", 0)))


def rounded_button(surface: pygame.Surface, rect: pygame.Rect, shape: str, angle: int, pressed: bool, label: str, font: pygame.font.Font, edit: bool) -> None:
    if shape == "circle":
        radius = min(rect.width, rect.height) // 2
        center = rect.center
        fill = (38, 130, 220) if pressed else (30, 41, 59)
        edge = (125, 211, 252) if pressed else ((245, 158, 11) if edit else (145, 165, 185))
        pygame.draw.circle(surface, fill, center, radius)
        pygame.draw.circle(surface, edge, center, radius, 2)
    else:
        pad = 2
        button = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        fill = (38, 130, 220, 245) if pressed else (30, 41, 59, 210)
        edge = (125, 211, 252, 255) if pressed else ((245, 158, 11, 255) if edit else (145, 165, 185, 220))
        pygame.draw.rect(button, fill, button.get_rect(), border_radius=24)
        pygame.draw.rect(button, edge, button.get_rect().inflate(-pad * 2, -pad * 2), 2, border_radius=22)
        if angle:
            button = pygame.transform.rotate(button, angle)
        surface.blit(button, button.get_rect(center=rect.center))
    text = font.render(label, True, (240, 248, 255))
    surface.blit(text, text.get_rect(center=rect.center))


def draw_panel(screen: pygame.Surface, joystick: pygame.joystick.Joystick | None, settings: dict[str, Any], edit_mode: bool, bg_mode: bool, background: pygame.Surface | None, font: pygame.font.Font) -> dict[str, pygame.Rect]:
    panel = pygame.Rect(0, 0, PANEL_W, PANEL_H)
    pygame.draw.rect(screen, (9, 10, 15), panel, border_radius=30)
    pygame.draw.rect(screen, (20, 25, 35), panel.inflate(-2, -2), border_radius=28)

    if background:
        image, pos = transformed_background(background, settings)
        image.set_alpha(165 if not bg_mode else 110)
        screen.blit(image, (PANEL_W // 2 - image.get_width() // 2 + pos[0], PANEL_H // 2 - image.get_height() // 2 + pos[1]))

    states = pressed_states(joystick) if joystick else {}
    hitboxes: dict[str, pygame.Rect] = {}
    for key, x, y, width, height, shape, angle in BUTTON_LAYOUT:
        rect = pygame.Rect(x, y, width, height)
        hitboxes[key] = rect
        rounded_button(screen, rect, shape, angle, states.get(key, False), str(settings["labels"].get(key, DEFAULT_LABELS[key])), font, edit_mode)
    if bg_mode:
        pygame.draw.rect(screen, (56, 189, 248), panel, 3, border_radius=30)
    return hitboxes


def draw_toolbar(screen: pygame.Surface, text: str, font: pygame.font.Font, edit_mode: bool, bg_mode: bool) -> None:
    pygame.draw.rect(screen, (15, 23, 42), (0, 0, screen.get_width(), 62))
    title = font.render("GP2040-CE Python Controller", True, (226, 232, 240))
    screen.blit(title, (16, 8))
    help_text = "F2:配置名  F3:背景編集  B:背景選択  R:リセット  ESC:終了"
    screen.blit(font.render(help_text, True, (148, 163, 184)), (16, 34))
    status = font.render(text, True, (52, 211, 153) if text else (244, 63, 94))
    screen.blit(status, (screen.get_width() - status.get_width() - 16, 15))
    if edit_mode:
        screen.blit(font.render("配置名変更 ON", True, (251, 191, 36)), (screen.get_width() - 150, 38))
    elif bg_mode:
        screen.blit(font.render("背景編集 ON", True, (56, 189, 248)), (screen.get_width() - 145, 38))


def controller_selection(screen: pygame.Surface, joysticks: list[pygame.joystick.Joystick], title_font: pygame.font.Font, font: pygame.font.Font, clock: pygame.time.Clock) -> int | None:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                y = 140
                for index, _joystick in enumerate(joysticks):
                    if pygame.Rect(120, y, 560, 44).collidepoint(event.pos):
                        return index
                    y += 58
        screen.fill((9, 10, 15))
        screen.blit(title_font.render("使用するコントローラーを選択してください", True, (56, 189, 248)), (120, 70))
        if not joysticks:
            screen.blit(font.render("コントローラーが見つかりません。接続後に再起動してください。", True, (251, 113, 133)), (120, 140))
        else:
            y = 140
            for index, joystick in enumerate(joysticks):
                rect = pygame.Rect(120, y, 560, 44)
                pygame.draw.rect(screen, (30, 41, 59), rect, border_radius=10)
                pygame.draw.rect(screen, (71, 85, 105), rect, 2, border_radius=10)
                screen.blit(font.render(f"[{index}] {joystick.get_name()}", True, (226, 232, 240)), (138, y + 12))
                y += 58
        pygame.display.flip()
        clock.tick(30)


def run(args: argparse.Namespace) -> None:
    pygame.init()
    pygame.joystick.init()
    settings = load_settings()
    joysticks = read_joysticks()
    # Background mode keeps the pygame loop alive without showing the
    # controller-selection screen.  This is useful when launching the script
    # with pythonw.exe or from a startup task while OBS captures the window.
    obs_mode = args.obs or args.background
    selected = args.controller_index if args.controller_index is not None else (0 if obs_mode and joysticks else None)
    if selected is not None and not (0 <= selected < len(joysticks)):
        selected = None

    window_size = (PANEL_W, PANEL_H) if obs_mode else (760, 500)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("GP2040-CE Python Controller Overlay")
    clock = pygame.time.Clock()
    title_font, font, small_font = get_font(18, True), get_font(14), get_font(11)
    background_path = settings.get("bg") or (str(ROOT / "controller-bg.png") if (ROOT / "controller-bg.png").exists() else "")
    background = load_image(background_path)
    edit_mode = False
    bg_mode = False
    dragging = False
    drag_start = (0, 0)
    config_dirty = False
    last_raw_signature = None
    panel_x = 0 if obs_mode else (screen.get_width() - PANEL_W) // 2
    panel_y = 0 if obs_mode else 78

    try:
        if not obs_mode and selected is None:
            selected = controller_selection(screen, joysticks, title_font, font, clock)
            if selected is None:
                return
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type in (getattr(pygame, "JOYDEVICEADDED", -1), getattr(pygame, "JOYDEVICEREMOVED", -2)):
                    joysticks = read_joysticks()
                    if selected is not None and selected >= len(joysticks):
                        selected = None
                    if obs_mode and selected is None and joysticks:
                        selected = 0
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if obs_mode:
                            return
                        selected = None
                    elif event.key == pygame.K_F2 and not obs_mode:
                        edit_mode = not edit_mode
                    elif event.key == pygame.K_F3 and not obs_mode:
                        bg_mode = not bg_mode
                    elif event.key == pygame.K_b and not obs_mode:
                        chosen = choose_background()
                        if chosen:
                            background_path = chosen
                            background = load_image(chosen)
                            settings["bg"] = chosen
                            config_dirty = True
                    elif event.key == pygame.K_r and not obs_mode:
                        settings.update({"bg_x": 0, "bg_y": 0, "bg_scale": 1.0})
                        config_dirty = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    local_pos = (event.pos[0] - panel_x, event.pos[1] - panel_y)
                    if bg_mode and event.button == 1:
                        dragging = True
                        drag_start = (local_pos[0] - int(settings.get("bg_x", 0)), local_pos[1] - int(settings.get("bg_y", 0)))
                    elif bg_mode and event.button in (4, 5):
                        settings["bg_scale"] = round(max(0.1, min(10.0, float(settings.get("bg_scale", 1.0)) + (0.08 if event.button == 4 else -0.08))), 3)
                        config_dirty = True
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging = False
                if event.type == pygame.MOUSEMOTION and dragging and bg_mode:
                    local_pos = (event.pos[0] - panel_x, event.pos[1] - panel_y)
                    settings["bg_x"] = local_pos[0] - drag_start[0]
                    settings["bg_y"] = local_pos[1] - drag_start[1]
                    config_dirty = True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and edit_mode:
                    local_pos = (event.pos[0] - panel_x, event.pos[1] - panel_y)
                    for key, x, y, width, height, _shape, _angle in BUTTON_LAYOUT:
                        if pygame.Rect(x, y, width, height).collidepoint(local_pos):
                            value = ask_text("ボタン名を変更", str(settings["labels"].get(key, DEFAULT_LABELS[key])))
                            if value is not None:
                                settings["labels"][key] = value
                                config_dirty = True
                            break

            if selected is None and not obs_mode:
                selected = controller_selection(screen, joysticks, title_font, font, clock)
                if selected is None:
                    return
            joystick = joysticks[selected] if selected is not None and selected < len(joysticks) else None
            if args.debug_input and joystick is not None:
                signature = raw_input_signature(joystick)
                if signature != last_raw_signature:
                    print(f"[入力診断] buttons={signature[0]} axes={signature[1]} hat={signature[2]}", flush=True)
                    last_raw_signature = signature
            if config_dirty:
                save_settings(settings)
                config_dirty = False

            screen.fill((9, 10, 15))
            if obs_mode:
                draw_panel(screen, joystick, settings, False, False, background, font)
            else:
                draw_toolbar(screen, joystick.get_name() if joystick else "未接続", small_font, edit_mode, bg_mode)
                panel = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
                draw_panel(panel, joystick, settings, edit_mode, bg_mode, background, font)
                screen.blit(panel, (panel_x, panel_y))
            pygame.display.flip()
            clock.tick(60)
    finally:
        for joystick in joysticks:
            try:
                joystick.quit()
            except pygame.error:
                pass
        pygame.quit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Python-only GP2040 controller overlay for OBS")
    parser.add_argument("--obs", action="store_true", help="640x360 overlay-only mode for OBS Window Capture")
    parser.add_argument(
        "--background",
        action="store_true",
        help="start without the controller-selection screen; safe to run in the background",
    )
    parser.add_argument("--controller-index", type=int, default=None, help="controller index for --obs mode")
    parser.add_argument("--debug-input", action="store_true", help="print raw pygame button/axis/hat values")
    run(parser.parse_args())


if __name__ == "__main__":
    main()
