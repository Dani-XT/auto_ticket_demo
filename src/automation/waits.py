# src/automation/waits.py
from playwright.sync_api import TimeoutError as PWTimeoutError

from src.app.config import MONTHS_ES_INV

from src.utils.exceptions import RetryableUIError


def find_in_all_frames(page, css_selector: str):
    loc = page.main_frame.locator(css_selector)
    try:
        if loc.count() > 0:
            return loc, page.main_frame
    except Exception:
        pass

    for frame in page.frames:
        loc = frame.locator(css_selector)
        try:
            if loc.count() > 0:
                return loc, frame
        except Exception:
            continue

    return None, None

def wait_in_all_frames(page, css_selector: str, timeout_ms: int = 10_000, step_ms: int = 200, state: str = "visible", require_enabled: bool = False):
    waited = 0
    last_err = None

    while waited < timeout_ms:
        try:
            loc = page.main_frame.locator(css_selector)
            if loc.count() > 0:
                locator = loc.first
                locator.wait_for(state=state, timeout=step_ms)
                if require_enabled and not locator.is_enabled():
                    raise Exception("locator not enabled yet")
                return locator, page.main_frame
        except Exception as e:
            last_err = e

        for frame in page.frames:
            try:
                loc = frame.locator(css_selector)
                if loc.count() > 0:
                    locator = loc.first
                    locator.wait_for(state=state, timeout=step_ms)
                    if require_enabled and not locator.is_enabled():
                        raise Exception("locator not enabled yet")
                    return locator, frame
            except Exception as e:
                last_err = e
                continue

        page.wait_for_timeout(step_ms)
        waited += step_ms

    raise PWTimeoutError(f"Timeout esperando {css_selector}. Último error: {last_err}")

def wait_visible_enabled(page, locator, timeout_ms: int = 10_000, step_ms: int = 200):
    locator.wait_for(state="visible", timeout=timeout_ms)

    waited = 0
    last_err = None
    while waited < timeout_ms:
        try:
            if locator.is_enabled():
                return locator
        except Exception as e:
            last_err = e

        page.wait_for_timeout(step_ms)
        waited += step_ms

    raise PWTimeoutError(f"Locator visible pero no habilitado a tiempo. Último error: {last_err}")


def smart_click(locator, frame=None, expect_nav: bool = False, nav_timeout_ms: int = 30_000):
    try:
        locator.scroll_into_view_if_needed(timeout=5_000)
    except Exception:
        pass

    if expect_nav and frame is not None:
        try:
            with frame.expect_navigation(wait_until="domcontentloaded", timeout=nav_timeout_ms):
                locator.click(timeout=10_000)
            return
        except PWTimeoutError:
            pass

    locator.click(timeout=10_000)


def get_visible_popup(page, popup_selector: str, must_contain_selector: str | None = None):
    for fr in page.frames:
        popups = fr.locator(popup_selector)
        try:
            count = popups.count()
        except Exception:
            continue

        for i in range(count):
            p = popups.nth(i)
            try:
                if not p.is_visible():
                    continue
                if must_contain_selector and p.locator(must_contain_selector).count() == 0:
                    continue
                return p
            except Exception:
                continue

    return None


def wait_visible_popup(page, popup_selector: str, must_contain_selector: str | None = None, timeout_ms: int = 10_000, step_ms: int = 200):
    waited = 0
    while waited < timeout_ms:
        popup = get_visible_popup(page, popup_selector, must_contain_selector)
        if popup:
            return popup

        page.wait_for_timeout(step_ms)
        waited += step_ms

    raise PWTimeoutError(
        f"Timeout esperando popup visible: {popup_selector} (must_contain={must_contain_selector})"
    )


def get_label_txt(page, selector: str, timeout_ms: int = 10_000):
    locator, frame = wait_in_all_frames(page, selector, timeout_ms=timeout_ms, state="visible")
    return locator.inner_text().strip()


def get_label_popup_txt(page, popup_selector: str, label_selector: str, timeout_ms: int = 10_000):
    popup = wait_visible_popup(
        page,
        popup_selector=popup_selector,
        must_contain_selector=label_selector,
        timeout_ms=timeout_ms,
    )
    label = popup.locator(label_selector)
    label.wait_for(state="visible", timeout=timeout_ms)
    return label.inner_text().strip()


def wait_popup_result(
    page,
    popup,
    option_selector: str,
    min_results: int = 1,
    timeout_ms: int = 10_000,
    step_ms: int = 200,
    ignore_null_id: bool = True,
):
    waited = 0
    last_visible = 0

    while waited < timeout_ms:
        try:
            options = popup.locator(option_selector)
            count = options.count()

            visible_count = 0
            for i in range(count):
                opt = options.nth(i)
                try:
                    if ignore_null_id:
                        opt_id = opt.get_attribute("id")
                        if opt_id == "pawIdNull":
                            continue
                    if opt.is_visible():
                        visible_count += 1
                except Exception:
                    continue

            if visible_count >= min_results:
                return options

            last_visible = visible_count
        except Exception:
            pass

        page.wait_for_timeout(step_ms)
        waited += step_ms

    raise PWTimeoutError(
        f"No aparecieron suficientes resultados en popup. visibles={last_visible}, requeridos={min_results}"
    )


