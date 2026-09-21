import io
import logging
from collections import namedtuple
from contextlib import redirect_stdout

import streamlit as st

from coursera_app.auth import CourseraAuthenticationError, connect, list_courses
from coursera_app.config import (
    clear_legacy_credentials,
    load_config,
    write_legacy_credentials,
)


class StreamlitLogHandler(logging.Handler):
    """Send Python log messages to the in-memory Streamlit log viewer."""

    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

    def emit(self, record):
        self.buffer.write(self.format(record) + "\n")


config = load_config()
username = config.coursera_username
password = config.coursera_password

st.set_page_config(page_title="Coursera Downloader", page_icon="📚")
st.title("Coursera Downloader")

st.sidebar.header("Account Management")
with st.sidebar.form("credentials_form"):
    new_username = st.text_input("Coursera Email", value=username or "")
    new_password = st.text_input(
        "Coursera Password",
        value=password or "",
        type="password",
    )
    submitted = st.form_submit_button("Update Credentials")

    if submitted:
        try:
            write_legacy_credentials(new_username, new_password)
            st.success("Credentials updated. Please reload the app.")
        except Exception as exc:
            st.error(f"Failed to update credentials: {exc}")

if st.sidebar.button("Logout"):
    try:
        clear_legacy_credentials()
        st.success("Logged out. Please reload the app.")
    except Exception as exc:
        st.error(f"Failed to logout: {exc}")


if username and password:
    st.success("Credentials loaded from local configuration.")

    try:
        connection = connect(username, password)
        session = connection.session
        courses = list_courses(connection)

        if courses:
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
                    st.session_state["content_toggles"][key] = (
                        st.session_state["select_all"]
                    )

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
                file_formats = " ".join(
                    format_map[content_type]
                    for content_type in selected_types
                )
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
                    username,
                    password,
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
                            percent_num = int(
                                percent.split()[-1].replace("%", "")
                            )
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
                        (
                            username,
                            password,
                            selected_course,
                            file_formats,
                        ) = st.session_state["last_download_params"]

                    args = Args(
                        username=username,
                        password=password,
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
                            session,
                            args,
                            selected_course,
                        )

                    if completed:
                        st.success("Download completed!")
                        st.session_state["download_status"] = "idle"
                    elif error:
                        st.warning(
                            "Download finished with some errors. "
                            "Check logs for details."
                        )
                        st.session_state["download_status"] = "failed"
                    else:
                        st.info(
                            "Download finished, but nothing new was downloaded."
                        )
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
        else:
            st.warning("No courses found for this user.")

    except CourseraAuthenticationError as exc:
        st.error(f"Failed to authenticate with Coursera: {exc}")
    except Exception as exc:
        st.error(f"Failed to fetch courses: {exc}")

else:
    st.error(
        "Please add Coursera credentials in the sidebar. "
        "Phase 2 will replace this compatibility login with browser-cookie authentication."
    )
