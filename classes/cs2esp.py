import logging
import requests
import pymem
import pyMeow as overlay
from typing import Iterator, Optional, Dict
from classes.utils import read_vec3, read_string, read_floats, transliterate
from classes.config import Offsets, Colors, overlay_settings
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Constants for entity iteration
ENTITY_COUNT = 64
ENTITY_ENTRY_SIZE = 120

class Entity:
    """
    Represents a game entity with properties such as name, health, team, position, etc.
    """
    def __init__(self, controller_ptr: int, pawn_ptr: int, mem: pymem.Pymem) -> None:
        self.ptr = controller_ptr
        self.pawn_ptr = pawn_ptr
        self.mem = mem
        self.pos2d: Optional[Dict[str, float]] = None
        self.head_pos2d: Optional[Dict[str, float]] = None

    @property
    def name(self) -> str:
        original_name = read_string(self.mem, self.ptr + Offsets.m_iszPlayerName)
        return transliterate(original_name) if overlay_settings.use_transliteration else original_name

    @property
    def health(self) -> int:
        try:
            return self.mem.read_int(self.pawn_ptr + Offsets.m_iHealth)
        except Exception as e:
            logging.error("Failed to read health: %s", e)
            return 0

    @property
    def team(self) -> int:
        try:
            return self.mem.read_int(self.pawn_ptr + Offsets.m_iTeamNum)
        except Exception as e:
            logging.error("Failed to read team: %s", e)
            return -1

    @property
    def pos(self) -> Dict[str, float]:
        try:
            return read_vec3(self.mem, self.pawn_ptr + Offsets.m_vOldOrigin)
        except Exception as e:
            logging.error("Failed to read position: %s", e)
            return {"x": 0.0, "y": 0.0, "z": 0.0}

    @property
    def dormant(self) -> bool:
        try:
            return bool(self.mem.read_int(self.pawn_ptr + Offsets.m_bDormant))
        except Exception as e:
            logging.error("Failed to read dormant flag: %s", e)
            return True

    def bone_pos(self, bone: int) -> Dict[str, float]:
        try:
            game_scene = self.mem.read_longlong(self.pawn_ptr + Offsets.m_pGameSceneNode)
            bone_array_ptr = self.mem.read_longlong(game_scene + Offsets.m_pBoneArray)
            return read_vec3(self.mem, bone_array_ptr + bone * 32)
        except Exception as e:
            logging.error("Failed to get bone position for bone %d: %s", bone, e)
            return {"x": 0.0, "y": 0.0, "z": 0.0}

    @staticmethod
    def validate_screen_position(pos: Dict[str, float]) -> bool:
        screen_width = overlay.get_screen_width()
        screen_height = overlay.get_screen_height()
        return 0 <= pos["x"] <= screen_width and 0 <= pos["y"] <= screen_height

    def world_to_screen(self, view_matrix: list) -> bool:
        try:
            pos2d = overlay.world_to_screen(view_matrix, self.pos, 1)
            head2d = overlay.world_to_screen(view_matrix, self.bone_pos(6), 1)

            # Use the static method to validate the screen positions
            if not Entity.validate_screen_position(pos2d) or not Entity.validate_screen_position(head2d):
                logging.debug("Converted 2D position out of screen bounds: pos2d=%s, head2d=%s", pos2d, head2d)
                return False

            self.pos2d = pos2d
            self.head_pos2d = head2d
            return True
        except Exception as e:
            return False

