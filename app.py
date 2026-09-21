import io
import logging
from collections import namedtuple
from contextlib import redirect_stdout

import streamlit as st

from coursera_app.auth import (
    CourseraAuthenticationError,
    connect_with_cauth,
    list_courses,
)
from coursera_app.browser_auth import (
    BrowserCookieError,
    SUPPORTED_BROWSERS,
    read_cauth_from_browser,
)
from coursera_app.config import load_config


class StreamlitLogHandler(logging.Handler):
    """Send Python log messages to the in-memory Streamlit log viewer."""

    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

    def emit(self, record):
        self.buffer.write(self.format(record) + "\n")


config = load_config()

st.set_page_config(page_title="Coursera Downloader", page_icon="📚")
st.title("Coursera Downloader")

if "cauth" not in st.session_state:
    st.session_state["cauth"] = ""
if "auth_source" not in st.session_state:
    st.session_state["auth_source"] = ""
if "courses" not in st.session_state:
    st.session_state["courses"] = []
if "connection" not in st.session_state:
    st.session_state["connection"] = None

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
        cauth = read_cauth_from_browser(browser)
        connection = connect_with_cauth(cauth)
        courses = list_courses(connection)

        st.session_state["cauth"] = cauth
        st.session_state["auth_source"] = browser
        st.session_state["connection"] = connection
        st.session_state["courses"] = courses
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
    ("Assignments", "assignment"),
    ("Supplementary files", "supplement"),
]

if "select_all" not in st.session_state:
    st.session_state["select_all"] = False

if "content_toggles" not in st.session_state:
    st.session_state["content_toggles"] = {
        key: False for _, key in content_types
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
st.write("Selected content types:", selected_types)

format_map = {
    "video": "mp4",
    "subtitle": "srt txt",
    "pdf": "pdf",
    "assignment": "html",
    "supplement": (
        "zip rar xlsx csv tsv ipynb json ppt pptx "
        "doc docx py Rmd Rdata wf1"
    ),
}

if selected_types and len(selected_types) < len(content_types):
    file_formats = " ".join(format_map[item] for item in selected_types)
else:
    file_formats = "all"

if "download_status" not in st.session_state:
    st.session_state["download_status"] = "idle"

if "last_download_params" not in st.session_state:
    st.session_state["last_download_params"] = None

if "cancel_download" not in st.session_state:
    st.session_state["cancel_download"] = False


def cancel_download():
    st.session_state["cancel_download"] = True


def reset_cancel():
    st.session_state["cancel_download"] = False


if st.button("Download"):
    st.session_state["download_status"] = "running"
    st.session_state["last_download_params"] = (
        selected_course,
        file_formats,
    )
    reset_cancel()

if (
    st.session_state["download_status"] == "failed"
    and st.button("Retry")
):
    st.session_state["download_status"] = "running"
    reset_cancel()

if st.session_state["download_status"] == "running":
    st.button("Cancel", on_click=cancel_download)

if st.session_state["download_status"] == "running":
    log_buffer = io.StringIO()
    log_handler = StreamlitLogHandler(log_buffer)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    progress_bar = st.progress(0)
    log_area = st.empty()

    try:
        from coursera.downloaders import DownloadProgress
        from coursera.coursera_dl import download_on_demand_class

        original_report_progress = DownloadProgress.report_progress

        def patched_report_progress(self):
            percent = self.calc_percent()
            try:
                percent_num = int(percent.split()[-1].replace("%", ""))
            except Exception:
                percent_num = 0

            progress_bar.progress(min(percent_num, 100))
            original_report_progress(self)

            if st.session_state.get("cancel_download"):
                raise RuntimeError("Download cancelled by user.")

        DownloadProgress.report_progress = patched_report_progress

        Args = namedtuple(
            "Args",
            [
                "username",
                "password",
                "class_names",
                "file_formats",
                "path",
                "reverse",
                "unrestricted_filenames",
                "subtitle_language",
                "video_resolution",
                "download_quizzes",
                "mathjax_cdn_url",
                "download_notebooks",
                "cache_syllabus",
                "only_syllabus",
                "ignore_formats",
                "disable_url_skipping",
                "jobs",
            ],
        )

        if st.session_state["last_download_params"]:
            selected_course, file_formats = st.session_state["last_download_params"]

        args = Args(
            username="",
            password="",
            class_names=[selected_course],
            file_formats=file_formats.split(),
            path=config.download_dir,
            reverse=False,
            unrestricted_filenames=False,
            subtitle_language="all",
            video_resolution="540p",
            download_quizzes=False,
            mathjax_cdn_url=None,
            download_notebooks=False,
            cache_syllabus=False,
            only_syllabus=False,
            ignore_formats=None,
            disable_url_skipping=False,
            jobs=1,
        )

        with redirect_stdout(log_buffer):
            error, completed = download_on_demand_class(
                connection.session,
                args,
                selected_course,
            )

        if completed:
            st.success("Download completed!")
            st.session_state["download_status"] = "idle"
        elif error:
            st.warning(
                "Download finished with some errors. Check logs for details."
            )
            st.session_state["download_status"] = "failed"
        else:
            st.info("Download finished, but nothing new was downloaded.")
            st.session_state["download_status"] = "idle"

    except Exception as exc:
        if str(exc) == "Download cancelled by user.":
            st.warning("Download cancelled.")
        else:
            st.error(f"Error during download: {exc}")
        st.session_state["download_status"] = "failed"

    finally:
        logger.removeHandler(log_handler)

    log_area.text_area(
        "Download Log",
        log_buffer.getvalue(),
        height=300,
    )
