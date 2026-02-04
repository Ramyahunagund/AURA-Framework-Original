# core/scraper.py

import os
import io
import time
from datetime import datetime
from PIL import Image, ImageChops
from core.settings import framework_logger, Constants
from core.utils import (
    save_full_page_screenshot,
    take_element_handle_screenshot,
    load_or_create_workbook,
    write_excel_context,
    hash_text,
    ensure_dirs,
    extract_animated_svgs,
    extract_animated_gifs,
    extract_animated_visuals
)

EXTRA_WAIT = 3
SAVE_ONLY_GIF_FROM_SVG = True

def get_semantic_type(tag, href, onclick):
    tag_upper = tag.upper()
    if tag_upper.startswith("H") and len(tag_upper) == 2 and tag_upper[1].isdigit():
        return "Heading"
    if tag_upper == "A" and href:
        return "Link"
    if tag_upper == "BUTTON" or onclick:
        return "Button"
    if tag_upper in ("INPUT", "SELECT", "TEXTAREA"):
        return "FormControl"
    if tag_upper == "LABEL":
        return "Label"
    if tag_upper == "IMG":
        return "Image"
    return tag_upper.title()

def scrape_context(
    flow_name,
    context_name,
    page,
    excel_path,
    output_dir,
    screenshot_only=False,
    sub_context=None,
    lang_code=None,
    animations=False,
    target_dir=None
):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    screenshot_dir = os.path.join(output_dir, "screenshots")
    ensure_dirs(screenshot_dir)
    subctx_suffix = f"_{sub_context}" if sub_context else ""
    fullpage_shot_name = save_full_page_screenshot(page, flow_name, f"{context_name}{subctx_suffix}_full_page", screenshot_dir)
    elements = []
    seen = set()
    elements.append({
        "Context": context_name,
        "SubContext": sub_context or "",
        "PageURL": page.url if hasattr(page, 'url') else "",
        "Timestamp": timestamp,
        "Type": "FullPage",
        # "Role": "",
        "Tag": "",
        "Text": "",
        "Href": "",
        # "OnClick": "",
        # "X": 0,
        # "Y": 0,
        # "Width": 0,
        # "Height": 0,
        # "Font": "",
        # "FontSize": "",
        # "FontWeight": "",
        # "Color": "",
        # "BgColor": "",
        "Screenshot": fullpage_shot_name,
        "ExcludeRegions": ""
    })
    if screenshot_only:
        wb, _ = load_or_create_workbook(excel_path, Constants.SCRAPE_HEADERS)
        write_excel_context(elements, wb, context_name, excel_path, Constants.SCRAPE_HEADERS)
        framework_logger.info(
            f"[SCRAPER] Screenshot-only mode: Saved full-page screenshot for {flow_name}/{context_name}{subctx_suffix} as {fullpage_shot_name} and logged row."
        )
        return
    handles = page.query_selector_all("body *")
    for idx, handle in enumerate(handles):
        try:
            tag = handle.evaluate("el => el.tagName")
            if tag is None or tag.upper() in Constants.IGNORE_TAGS:
                continue
            if not handle.is_visible():
                continue
            text = handle.inner_text().strip()
            if not text:
                continue
            box = handle.bounding_box()
            if not box or box['width'] == 0 or box['height'] == 0:
                continue
            # role = handle.get_attribute("role") or ""
            href = handle.get_attribute("href") or ""
            onclick = handle.get_attribute("onclick") or ""
            # font = handle.evaluate("el => getComputedStyle(el).fontFamily")
            # font_size = handle.evaluate("el => getComputedStyle(el).fontSize")
            # font_weight = handle.evaluate("el => getComputedStyle(el).fontWeight")
            # color = handle.evaluate("el => getComputedStyle(el).color")
            # bg_color = handle.evaluate("el => getComputedStyle(el).backgroundColor")
            semantic_type = get_semantic_type(tag, href, onclick)
            dedup_key = (sub_context or "", text, tag, href)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            fname = f"{context_name}{subctx_suffix}_{lang_code}_{idx:04d}_{semantic_type}_{hash_text(text)}.png"
            shot_path = os.path.join(screenshot_dir, fname)
            shot_ok = take_element_handle_screenshot(handle, shot_path)
            elements.append({
                "Context": context_name,
                "SubContext": sub_context or "",
                "PageURL": page.url if hasattr(page, 'url') else "",
                "Timestamp": timestamp,
                "Type": semantic_type,
                # "Role": role,
                "Tag": tag,
                "Text": text,
                "Href": href,
                # "OnClick": onclick,
                # "X": box['x'],
                # "Y": box['y'],
                # "Width": box['width'],
                # "Height": box['height'],
                # "Font": font,
                # "FontSize": font_size,
                # "FontWeight": font_weight,
                # "Color": color,
                # "BgColor": bg_color,
                "Screenshot": fname if shot_ok else "",
                "ExcludeRegions": ""
            })
        except Exception as e:
            if ("Node is not anHTMLElement" not in str(e)) and ("Node is not an HTMLElement" not in str(e)):
                framework_logger.debug(f"[SCRAPER] Failed to scrape element {idx} in context '{context_name}': {e}")
            continue

    if animations:
        animation_dir = os.path.join(output_dir, "animations")
        os.makedirs(animation_dir, exist_ok=True)

        svg_animations = extract_animated_svgs(page)
        for svg_info in svg_animations:
            svg_xml = svg_info["outer_html"]
            svg_hash = hash_text(svg_xml)
            svg_filename = f"{context_name}{subctx_suffix}_svg_{svg_hash}.svg"
            svg_path = os.path.join(animation_dir, svg_filename)
            gif_bytes = svg_info.get("gif_bytes")
            gif_filename = f"{context_name}{subctx_suffix}_svg_{svg_hash}.gif"
            gif_path = os.path.join(animation_dir, gif_filename)

            # -- Only GIF row (if toggle True), or both rows (if False) --
            if gif_bytes:
                with open(gif_path, "wb") as f:
                    f.write(gif_bytes)
                framework_logger.info(f"Animated SVG GIF saved at {gif_path}")
                elements.append({
                    "Context": context_name,
                    "SubContext": sub_context or "",
                    "PageURL": page.url if hasattr(page, 'url') else "",
                    "Timestamp": timestamp,
                    "Type": "Animation",
                    "Tag": "gif",
                    "Text": "",
                    "Href": "",
                    "Screenshot": gif_filename,
                    "ExcludeRegions": ""
                })
            if not SAVE_ONLY_GIF_FROM_SVG:
                with open(svg_path, "w", encoding="utf-8") as f:
                    f.write(svg_xml)
                framework_logger.info(f"Animated SVG saved at {svg_path}")
                elements.append({
                    "Context": context_name,
                    "SubContext": sub_context or "",
                    "PageURL": page.url if hasattr(page, 'url') else "",
                    "Timestamp": timestamp,
                    "Type": "Animation",
                    "Tag": "svg",
                    "Text": "",
                    "Href": "",
                    "Screenshot": svg_filename,
                    "ExcludeRegions": ""
                })

        gif_animations = extract_animated_gifs(page)
        for gif_info in gif_animations:
            src = gif_info["src"]
            gif_bytes = gif_info["bytes"]
            gif_hash = hash_text(gif_bytes)
            gif_filename = f"{context_name}{subctx_suffix}_gif_{gif_hash}.gif"
            gif_path = os.path.join(animation_dir, gif_filename)
            with open(gif_path, 'wb') as f:
                f.write(gif_bytes)
            framework_logger.info(f"Animated GIF saved at {gif_path}")
            elements.append({
                "Context": context_name,
                "SubContext": sub_context or "",
                "PageURL": page.url if hasattr(page, 'url') else "",
                "Timestamp": timestamp,
                "Type": "Animation",
                "Tag": "gif",
                "Text": "",
                "Href": src,
                "Screenshot": gif_filename,
                "ExcludeRegions": ""
            })

        visual_animations = extract_animated_visuals(
            page,
            selector=".stepsImage",
            screenshot_dir=animation_dir,
            context_hint=context_name
        )
        for visual in visual_animations:
            elements.append({
                "Context": context_name,
                "SubContext": sub_context or "",
                "PageURL": page.url if hasattr(page, 'url') else "",
                "Timestamp": timestamp,
                "Type": "Animation",
                "Tag": visual.get("tag", "div"),
                "Text": visual.get("animation_type", "visual"),
                "Href": "",
                "Screenshot": os.path.basename(visual["screenshot_path"]),
                "ExcludeRegions": ""
            })

    wb, _ = load_or_create_workbook(excel_path, Constants.SCRAPE_HEADERS)
    write_excel_context(elements, wb, context_name, excel_path, Constants.SCRAPE_HEADERS)
    framework_logger.info(f"[SCRAPER] Scraped {len(elements)} elements for {flow_name}/{context_name}{subctx_suffix}. Data written to {excel_path}")