class CS2Esp:
    """
    Core class that initializes memory reading, loads offsets,
    iterates over game entities, and renders the overlay.
    """
    def __init__(self) -> None:
        try:
            self.mem = pymem.Pymem("cs2.exe")
            client_module = pymem.process.module_from_name(self.mem.process_handle, "client.dll")
            self.mod = client_module.lpBaseOfDll
        except pymem.exception.ProcessNotFound:
            raise Exception("cs2.exe process not found.")
        except Exception as e:
            raise Exception(f"Error initializing pymem: {e}")

        self.running: bool = True
        self.load_offsets()

    def load_offsets(self) -> None:
        """
        Loads game offsets and field mappings from remote JSON resources.
        """
        try:
            # Use a session for improved performance and timeout handling
            with requests.Session() as session:
                offsets_url = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json"
                offsets_response = session.get(offsets_url, timeout=10)
                offsets_response.raise_for_status()
                offsets_data = offsets_response.json()

                # Load required offset keys
                keys = ["dwViewMatrix", "dwEntityList", "dwLocalPlayerController", "dwLocalPlayerPawn"]
                for key in keys:
                    setattr(Offsets, key, offsets_data["client.dll"].get(key))

                client_dll_url = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json"
                client_dll_response = session.get(client_dll_url, timeout=10)
                client_dll_response.raise_for_status()
                client_dll_data = client_dll_response.json()

                mapping = {
                    "m_iIDEntIndex": "C_CSPlayerPawnBase",
                    "m_hPlayerPawn": "CCSPlayerController",
                    "m_fFlags": "C_BaseEntity",
                    "m_iszPlayerName": "CBasePlayerController",
                    "m_iHealth": "C_BaseEntity",
                    "m_iTeamNum": "C_BaseEntity",
                    "m_vOldOrigin": "C_BasePlayerPawn",
                    "m_pGameSceneNode": "C_BaseEntity",
                    "m_bDormant": "CGameSceneNode",
                }
                for field, cls in mapping.items():
                    setattr(Offsets, field, client_dll_data["client.dll"]["classes"][cls]["fields"].get(field))
        except Exception as e:
            raise Exception(f"Error loading offsets: {e}")

    def iterate_entities(self) -> Iterator[Entity]:
        """
        Iterates over game entities and yields Entity objects.
        """
        try:
            ent_list_ptr = self.mem.read_longlong(self.mod + Offsets.dwEntityList)
            local_controller_ptr = self.mem.read_longlong(self.mod + Offsets.dwLocalPlayerController)
        except Exception as e:
            logging.error("Error reading entity list or local controller pointer: %s", e)
            return iter([])

        for i in range(1, ENTITY_COUNT + 1):
            try:
                list_index = (i & 0x7FFF) >> 9
                entity_index = i & 0x1FF
                entry_ptr = self.mem.read_longlong(ent_list_ptr + (8 * list_index) + 16)
                if not entry_ptr:
                    continue

                controller_ptr = self.mem.read_longlong(entry_ptr + ENTITY_ENTRY_SIZE * entity_index)
                if not controller_ptr or controller_ptr == local_controller_ptr:
                    continue

                controller_pawn_ptr = self.mem.read_longlong(controller_ptr + Offsets.m_hPlayerPawn)
                if not controller_pawn_ptr:
                    continue

                list_entry_ptr = self.mem.read_longlong(ent_list_ptr + 8 * ((controller_pawn_ptr & 0x7FFF) >> 9) + 16)
                if not list_entry_ptr:
                    continue

                pawn_ptr = self.mem.read_longlong(list_entry_ptr + ENTITY_ENTRY_SIZE * (controller_pawn_ptr & 0x1FF))
                if not pawn_ptr:
                    continue
            except Exception as e:
                logging.error("Error iterating entity %d: %s", i, e)
                continue

            yield Entity(controller_ptr, pawn_ptr, self.mem)

    def draw_entity(self, entity: Entity, view_matrix: list, is_teammate: bool = False) -> None:
        """
        Renders the ESP overlay for a given entity.
        """
        try:
            if not entity.world_to_screen(view_matrix):
                return
            if entity.health <= 0 or entity.dormant:
                return

            head_y = entity.head_pos2d["y"]
            pos_y = entity.pos2d["y"]
            box_height = pos_y - head_y
            box_width = box_height / 2
            half_width = box_width / 2

            outline_color = overlay.get_color(
                overlay_settings.teammate_color_hex if is_teammate else overlay_settings.box_color_hex
            )
            text_color = overlay.get_color(overlay_settings.text_color_hex)
            # Optionally draw snaplines
            if overlay_settings.draw_snaplines:
                screen_width = overlay.get_screen_width()
                screen_height = overlay.get_screen_height()
                overlay.draw_line(
                    screen_width / 2,
                    screen_height / 2,
                    entity.head_pos2d["x"],
                    entity.head_pos2d["y"],
                    overlay.get_color(overlay_settings.snaplines_color_hex),
                    2
                )

            # Draw the entity's bounding box
            overlay.draw_rectangle(
                entity.head_pos2d["x"] - half_width,
                entity.head_pos2d["y"] - half_width / 2,
                box_width,
                box_height + half_width / 2,
                Colors.grey
            )
            overlay.draw_rectangle_lines(
                entity.head_pos2d["x"] - half_width,
                entity.head_pos2d["y"] - half_width / 2,
                box_width,
                box_height + half_width / 2,
                outline_color,
                overlay_settings.box_line_thickness
            )

            # Draw the entity's nickname above the box
            nickname = entity.name
            nickname_font_size = 10
            nickname_width = overlay.measure_text(nickname, nickname_font_size)
            overlay.draw_text(
                nickname,
                entity.head_pos2d["x"] - nickname_width // 2,
                entity.head_pos2d["y"] - half_width / 2 - 15,
                nickname_font_size,
                text_color
            )

            # Draw the vertical health bar to the left of the bounding box
            bar_width = 4
            bar_margin = 2
            bar_x = entity.head_pos2d["x"] - half_width - bar_width - bar_margin
            bar_y = entity.head_pos2d["y"] - half_width / 2
            bar_height = box_height + half_width / 2
            overlay.draw_rectangle(
                bar_x,
                bar_y,
                bar_width,
                bar_height,
                overlay.get_color("black")
            )
            health_percent = max(0, min(entity.health, 100))
            fill_height = (health_percent / 100.0) * bar_height
            if health_percent <= 20:
                fill_color = overlay.get_color("red")
            elif health_percent <= 50:
                fill_color = overlay.get_color("yellow")
            else:
                fill_color = overlay.get_color("green")
            fill_y = bar_y + (bar_height - fill_height)
            overlay.draw_rectangle(
                bar_x,
                fill_y,
                bar_width,
                fill_height,
                fill_color
            )
            # Optionally draw health numbers
            if getattr(overlay_settings, 'draw_health_numbers', False):
                health_text = f"{entity.health}"
                overlay.draw_text(
                    health_text,
                    int(bar_x - 25),
                    int(bar_y + bar_height / 2 - 5),
                    10,
                    text_color
                )
        except Exception as e:
            logging.error("Error drawing entity: %s", e)

    def run(self) -> None:
        """
        Main loop that initializes the overlay and updates entity ESP.
        """
        try:
            overlay.overlay_init("Counter-Strike 2", fps=144)
        except Exception as e:
            raise Exception(f"Overlay initialization error: {e}")

        try:
            while self.running and overlay.overlay_loop():
                try:
                    view_matrix = read_floats(self.mem, self.mod + Offsets.dwViewMatrix, 16)
                except Exception as e:
                    logging.error("Error reading view matrix: %s", e)
                    continue

                # Get the local player's team
                local_team: Optional[int] = None
                try:
                    local_pawn_ptr = self.mem.read_longlong(self.mod + Offsets.dwLocalPlayerPawn)
                    if local_pawn_ptr:
                        local_team = self.mem.read_int(local_pawn_ptr + Offsets.m_iTeamNum)
                except Exception as e:
                    logging.error("Error reading local team: %s", e)

                overlay.begin_drawing()
                overlay.draw_fps(0, 0)
                for entity in self.iterate_entities():
                    try:
                        # Determine if the entity is a teammate and skip if not drawing teammates.
                        is_teammate = False
                        if local_team is not None and entity.team == local_team:
                            if not overlay_settings.draw_teammates:
                                continue
                            is_teammate = True
                        self.draw_entity(entity, view_matrix, is_teammate)
                    except Exception as e:
                        logging.error("Error processing an entity: %s", e)
                        continue
                overlay.end_drawing()
        except Exception as e:
            logging.error("Error in overlay loop: %s", e)
            raise Exception(f"Overlay error: {e}")
        finally:
            overlay.overlay_close()
            logging.info("Overlay loop ended.")

    def stop(self) -> None:
        """Stops the overlay loop."""
        self.running = False

class OverlayWorker(QObject):
    """
    A Qt worker class for running the CS2 ESP overlay in a separate thread.
    """
    finished = pyqtSignal()
    errorOccurred = pyqtSignal(str)

    @pyqtSlot()
    def run(self) -> None:
        try:
            self.esp = CS2Esp()
        except Exception as e:
            self.errorOccurred.emit(f"Initialization error: {e}")
            self.finished.emit()
            return

        try:
            self.esp.run()
        except Exception as e:
            self.errorOccurred.emit(f"Runtime error: {e}")
        finally:
            self.finished.emit()

    @pyqtSlot()
    def stop(self) -> None:
        if hasattr(self, 'esp') and self.esp:
            self.esp.stop()