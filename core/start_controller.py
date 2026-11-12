import sys
import time

from ok import Handler, og
from ok import Logger
from ok.device.capture import BaseWindowsCaptureMethod, BrowserCaptureMethod
from ok.core.events import communicate
from ok.core.notifications import alert_error, alert_info
from ok.util.process import is_admin, execute, WINDOWS_START_METHOD_START

logger = Logger.get_logger(__name__)


class StartController:
    STARTED_WINDOW_MIN_SIZE = (100, 100)
    STARTED_WINDOW_STABLE_SECONDS = 5
    STARTED_WINDOW_POLL_INTERVAL = 0.2

    def __init__(self, app_config, exit_event):
        self.config = app_config
        self.exit_event = exit_event
        self.handler = Handler(exit_event, __name__)
        self.start_timeout = app_config.get('start_timeout', 60)
        windows_config = app_config.get('windows') or {}
        self.window_stable_seconds = windows_config.get(
            'window_stable_seconds', self.STARTED_WINDOW_STABLE_SECONDS)
        self.start_exe = windows_config.get('start_exe', True)
        self.start_method = windows_config.get('start_method', WINDOWS_START_METHOD_START)
        self.starting = False

    def tr(self, message):
        app = getattr(og, "app", None)
        return app.tr(message) if app is not None else message

    @staticmethod
    def _mark_task_enabled(task):
        if not task.enabled:
            task._enabled = True
            task.info_clear()
            task.executor.enqueue_onetime_task(task)
            logger.info(f"enabled task {task}")
        communicate.task.emit(task)

    def start(self, task=None, exit_after=False):
        self.starting = True
        try:
            self.handler.post(lambda: self.do_start(task, exit_after))
        except Exception:
            self.starting = False
            raise

    def do_start(self, task=None, exit_after=False):
        self.starting = True
        try:
            return self._do_start(task, exit_after)
        finally:
            self.starting = False

    def _do_start(self, task=None, exit_after=False):
        if (owner := getattr(getattr(og, 'executor', None), 'exclusive_owner', None)) is not None:
            logger.info(f'do_start refused, executor held by {owner}')
            communicate.starting_emulator.emit(
                True, self.tr('Cannot start: the app is controlled by {owner}').format(owner=owner), 0)
            return False
        communicate.starting_emulator.emit(False, None, self.start_timeout)
        tasks_to_enable = []
        try:
            if isinstance(task, int):
                task = og.executor.onetime_tasks[task]
                logger.info(f"enable param task {task}")

            if task and task.enabled and task.paused:
                logger.info(f"resume paused task {task}")
                if exit_after:
                    task.exit_after_task = True
                    communicate.task.emit(task)
                task.unpause()
                communicate.starting_emulator.emit(True, None, 0)
                return True

            if task and og.executor.current_task and og.executor.current_task != task:
                logger.info(f"queue task while another task is running {task}")
                if exit_after:
                    task.exit_after_task = True
                self._mark_task_enabled(task)
                if og.executor.paused:
                    og.executor.start()
                communicate.starting_emulator.emit(True, None, 0)
                return True
        except Exception as e:
            logger.error(f'do_start resume exception: {e}', e)
            communicate.starting_emulator.emit(True, self.tr('Start failed: {error}').format(error=e), 0)
            return False

        try:
            logger.info(f'do_start: call do_refresh {self.start_exe}')
            og.device_manager.do_refresh(True)
        except Exception as e:
            logger.error(f'do_start do_refresh exception: {e}', e)
            communicate.starting_emulator.emit(True, self.tr(str(e)), 0)
            return False

        try:
            if self.start_exe:
                if not self.start_device(initial_refresh_done=True):
                    return False
            else:
                logger.info('windows.start_exe is False, skip start_device')

            def add_task_to_enable(enable_task):
                if enable_task and enable_task not in tasks_to_enable:
                    tasks_to_enable.append(enable_task)

            for start_task in og.executor.get_all_tasks():
                if getattr(start_task, 'enable_after_start', False):
                    logger.info(f"enable_after_start task {start_task}")
                    add_task_to_enable(start_task)

            if task:
                add_task_to_enable(task)
                if exit_after:
                    task.exit_after_task = True

            for task in tasks_to_enable:
                self._mark_task_enabled(task)

            og.executor.start()
            communicate.starting_emulator.emit(True, None, 0)
            return True
        except Exception as e:
            logger.error(f'do_start exception: {e}', e)
            communicate.starting_emulator.emit(True, self.tr('Start failed: {error}').format(error=e), 0)
            return False

    def _wait_until_device_ready(self, refresh_first=True):
        wait_until = time.time() + self.start_timeout
        first_check = True
        while not self.exit_event.is_set():
            if refresh_first or not first_check:
                og.device_manager.do_refresh(True)
            first_check = False
            error = self.check_device_error()
            if error is None:
                return True
            logger.error(f'waiting for game to start error {error}')
            remaining_time = wait_until - time.time()
            if remaining_time <= 0:
                communicate.starting_emulator.emit(True, self.tr('Start game timeout!'), 0)
                return False
            communicate.starting_emulator.emit(False, None, int(remaining_time))
            time.sleep(2)
        return False

    def _wait_until_started_window_stable(self):
        wait_until = time.monotonic() + self.start_timeout
        stable_size = None
        stable_since = None
        min_width, min_height = self.STARTED_WINDOW_MIN_SIZE

        while not self.exit_event.is_set():
            hwnd_window = getattr(og.device_manager, 'hwnd_window', None)
            if hwnd_window is not None:
                hwnd_window.do_update_window_size()
                size = (hwnd_window.width, hwnd_window.height)
                if hwnd_window.hwnd and size[0] >= min_width and size[1] >= min_height:
                    now = time.monotonic()
                    if size != stable_size:
                        logger.info(f'waiting for started window to stabilize, current size {size[0]}x{size[1]}')
                        stable_size = size
                        stable_since = now
                    elif now - stable_since >= self.window_stable_seconds:
                        logger.info(f'started window size stable for {self.window_stable_seconds}s: {size[0]}x{size[1]}')
                        return True
                else:
                    stable_size = None
                    stable_since = None

            remaining_time = wait_until - time.monotonic()
            if remaining_time <= 0:
                communicate.starting_emulator.emit(True, self.tr('Start game timeout!'), 0)
                return False
            time.sleep(self.STARTED_WINDOW_POLL_INTERVAL)
        return False

    def _is_device_connected(self):
        device = og.device_manager.get_preferred_device()
        if not device or not device.get('connected'):
            return False
        capture_method = getattr(og.device_manager, 'capture_method', None)
        if capture_method is None or not capture_method.connected():
            return False
        return True

    def start_device(self, initial_refresh_done=False):
        if not self._is_device_connected():
            logger.info("Game not connected, attempting to connect up to 3 times...")
            for attempt in range(1, 4):
                if self.exit_event.is_set():
                    return False
                logger.info(f"Connecting to game, attempt {attempt}/3")
                try:
                    og.device_manager.do_refresh(True)
                except Exception as e:
                    logger.debug(f"do_refresh attempt {attempt} error: {e}")
                if self._is_device_connected():
                    logger.info(f"Connected to game on attempt {attempt}")
                    break
                if attempt < 3:
                    time.sleep(0.5)

        if not self._is_device_connected():
            error_msg = self.tr("Game is not running or game process not detected, please start the game first!")
            logger.error(f"start_device failed: {error_msg}")
            communicate.starting_emulator.emit(True, error_msg, 0)
            return False

        error = self.check_device_error()
        if error:
            logger.error(f"start_device check_device_error: {error}")
            communicate.starting_emulator.emit(True, error, 0)
            return False

        communicate.starting_emulator.emit(True, None, 0)
        return True

    def check_auto_hdr(self):
        pass

    def check_gpu_driver_post_processing(self):
        pass

    def check_resolution(self):
        error = None
        supported_resolution = self.config.get(
            'supported_resolution', {})
        supported_ratio = supported_resolution.get('ratio')
        min_size = supported_resolution.get('min_size')
        resize_to = supported_resolution.get('resize_to')
        force_ratio = supported_resolution.get('force_ratio')
        capture_method = og.device_manager.capture_method
        is_windows_capture = isinstance(capture_method, BaseWindowsCaptureMethod)
        auto_resize_enabled = (
            not is_windows_capture
            or og.global_config.get_config('Basic Options').get('Auto Resize Game Window', True)
        )
        supported, resolution = og.executor.check_frame_and_resolution(supported_ratio, min_size)
        if not supported:
            resize_success = False
            if resize_to and is_windows_capture and auto_resize_enabled:
                resize_success = capture_method.hwnd_window.try_resize_to(resize_to)
            if not resize_success:
                error = self.tr(
                    'Resolution {resolution} check failed, some tasks might not work correctly!').format(
                    resolution=resolution)
                if supported_ratio:
                    error += self.tr(', the supported ratio is {supported_ratio}').format(
                        supported_ratio=supported_ratio)
                if min_size:
                    error += self.tr(', the supported min resolution is {min_size}').format(
                        min_size=f'{min_size[0]}x{min_size[1]}')
        if error and not auto_resize_enabled:
            logger.info(f'check_resolution: {error}')
            alert_info(error)
            return None
        if force_ratio:
            return error
        elif error:
            alert_error(error, tray=True)

    def check_device_error(self):
        try:
            device = og.device_manager.get_preferred_device()
            error_msg = self.tr("{} is not connected, please select the game window.").format(
                device['nick'])
            logger.info(f'test check_device_error msg: {error_msg}')
            if not device:
                return self.tr('No game selected!')
            if og.device_manager.capture_method is None:
                return self.tr("Selected capture method is not supported by the game or your system!")
            if not og.device_manager.device_connected():
                logger.error(f'Emulator is not connected {og.device_manager.device}')
                return self.tr("Emulator is not connected, start the emulator first!")
            if isinstance(og.device_manager.capture_method,
                          BrowserCaptureMethod) and not og.device_manager.capture_method.connected():
                logger.info(f"start browser")
                og.device_manager.capture_method.start_browser()
            if not og.device_manager.capture_method.connected():
                logger.error(f'Game window is not connected {og.device_manager.capture_method}')
                # [LINUX-PORT-CRITICAL] Guide user when Vulkan capture is selected but game lacks OBS_VKCAPTURE=1
                from ok.device.capture_methods.linux_vulkan_capture import LinuxVulkanCaptureMethod
                if isinstance(og.device_manager.capture_method, LinuxVulkanCaptureMethod):
                    hwnd_window = getattr(og.device_manager.capture_method, 'hwnd_window', None)
                    if hwnd_window and getattr(hwnd_window, 'exists', False):
                        return self.tr("Game is running, but Vulkan capture layer is not active. Please launch the game with OBS_VKCAPTURE=1, or switch the Capture Method to X11_Direct.")
                return error_msg
            if isinstance(og.device_manager.capture_method, BaseWindowsCaptureMethod):

                if not og.device_manager.capture_method.hwnd_window.pos_valid:
                    hwnd_window = og.device_manager.capture_method.hwnd_window
                    if hwnd_window.hwnd and hwnd_window.window_width > 0 and hwnd_window.window_height > 0:
                        from ok.util.window import resize_window
                        logger.info(
                            f"Window pos invalid, trying to center window with size {hwnd_window.window_width}x{hwnd_window.window_height}")
                        resize_window(hwnd_window.hwnd, hwnd_window.window_width, hwnd_window.window_height)
                        hwnd_window.do_update_window_size()
                    if not og.device_manager.capture_method.hwnd_window.pos_valid:
                        return self.tr(
                            'Window is minimized or out of screen, and don\'t use full-screen exclusive mode!')
            frame = self.try_capture_a_frame()
            if frame is None:
                logger.error(f'check_device_error: try_capture_a_frame returned None')
                return self.tr('Capture failed, please check game window')
            logger.info(f'check_device_error: capturing frame {frame.shape[1], frame.shape[0]}')
            if og.executor.feature_set is not None:
                logger.info(f'check_device_error: checking feature_set size')
                if not og.executor.feature_set.check_size(frame):
                    logger.error(f'check_device_error: feature_set check_size failed')
                    return self.tr(
                        'Image resource load failed, please try install again.(Don\'t put the app in Downloads folder)')
            else:
                logger.info(f'check_device_error: feature_set is None')

            logger.info(f'check_device_error: checking resolution')
            resolution_error = self.check_resolution()
            if resolution_error:
                logger.error(f'check_device_error: resolution_error: {resolution_error}')
                return resolution_error

            if device and device['device'] == "adb" and self.config.get('adb'):
                started = og.device_manager.adb_ensure_in_front()
                if not started:
                    return self.tr("Can't start game, make sure the game is installed")
        except FileNotFoundError as e:
            raise e
        except Exception as e:
            logger.error(f'check_device_error exception: {str(e)}', e)
            return self.tr(str(e))

    @staticmethod
    def try_capture_a_frame():
        start = time.time()
        while True:
            # A running executor may own the capture; wait for it rather than
            # polling a lock it releases only briefly between frames.
            frame = og.device_manager.capture_method.get_frame(busy_wait=1)
            if frame is not None:
                return frame
            logger.info(f'try_capture_a_frame: frame is None, retrying...')
            if time.time() - start > 5:
                logger.error(f'time out try_capture_a_frame')
                return None
            time.sleep(0.1)
