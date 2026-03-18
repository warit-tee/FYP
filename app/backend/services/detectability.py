import os
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException


# ── Sapling (webscraping) ───────────────────────────────────────────────────

def _get_chrome_driver():
    """Create a headless Chrome WebDriver instance."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        raise RuntimeError(f"Failed to create Chrome driver: {e}")


def sapling(text: str) -> dict:
    """
    Scrape Sapling AI detector (https://sapling.ai/ai-content-detector).
    Returns score in [0,1] where 1.0 = fully AI-generated.
    Falls back to error dict if scraping fails.
    """
    driver = None
    try:
        driver = _get_chrome_driver()
        driver.get("https://sapling.ai/ai-content-detector")

        # Wait for the textarea / input area
        wait = WebDriverWait(driver, 20)

        # Find the main textarea for text input
        textarea = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "textarea, [contenteditable='true'], [data-testid='text-input']")
            )
        )

        # Clear and type the text
        textarea.clear()
        textarea.send_keys(text[:5000])  # Sapling may have a limit

        # Click the submit / check button
        submit_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(),'Check') or contains(text(),'Detect') or contains(text(),'Submit') or contains(text(),'Analyze')]")
            )
        )
        submit_btn.click()

        # Wait for result to appear
        time.sleep(5)

        # Try to find the score element
        try:
            score_element = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[class*='score'], [class*='result'], [class*='percentage'], [data-testid*='score']")
                )
            )
            score_text = score_element.text.strip()
            # Parse percentage or decimal
            if "%" in score_text:
                score = float(score_text.replace("%", "").strip()) / 100.0
            else:
                score = float(score_text)
            return {"score": round(score, 4), "sentence_scores": None}
        except (TimeoutException, ValueError):
            # Try alternative selectors
            try:
                all_text = driver.find_element(By.TAG_NAME, "body").text
                # Look for percentage pattern
                import re
                matches = re.findall(r'(\d+(?:\.\d+)?)\s*%\s*(?:AI|Fake|Generated)', all_text, re.IGNORECASE)
                if matches:
                    score = float(matches[0]) / 100.0
                    return {"score": round(score, 4), "sentence_scores": None}
            except Exception:
                pass
            return {"error": "Could not parse Sapling score from page"}

    except RuntimeError as e:
        return {"error": str(e)}
    except TimeoutException:
        return {"error": "Sapling page timed out"}
    except WebDriverException as e:
        return {"error": f"WebDriver error: {str(e)}"}
    except Exception as e:
        return {"error": f"Sapling scraping failed: {str(e)}"}
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


# ── ZeroGPT (API-style request) ────────────────────────────────────────────

def zerogpt(text: str) -> dict:
    try:
        resp = requests.post(
            "https://api.zerogpt.com/api/detect/detectText",
            headers={
                "Content-Type": "application/json",
                "Origin": "https://www.zerogpt.com",
                "Referer": "https://www.zerogpt.com/",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                ),
            },
            json={"text": text, "input_text": text},
            timeout=20,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                d = data.get("data", {})
                return {
                    "fake_percentage": d.get("fakePercentage"),
                    "is_human":        d.get("isHuman"),
                    "ai_words":        d.get("aiWords"),
                    "text_words":      d.get("textWords"),
                    "feedback":        d.get("feedback"),
                }
            return {"error": "ZeroGPT returned success=False", "raw": data}
        return {"error": f"ZeroGPT returned {resp.status_code}: {resp.text}"}
    except Exception as exc:
        return {"error": str(exc)}


# ── Combined ────────────────────────────────────────────────────────────────

def all_detectors(text: str) -> dict:
    return {
        "sapling": sapling(text),
        "zerogpt": zerogpt(text),
    }