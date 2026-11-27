"""Capture labels shared by the Qt and headless interfaces."""


def capture_method_label(method_name):
    return {
        'Vulkan': 'Vulkan - Shared-memory capture via obs-vkcapture (Recommended)',
        'X11_Direct': 'X11_Direct - X11 MIT-SHM direct window capture',
        'WGC': 'WGC - Fast, support HDR (not AutoHDR)',
        'WGC_HDR': 'WGC_HDR - Only use when using AutoHDR (Not Recommended)',
    }.get(method_name, method_name)