def select_popup_option_by_text(
    page,
    popup,
    option_selector: str,
    target_text: str,
    timeout_ms: int = 10_000,
    step_ms: int = 200,
):
    waited = 0

    while waited < timeout_ms:
        options = wait_popup_result(
            page=page,
            popup=popup,
            option_selector=option_selector,
            min_results=1,
            timeout_ms=step_ms,
            step_ms=step_ms,
            ignore_null_id=False,
        )

        count = options.count()
        for i in range(count):
            opt = options.nth(i)
            try:
                if opt.is_visible() and opt.inner_text().strip() == target_text:
                    opt.click(timeout=5_000)
                    return True
            except Exception:
                continue

        page.wait_for_timeout(step_ms)
        waited += step_ms

    raise RuntimeError(f"No se encontró la opción '{target_text}' en el popup.")


def select_popup_option_by_attr_contains(page, popup, attr: str, needle: str, timeout_ms: int = 10_000, step_ms: int = 200, case_insensitive: bool = True,):
    wanted = (needle or "").strip()
    if not wanted:
        raise RuntimeError("needle vacío")

    if ":" in attr:
        attr_expr = f"@*[name()='{attr}']"
    else:
        attr_expr = f"@{attr}"

    if case_insensitive:
        xpath = (
            "xpath=.//div[contains(@class,'pawOpt') and not(@id='pawIdNull') and "
            f"contains(translate({attr_expr}, "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜÑ', "
            "'abcdefghijklmnopqrstuvwxyzáéíóúüñ'), "
            f"'{wanted.lower()}')]"
        )
    else:
        xpath = (
            "xpath=.//div[contains(@class,'pawOpt') and not(@id='pawIdNull') and "
            f"contains({attr_expr}, '{wanted}')]"
        )

    waited = 0
    last_err = None

    while waited < timeout_ms:
        try:
            opt = popup.locator(xpath).first
            opt.wait_for(state="visible", timeout=step_ms)
            opt.click(timeout=5_000)
            return True
        except Exception as e:
            last_err = e

        page.wait_for_timeout(step_ms)
        waited += step_ms

    raise RuntimeError(f"No se encontró opción por atributo '{attr}' que contenga '{needle}'. Último error: {last_err}")


def parse_month_year_es(text: str) -> tuple[int, int]:
    t = (text or "").strip().lower()
    parts = [p.strip() for p in t.split(" de ")]
    if len(parts) != 2:
        raise RuntimeError(f"No pude parsear mes/año desde: '{text}'")

    month_name, year_str = parts
    if month_name not in MONTHS_ES_INV:
        raise RuntimeError(f"Mes no reconocido: '{month_name}' en '{text}'")

    return int(year_str), MONTHS_ES_INV[month_name]


def get_tree_popup(frame, root_label: str, timeout=20_000):
    popup = frame.locator('css=div[paw\\:ctrl="pawTree"].pawTreePopup:visible').first
    popup.wait_for(state="visible", timeout=timeout)
    popup.locator('css=span.pawTreeNodeLabel', has_text=root_label).first.wait_for(
        state="visible",
        timeout=timeout,
    )
    return popup


def tree_header_by_label(popup, label: str):
    return popup.locator(
        'xpath=.//div[contains(@class,"pawTreeNodeHeader")]'
        f'[.//span[contains(@class,"pawTreeNodeLabel")][normalize-space(.)="{label}"]]'
    ).first


def tree_expand(page, popup, label: str, timeout=20_000):
    header = tree_header_by_label(popup, label)
    header.wait_for(state="visible", timeout=timeout)
    header.scroll_into_view_if_needed()

    exp = header.locator("css=img#pawExp").first
    if exp.count() > 0:
        exp.wait_for(state="visible", timeout=timeout)
        exp.click()
    else:
        header.click()

    page.wait_for_timeout(200)


def tree_click_leaf(page, popup, label: str, timeout=20_000):
    header = tree_header_by_label(popup, label)
    header.wait_for(state="visible", timeout=timeout)
    header.scroll_into_view_if_needed()
    header.click()
    page.wait_for_timeout(200)


def tree_wait_label_visible(popup, label: str, timeout=20_000):
    popup.locator("css=span.pawTreeNodeLabel", has_text=label).first.wait_for(
        state="visible",
        timeout=timeout,
    )


def click_radio_btn(page, row_id: str, timeout=10_000):
    locator, frame = wait_in_all_frames(page, f"tr#{row_id}", timeout_ms=timeout, state="visible")
    smart_click(locator, frame=frame, expect_nav=False)
    page.wait_for_timeout(200)
    return frame


def deselect_page(page):
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(150)
    except Exception:
        pass
    try:
        body = page.main_frame.locator("body")
        body.click(timeout=2_000)
        page.wait_for_timeout(150)
    except Exception:
        pass


def retry_ui_block(page, action, attempts: int = 3, step_ms: int = 300, recover=None, error_message: str = "No se pudo completar la acción UI.",):
    last_err = None

    for attempt in range(1, attempts + 1):
        try:
            return action()
        except Exception as e:
            last_err = e

            if attempt >= attempts:
                break

            if recover:
                try:
                    recover()
                except Exception:
                    pass

            page.wait_for_timeout(step_ms)

    raise RetryableUIError(f"{error_message} Último error: {last_err}") from last_err