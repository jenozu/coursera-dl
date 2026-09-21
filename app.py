import streamlit as st

from coursera_app.auth import (
    CourseraAuthenticationError,
    connect_with_cauth,
    list_courses,
)
from coursera_app.browser_auth import (
    BrowserCookieError,
    SUPPORTED_BROWSERS,
    read_coursera_cookies_from_browser,
)
from coursera_app.config import load_config
from coursera_app.download_engine import (
    DownloadEngineError,
    cookies_from_cauth,
    download_course,
)


config = load_config()

st.set_page_config(page_title="Coursera Downloader", page_icon="📚")
st.title("Coursera Downloader")

for key, default in {
    "cauth": "",
    "auth_source": "",
    "courses": [],
    "connection": None,
    "browser_cookies": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.sidebar.header("Coursera Login")
st.sidebar.caption(
    "Log in to coursera.org in a supported browser, then connect here. "
    "Your Coursera password is not stored by this app."
)

browser = st.sidebar.selectbox(
    "Browser",
    options=list(SUPPORTED_BROWSERS),
    format_func=lambda value: value.title(),
)

if st.sidebar.button("Connect from Browser", use_container_width=True):
    try:
        cookies = read_coursera_cookies_from_browser(browser)
        cauth = next(
            cookie["value"]
            for cookie in cookies
            if cookie.get("name") == "CAUTH"
        )
        connection = connect_with_cauth(cauth)
        courses = list_courses(connection)

        st.session_state["cauth"] = cauth
        st.session_state["auth_source"] = browser
        st.session_state["connection"] = connection
        st.session_state["courses"] = courses
        st.session_state["browser_cookies"] = cookies
        st.sidebar.success(f"Connected using {browser.title()}.")
    except (BrowserCookieError, CourseraAuthenticationError) as exc:
        st.sidebar.error(str(exc))
    except Exception as exc:
        st.sidebar.error(f"Could not connect to Coursera: {exc}")

with st.sidebar.expander("Manual CAUTH fallback"):
    st.caption(
        "Use this only if automatic browser-cookie reading does not work. "
        "The value is kept in Streamlit session memory and is not written to .env."
    )
    manual_cauth = st.text_input(
        "CAUTH cookie",
        type="password",
        key="manual_cauth_input",
    )

    if st.button("Connect with CAUTH", use_container_width=True):
        try:
            connection = connect_with_cauth(manual_cauth)
            courses = list_courses(connection)

            st.session_state["cauth"] = manual_cauth.strip()
            st.session_state["auth_source"] = "manual"
            st.session_state["connection"] = connection
            st.session_state["courses"] = courses
            st.session_state["browser_cookies"] = cookies_from_cauth(manual_cauth)
            st.success("Connected to Coursera.")
        except CourseraAuthenticationError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Could not connect to Coursera: {exc}")

if st.sidebar.button("Disconnect", use_container_width=True):
    st.session_state["cauth"] = ""
    st.session_state["auth_source"] = ""
    st.session_state["connection"] = None
    st.session_state["courses"] = []
    st.session_state["browser_cookies"] = []
    st.sidebar.success("Disconnected.")

connection = st.session_state["connection"]
courses = st.session_state["courses"]

if not connection:
    st.info(
        "Sign in to Coursera in Firefox, Edge, or Brave, then choose that browser "
        "in the sidebar and click **Connect from Browser**."
    )
    st.stop()

if st.session_state["auth_source"]:
    source = st.session_state["auth_source"]
    source_label = source.title() if source != "manual" else "Manual CAUTH"
    st.success(f"Connected to Coursera via {source_label}.")

if not courses:
    st.warning(
        "Authentication succeeded, but no enrolled courses were returned. "
        "Phase 3 will also add direct course URL/slug loading as a fallback."
    )
    st.stop()

selected_course = st.selectbox(
    "Select a course to download:",
    courses,
)
st.info(f"Selected course: {selected_course}")

st.subheader("Select content types to download:")
content_types = [
    ("Videos", "video"),
    ("Subtitles", "subtitle"),
    ("PDFs", "pdf"),
    ("Assignments / HTML", "assignment"),
    ("Supplementary files", "supplement"),
]

if "select_all" not in st.session_state:
    st.session_state["select_all"] = True

if "content_toggles" not in st.session_state:
    st.session_state["content_toggles"] = {
        key: True for _, key in content_types
    }


def toggle_all():
    for _, key in content_types:
        st.session_state["content_toggles"][key] = st.session_state["select_all"]


st.checkbox("Select All", key="select_all", on_change=toggle_all)

for label, key in content_types:
    st.session_state["content_toggles"][key] = st.checkbox(
        label,
        value=st.session_state["content_toggles"][key],
        key=f"cb_{key}",
    )

selected_types = [
    key
    for key, selected in st.session_state["content_toggles"].items()
    if selected
]

if not selected_types:
    st.warning("Select at least one content type before downloading.")

if st.button("Download", disabled=not selected_types):
    status = st.status("Preparing course download...", expanded=True)

    try:
        status.write("Crawling the current Coursera course structure...")
        result = download_course(
            cookies=st.session_state["browser_cookies"],
            course_slug=selected_course,
            output_dir=config.download_dir,
            selected_types=selected_types,
        )

        status.write(
            f"Found {result['total_tasks']} downloadable resources; "
            f"processed {result['download_tasks']} matching your selections."
        )
        status.update(label="Download finished", state="complete", expanded=True)

        st.success(
            f"Finished. Files are under: {result['output_dir']}"
        )
    except DownloadEngineError as exc:
        status.update(label="Download failed", state="error", expanded=True)
        st.error(
            "The new download engine could not finish this course. "
            f"Details: {exc}"
        )
