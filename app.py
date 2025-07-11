import streamlit as st
import os
from dotenv import load_dotenv

# coursera-dl imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'venv', 'Lib', 'site-packages'))
import requests
from coursera.extractors import CourseraExtractor
from coursera.coursera_dl import get_session, login

import io
import logging
from contextlib import redirect_stdout

# Custom log handler for Streamlit
class StreamlitLogHandler(logging.Handler):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer
    def emit(self, record):
        msg = self.format(record)
        self.buffer.write(msg + '\n')

# Load environment variables from .env file
load_dotenv()

# Retrieve credentials
username = os.getenv('COURSERA_USERNAME')
password = os.getenv('COURSERA_PASSWORD')

st.title('Coursera Downloader')

# Add credential management UI
st.sidebar.header('Account Management')
with st.sidebar.form('credentials_form'):
    new_username = st.text_input('Coursera Email', value=username or '')
    new_password = st.text_input('Coursera Password', value=password or '', type='password')
    submitted = st.form_submit_button('Update Credentials')
    if submitted:
        try:
            with open('.env', 'w') as f:
                f.write(f'COURSERA_USERNAME={new_username}\n')
                f.write(f'COURSERA_PASSWORD={new_password}\n')
            st.success('Credentials updated. Please reload the app.')
        except Exception as e:
            st.error(f'Failed to update credentials: {e}')
if st.sidebar.button('Logout'):
    try:
        with open('.env', 'w') as f:
            f.write('COURSERA_USERNAME=\nCOURSERA_PASSWORD=\n')
        st.success('Logged out. Please reload the app.')
    except Exception as e:
        st.error(f'Failed to logout: {e}')

if username and password:
    st.success('Credentials loaded from .env file.')
    # Try to authenticate and fetch courses
    try:
        session = get_session()
        login(session, username, password)
        extractor = CourseraExtractor(session)
        courses = extractor.list_courses()
        if courses:
            selected_course = st.selectbox('Select a course to download:', courses)
            st.info(f'Selected course: {selected_course}')

            st.subheader('Select content types to download:')
            content_types = [
                ('Videos', 'video'),
                ('Subtitles', 'subtitle'),
                ('PDFs', 'pdf'),
                ('Assignments', 'assignment'),
                ('Supplementary files', 'supplement')
            ]
            # Session state for toggles
            if 'select_all' not in st.session_state:
                st.session_state['select_all'] = False
            if 'content_toggles' not in st.session_state:
                st.session_state['content_toggles'] = {k: False for _, k in content_types}

            def toggle_all():
                for _, key in content_types:
                    st.session_state['content_toggles'][key] = st.session_state['select_all']

            st.checkbox('Select All', key='select_all', on_change=toggle_all)
            for label, key in content_types:
                st.session_state['content_toggles'][key] = st.checkbox(label, value=st.session_state['content_toggles'][key], key=f'cb_{key}')

            selected_types = [k for k, v in st.session_state['content_toggles'].items() if v]
            st.write('Selected content types:', selected_types)

            # Map content types to file formats
            format_map = {
                'video': 'mp4',
                'subtitle': 'srt txt',
                'pdf': 'pdf',
                'assignment': 'html',
                'supplement': 'zip rar xlsx csv tsv ipynb json ppt pptx doc docx py Rmd Rdata wf1'
            }
            if selected_types and len(selected_types) < len(content_types):
                file_formats = ' '.join([format_map[t] for t in selected_types])
            else:
                file_formats = 'all'

            # Download control buttons and state
            if 'download_status' not in st.session_state:
                st.session_state['download_status'] = 'idle'
            if 'last_download_params' not in st.session_state:
                st.session_state['last_download_params'] = None
            if 'cancel_download' not in st.session_state:
                st.session_state['cancel_download'] = False

            def cancel_download():
                st.session_state['cancel_download'] = True

            def reset_cancel():
                st.session_state['cancel_download'] = False

            # Download button
            if st.button('Download'):
                st.session_state['download_status'] = 'running'
                st.session_state['last_download_params'] = (username, password, selected_course, file_formats)
                reset_cancel()

            # Retry button
            if st.session_state['download_status'] == 'failed' and st.button('Retry'):
                st.session_state['download_status'] = 'running'
                reset_cancel()

            # Cancel button
            if st.session_state['download_status'] == 'running':
                st.button('Cancel', on_click=cancel_download)

            # Download logic
            if st.session_state['download_status'] == 'running':
                log_buffer = io.StringIO()
                log_handler = StreamlitLogHandler(log_buffer)
                logger = logging.getLogger()
                logger.addHandler(log_handler)
                logger.setLevel(logging.INFO)
                progress_bar = st.progress(0)
                log_area = st.empty()
                try:
                    from collections import namedtuple
                    from coursera.downloaders import DownloadProgress
                    orig_report_progress = DownloadProgress.report_progress
                    def patched_report_progress(self):
                        percent = self.calc_percent()
                        try:
                            percent_num = int(percent.split()[-1].replace('%',''))
                        except Exception:
                            percent_num = 0
                        progress_bar.progress(min(percent_num, 100))
                        orig_report_progress(self)
                        if st.session_state.get('cancel_download'):
                            raise Exception('Download cancelled by user.')
                    DownloadProgress.report_progress = patched_report_progress
                    Args = namedtuple('Args', [
                        'username', 'password', 'class_names', 'file_formats', 'path',
                        'reverse', 'unrestricted_filenames', 'subtitle_language', 'video_resolution',
                        'download_quizzes', 'mathjax_cdn_url', 'download_notebooks', 'cache_syllabus',
                        'only_syllabus', 'ignore_formats', 'disable_url_skipping', 'jobs'
                    ])
                    # Use last params for retry, else current
                    if st.session_state['last_download_params']:
                        username, password, selected_course, file_formats = st.session_state['last_download_params']
                    args = Args(
                        username=username,
                        password=password,
                        class_names=[selected_course],
                        file_formats=file_formats.split(),
                        path='',
                        reverse=False,
                        unrestricted_filenames=False,
                        subtitle_language='all',
                        video_resolution='540p',
                        download_quizzes=False,
                        mathjax_cdn_url=None,
                        download_notebooks=False,
                        cache_syllabus=False,
                        only_syllabus=False,
                        ignore_formats=None,
                        disable_url_skipping=False,
                        jobs=1
                    )
                    from coursera.coursera_dl import download_on_demand_class
                    with redirect_stdout(log_buffer):
                        error, completed = download_on_demand_class(session, args, selected_course)
                    if completed:
                        st.success('Download completed!')
                        st.session_state['download_status'] = 'idle'
                    elif error:
                        st.warning('Download finished with some errors. Check logs for details.')
                        st.session_state['download_status'] = 'failed'
                    else:
                        st.info('Download finished, but nothing new was downloaded.')
                        st.session_state['download_status'] = 'idle'
                except Exception as e:
                    if str(e) == 'Download cancelled by user.':
                        st.warning('Download cancelled.')
                    else:
                        st.error(f'Error during download: {e}')
                    st.session_state['download_status'] = 'failed'
                finally:
                    logger.removeHandler(log_handler)
                log_area.text_area('Download Log', log_buffer.getvalue(), height=300)
        else:
            st.warning('No courses found for this user.')
    except Exception as e:
        st.error(f'Failed to fetch courses: {e}')
else:
    st.error('Please set COURSERA_USERNAME and COURSERA_PASSWORD in your .env file.') 