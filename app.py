import flet as ft
import os
import subprocess
import json
import subprocess
import psutil

HYPRLAND_CONF = os.path.expanduser("~/.config/hypr/hyprland.conf")

def main(page: ft.Page):
    page.title = "Wallpaler Engine GUI"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.window_width = 800
    page.window_height = 600

    current_dir = os.path.expanduser("~/.steam/steam/steamapps/workshop/content/431960")
    path_text = ft.Text(value=current_dir, size=16, weight=ft.FontWeight.BOLD)
    file_list = ft.ListView(expand=True, spacing=10, padding=10)

    def get_preview_image(folder_path):
        try:
            for f in os.listdir(folder_path):
                if f.lower().endswith((".png", ".jpg", ".jpeg")):
                    return os.path.join(folder_path, f)
        except Exception:
            pass
        return None

    def update_hyprland_conf(folder_id):
        """Меняет команду в hyprland.conf"""
        try:
            if not os.path.exists(HYPRLAND_CONF):
                print(f"Файл {HYPRLAND_CONF} не найден!")
                return
            with open(HYPRLAND_CONF, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            found = False
            for line in lines:
                if line.strip().startswith("exec-once") and "linux-wallpaperengine" in line:
                    new_lines.append(f"exec-once = linux-wallpaperengine --silent --screen-root HDMI-A-2 {folder_id}\n")
                    found = True
                else:
                    new_lines.append(line)

            if not found:
                # Если строки нет — добавляем в конец
                new_lines.append(f"\nexec-once = linux-wallpaperengine --silent --screen-root HDMI-A-2 {folder_id}\n")

            with open(HYPRLAND_CONF, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            print(f"Hyprland конфиг обновлён для {folder_id}")

        except Exception as e:
            print(f"Ошибка обновления hyprland.conf: {e}")
        
    def get_primary_monitor():
        try:
            output = subprocess.check_output(["hyprctl", "monitors", "-j"])
            monitors = json.loads(output)
            # Можно выбрать первый активный монитор или искать primary
            if monitors:
                return monitors[0]["name"]
        except Exception as e:
            print(f"Ошибка получения монитора: {e}")
        return "HDMI-A-2"  # fallback


    def kill_wallpaperengine():
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'linux-wallpaperengine':
                proc.kill()

    def set_wallpaper(folder_id):
        try:
            kill_wallpaperengine()  # завершить старые процессы
            monitor = get_primary_monitor()
            subprocess.Popen([
                "linux-wallpaperengine",
                "--silent",
                "--screen-root", monitor,
                str(folder_id)
            ])
            update_hyprland_conf(folder_id)
            print(f"Запущен wallpaperengine для {folder_id} на {monitor}")
        except Exception as e:
            print(f"Ошибка запуска: {e}")

    def load_folders():
        file_list.controls.clear()
        try:
            for item in os.listdir(current_dir):
                full_path = os.path.join(current_dir, item)
                if os.path.isdir(full_path):
                    preview = get_preview_image(full_path)
                    img_src = preview if preview else "folder_icon.png"

                    file_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Image(src=img_src, width=60, height=60, fit=ft.ImageFit.COVER),
                                ft.Text(item, size=16)
                            ]),
                            on_click=lambda e, folder=item: set_wallpaper(folder)
                        )
                    )
        except FileNotFoundError:
            file_list.controls.append(ft.Text("Папка не найдена", color=ft.colors.RED))
        page.update()

    load_folders()

    page.add(ft.Column([
        path_text,
        file_list
    ], expand=True))

if __name__ == "__main__":
    ft.app(target=main)
