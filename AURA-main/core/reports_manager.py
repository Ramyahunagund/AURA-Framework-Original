import os
import ast
import html
import datetime
import json
import logging
import sys
import io
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from core.settings import framework_logger, Constants

# Local inline toggles for report generation (edit True/False here as needed)
# No CLI flags or environment variables are used; this file is the single source of truth.
# ENABLE_HTML = os.getenv('AURA_ENABLE_HTML', '1') not in ('0', 'false', 'False')
# ENABLE_JSON = os.getenv('AURA_ENABLE_JSON', '1') not in ('0', 'false', 'False')
ENABLE_HTML = True   # Set to False to skip generating HTML report
ENABLE_JSON = True   # Set to False to skip generating JSON companion

@dataclass
class ReportStep:
    id: int
    file: str
    line: int
    pattern: str
    status: str = "PENDING"  # PENDING | PASS | FAIL | NOT_EXECUTED
    logged_message: Optional[str] = None
    timestamp: Optional[str] = None
    duration_ms: Optional[int] = None
    _start_monotonic: Optional[float] = None
    execution_order: Optional[int] = None
    occurrences: int = 0
    first_timestamp_dt: Optional[datetime.datetime] = None

    def to_row(self) -> Dict[str, Any]:
        # Fallback to static pattern when no concrete logged message (e.g. NOT_EXECUTED / PENDING)
        display_message = self.logged_message if self.logged_message else self.pattern
        return {
            'id': self.id,
            'file': self.file,
            'line': self.line,
            'pattern': self.pattern,
            'status': self.status,
            'message': display_message or '',
            'timestamp': self.timestamp or '',
            'duration_ms': self.duration_ms,
            'first_timestamp': self.first_timestamp_dt.isoformat() + 'Z' if self.first_timestamp_dt else '',
        }

class _LogHandler(logging.Handler):
    def __init__(self, reporter: 'ReportsManager'):
        super().__init__(level=logging.INFO)
        self.reporter = reporter
    def emit(self, record: logging.LogRecord):  # type: ignore[override]
        try:
            if record.levelno != logging.INFO:
                return
            msg = record.getMessage()
            self.reporter.record_step_execution(msg, record)
        except Exception:
            pass

class ReportsManager:
    CONSOLE_MAX_BYTES = 2 * 1024 * 1024
    def __init__(self, flow_name: str, run_id: str, output_dir: Optional[str]):
        self.flow_name = flow_name
        self.run_id = run_id
        if output_dir is None:
            raise ValueError("ReportsManager requires an explicit output_dir; noop runs must supply run directory.")
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self._run_dir = self.output_dir
        self.steps: List[ReportStep] = []
        self._executed_step_ids: List[int] = []
        self._handler: Optional[_LogHandler] = None
        self._built_index: Dict[str, List[int]] = {}
        self._suite_start = datetime.datetime.utcnow()
        self._last_step_end_monotonic: Optional[float] = None
        self._exact_pattern_index: Dict[str, int] = {}
        self.console_buffer = io.StringIO()
        self._orig_stdout = None
        self._orig_stderr = None
        self._stdout_tee = None
        self._stderr_tee = None
        self._log_capture_handler: Optional[logging.Handler] = None
        self._flow_dir = os.path.join(Constants.TEST_FLOWS_PATH, self.flow_name)
        self._dynamic_added = set()  # type: ignore[var-annotated]
        self._location_index: Dict[tuple, List[int]] = {}
        self._next_exec_order = 1

    class _Tee:
        def __init__(self, original, buf: io.StringIO):
            self.original = original
            self.buf = buf
        def write(self, data):
            try:
                self.original.write(data)
            except Exception:
                pass
            try:
                self.buf.write(data)
            except Exception:
                pass
        def flush(self):
            try:
                self.original.flush()
            except Exception:
                pass

    def start(self):
        self.scan_sources()
        self._handler = _LogHandler(self)
        framework_logger.addHandler(self._handler)
        self._log_capture_handler = logging.Handler()
        self._log_capture_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
        self._log_capture_handler.setFormatter(formatter)
        def emit(rec):
            try:
                self.console_buffer.write(self._log_capture_handler.format(rec) + '\n')
            except Exception:
                pass
        self._log_capture_handler.emit = emit  # type: ignore
        framework_logger.addHandler(self._log_capture_handler)
        try:
            self._orig_stdout = sys.stdout
            self._orig_stderr = sys.stderr
            self._stdout_tee = self._Tee(sys.stdout, self.console_buffer)
            self._stderr_tee = self._Tee(sys.stderr, self.console_buffer)
            sys.stdout = self._stdout_tee  # type: ignore
            sys.stderr = self._stderr_tee  # type: ignore
        except Exception as e:
            framework_logger.debug(f"[REPORTS] Failed to tee stdout/stderr: {e}")
        framework_logger.debug(f"[REPORTS] Initialized with {len(self.steps)} potential steps. Output: {self.report_path}")

    def finalize(self, success: bool, exception: Optional[BaseException] = None):
        if not success and self._executed_step_ids:
            last_id = self._executed_step_ids[-1]
            step = self._get_step(last_id)
            if step.status in ("PASS", "PENDING"):
                step.status = "FAIL"
            if exception:
                step.logged_message = (step.logged_message or step.pattern) + f" | Exception: {exception}"[:500]
        for s in self.steps:
            if s.status == 'PENDING':
                s.status = 'NOT_EXECUTED'
        if self._handler:
            try: framework_logger.removeHandler(self._handler)
            except Exception: pass
        if self._log_capture_handler:
            try: framework_logger.removeHandler(self._log_capture_handler)
            except Exception: pass
        try:
            if self._orig_stdout is not None:
                sys.stdout = self._orig_stdout  # type: ignore
            if self._orig_stderr is not None:
                sys.stderr = self._orig_stderr  # type: ignore
        except Exception:
            pass
        if ENABLE_HTML:
            self._generate_html()
        if ENABLE_JSON:
            self._write_json()
        framework_logger.info(f"Test report generated: {self.report_path if ENABLE_HTML else '(HTML disabled)'}")

    def record_step_execution(self, log_message: str, record: logging.LogRecord):
        normalized_msg = log_message.strip()
        abs_path = getattr(record, 'pathname', None)
        lineno = getattr(record, 'lineno', None)
        import time
        attempt_like = (' - attempt ' in normalized_msg) or normalized_msg.endswith(' successful')
        if attempt_like and normalized_msg in self._exact_pattern_index:
            step = self._get_step(self._exact_pattern_index[normalized_msg])
            step.occurrences += 1
            step.timestamp = datetime.datetime.utcnow().isoformat(timespec='microseconds') + 'Z'
            return
        if abs_path and lineno and (abs_path, lineno) in self._location_index:
            for sid in self._location_index[(abs_path, lineno)]:
                step = self._get_step(sid)
                if step.pattern == normalized_msg or step.logged_message == normalized_msg or self._match(step.pattern, normalized_msg):
                    self._mark_step_execution(step, normalized_msg, time)
                    return
        for step in self.steps:
            if step.status == 'PENDING' and self._match(step.pattern, normalized_msg):
                if step.pattern.startswith('{…}') and step.logged_message:
                    existing_prefix = step.logged_message.split(' - attempt ')[0]
                    new_prefix = normalized_msg.split(' - attempt ')[0]
                    if existing_prefix != new_prefix:
                        continue
                if abs_path and lineno:
                    self._location_index.setdefault((abs_path, lineno), []).append(step.id)
                self._mark_step_execution(step, normalized_msg, time)
                return
        for step in self.steps:
            if self._match(step.pattern, normalized_msg):
                if step.pattern.startswith('{…}') and step.logged_message:
                    existing_prefix = step.logged_message.split(' - attempt ')[0]
                    new_prefix = normalized_msg.split(' - attempt ')[0]
                    if existing_prefix != new_prefix:
                        continue
                if abs_path and lineno and (abs_path, lineno) not in self._location_index:
                    self._location_index.setdefault((abs_path, lineno), []).append(step.id)
                step.occurrences += 1
                step.timestamp = datetime.datetime.utcnow().isoformat(timespec='microseconds') + 'Z'
                return
        if abs_path and lineno and os.path.isfile(abs_path):
            pattern = self._extract_logger_call_pattern(abs_path, lineno)
            if pattern:
                if attempt_like:
                    pattern = normalized_msg
                rel_file = os.path.relpath(abs_path, Constants.ROOT_DIR)
                new_id = len(self.steps) + 1
                now_monotonic = time.monotonic()
                if self._executed_step_ids:
                    prev = self._get_step(self._executed_step_ids[-1])
                    if prev._start_monotonic is not None and prev.duration_ms is None:
                        prev.duration_ms = int((now_monotonic - prev._start_monotonic) * 1000)
                new_step = ReportStep(
                    id=new_id,
                    file=rel_file,
                    line=lineno,
                    pattern=pattern.strip(),
                    status='PASS',
                    logged_message=normalized_msg,
                    timestamp=datetime.datetime.utcnow().isoformat(timespec='microseconds') + 'Z',
                    _start_monotonic=now_monotonic,
                    execution_order=self._next_exec_order,
                    occurrences=1,
                    first_timestamp_dt=datetime.datetime.utcnow()
                )
                self._next_exec_order += 1
                self.steps.append(new_step)
                self._exact_pattern_index[pattern] = new_id
                self._built_index.setdefault(pattern.strip()[:10].lower(), []).append(new_id)
                self._executed_step_ids.append(new_id)
                self._location_index.setdefault((abs_path, lineno), []).append(new_id)
                return
        if attempt_like and normalized_msg not in self._exact_pattern_index:
            new_id = len(self.steps) + 1
            now_monotonic = time.monotonic()
            if self._executed_step_ids:
                prev = self._get_step(self._executed_step_ids[-1])
                if prev._start_monotonic is not None and prev.duration_ms is None:
                    prev.duration_ms = int((now_monotonic - prev._start_monotonic) * 1000)
            new_step = ReportStep(
                id=new_id,
                file=abs_path or 'N/A',
                line=lineno or -1,
                pattern=normalized_msg,
                status='PASS',
                logged_message=normalized_msg,
                timestamp=datetime.datetime.utcnow().isoformat(timespec='microseconds') + 'Z',
                _start_monotonic=now_monotonic,
                execution_order=self._next_exec_order,
                occurrences=1,
                first_timestamp_dt=datetime.datetime.utcnow()
            )
            self._next_exec_order += 1
            self.steps.append(new_step)
            self._exact_pattern_index[normalized_msg] = new_id
            self._executed_step_ids.append(new_id)
            return

    def _mark_step_execution(self, step: ReportStep, normalized_msg: str, time_module):
        now_dt = datetime.datetime.utcnow()
        now_iso = now_dt.isoformat(timespec='microseconds') + 'Z'
        now_monotonic = time_module.monotonic()
        if self._executed_step_ids:
            prev = self._get_step(self._executed_step_ids[-1])
            if prev._start_monotonic is not None and prev.duration_ms is None:
                prev.duration_ms = int((now_monotonic - prev._start_monotonic) * 1000)
        if step.execution_order is None:
            step.execution_order = self._next_exec_order
            self._next_exec_order += 1
            self._executed_step_ids.append(step.id)
            step._start_monotonic = now_monotonic
            if step.first_timestamp_dt is None:
                step.first_timestamp_dt = now_dt
        step.status = 'PASS'
        if not step.logged_message:
            step.logged_message = normalized_msg
        step.timestamp = now_iso
        step.occurrences = step.occurrences + 1 if step.occurrences else 1

    def scan_sources(self):
        search_paths = [self._flow_dir]
        step_id = 1
        for path in search_paths:
            if not os.path.isdir(path):
                continue
            for root, _, files in os.walk(path):
                for fname in files:
                    if not fname.endswith('.py'):
                        continue
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            source = f.read()
                        tree = ast.parse(source, filename=fpath)
                    except Exception:
                        continue
                    for node in ast.walk(tree):
                        if not isinstance(node, ast.Call):
                            continue
                        func = node.func
                        if isinstance(func, ast.Attribute) and getattr(func.value, 'id', None) == 'framework_logger' and func.attr == 'info':
                            if not node.args:
                                continue
                            arg0 = node.args[0]
                            pattern = self._extract_pattern(arg0)
                            if not pattern:
                                continue
                            rel_file = os.path.relpath(fpath, Constants.ROOT_DIR)
                            self.steps.append(ReportStep(
                                id=step_id,
                                file=rel_file,
                                line=getattr(node, 'lineno', -1),
                                pattern=pattern.strip(),
                            ))
                            self._built_index.setdefault(pattern.strip()[:10].lower(), []).append(step_id)
                            step_id += 1

    def _get_step(self, step_id: int) -> ReportStep:
        return self.steps[step_id - 1]

    @staticmethod
    def _extract_pattern(node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.JoinedStr):
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    parts.append(value.value)
                else:
                    parts.append('{…}')
            return ''.join(parts)
        return None

    @staticmethod
    def _match(pattern: str, message: str) -> bool:
        if pattern == message:
            return True
        if ' - attempt ' in message and ' - attempt ' in pattern:
            msg_action = message.split(' - attempt ')[0]
            pat_action = pattern.split(' - attempt ')[0].replace('{…}', '').strip()
            if pat_action and pat_action in msg_action:
                return True
        simplified = pattern.replace('{…}', '').strip()
        if simplified and simplified in message:
            return True
        return False

    def _extract_logger_call_pattern(self, file_path: str, lineno: int) -> Optional[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and getattr(node, 'lineno', -1) == lineno:
                    func = node.func
                    if isinstance(func, ast.Attribute) and func.attr == 'info':
                        if isinstance(func.value, ast.Name) and func.value.id == 'framework_logger':
                            if node.args:
                                return self._extract_pattern(node.args[0])
        except Exception:
            return None
        return None

    @property
    def report_path(self) -> str:
        return os.path.join(self.output_dir, 'report.html')

    def _generate_html(self):
        total = len(self.steps)
        passed = sum(1 for s in self.steps if s.status == 'PASS')
        failed = sum(1 for s in self.steps if s.status == 'FAIL')
        not_exec = sum(1 for s in self.steps if s.status == 'NOT_EXECUTED')
        now = datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z'
        console_output, console_meta = self._get_console_output()
        def esc(s: str) -> str: return html.escape(s, quote=True)
        rows_html = []
        status_color = {'PASS': '#ccffcc','FAIL': '#ffb3b3','NOT_EXECUTED': '#f2f2f2','PENDING': '#ffffff'}
        executed_steps = [s for s in self.steps if s.execution_order is not None]
        for s in executed_steps:
            if s.first_timestamp_dt is None and s.timestamp:
                try:
                    ts = s.timestamp.rstrip('Z')
                    s.first_timestamp_dt = datetime.datetime.fromisoformat(ts)
                except Exception:
                    pass
        executed_steps.sort(key=lambda s: (s.first_timestamp_dt or self._suite_start, s.execution_order or 0))
        prev_step = None
        for s in executed_steps:
            if prev_step and prev_step.duration_ms is None and prev_step.first_timestamp_dt and s.first_timestamp_dt:
                delta = (s.first_timestamp_dt - prev_step.first_timestamp_dt).total_seconds() * 1000
                if delta >= 0: prev_step.duration_ms = int(delta)
            prev_step = s
        pending_steps = [s for s in self.steps if s.execution_order is None]
        ordered_steps = executed_steps + pending_steps
        exec_display_index = {s.id: idx + 1 for idx, s in enumerate(executed_steps)}
        for step in ordered_steps:
            display_num = exec_display_index.get(step.id, '')
            rows_html.append(
                f"<tr style='background:{status_color.get(step.status, '#fff')}'>"
                f"<td>{display_num}</td>"
                f"<td>{esc(step.status)}</td>"
                f"<td>{esc(step.logged_message if step.logged_message else step.pattern)}</td>"
                f"<td>{esc(step.file)}:{step.line}</td>"
                f"<td>{esc(step.timestamp or '')}</td>"
                f"<td>{'' if step.duration_ms is None else step.duration_ms}</td>"
                f"<td>{step.occurrences if step.occurrences else ''}</td>"
            )
        html_doc = f"""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='utf-8'/>
  <title>AURA Test Report - {esc(self.flow_name)} - {esc(self.run_id)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 1rem 2rem; }}
    h1 {{ font-size: 1.4rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 4px 6px; font-size: 0.75rem; }}
    th {{ background: #333; color: #fff; position: sticky; top:0; }}
    .summary {{ margin-bottom: 1rem; }}
    .badge {{ padding: 4px 8px; border-radius: 4px; color:#fff; font-weight:600; }}
    .pass {{ background:#2d7d2d; }}
    .fail {{ background:#b30000; }}
    .skip {{ background:#666; }}
    .filter-input {{ margin-left:1rem; }}
    details pre {{ max-height:400px; overflow:auto; background:#111; color:#eee; padding:8px; font-size:0.7rem; }}
    details summary {{ cursor:pointer; font-weight:600; }}
  </style>
  <script>
    function filterTable() {{
      const q = document.getElementById('filter').value.toLowerCase();
      const rows = document.querySelectorAll('#steps tbody tr');
      rows.forEach(r => {{
        const txt = r.innerText.toLowerCase();
        r.style.display = txt.includes(q) ? '' : 'none';
      }});
    }}
  </script>
 </head>
 <body>
   <h1>AURA HTML Report - {esc(self.flow_name)} (run: {esc(self.run_id)})</h1>
   <div class='summary'>
     <strong>Generated:</strong> {esc(now)}<br/>
     <strong>Total Steps:</strong> {total} &nbsp; 
     <span class='badge pass'>Pass: {passed}</span> &nbsp;
     <span class='badge fail'>Fail: {failed}</span> &nbsp;
     <span class='badge skip'>Not Executed: {not_exec}</span>
     <input id='filter' class='filter-input' placeholder='Filter...' onkeyup='filterTable()'/>
   </div>
     <table id='steps'>
         <thead><tr><th>Exec#</th><th>Status</th><th>Test Steps</th><th>Location</th><th>Timestamp</th><th>Duration (ms)</th><th>Occur</th></tr></thead>
     <tbody>
       {''.join(rows_html)}
     </tbody>
   </table>
     <h2>Console Output</h2>
     <p style='font-size:0.75rem;'>Lines: {console_meta['lines']} | Size: {console_meta['bytes']} bytes{ ' (TRUNCATED)' if console_meta['truncated'] else ''}</p>
     <details open>
         <summary>Show/Hide Console Log</summary>
         <pre>{esc(console_output)}</pre>
     </details>
 </body>
</html>"""
        try:
            with open(self.report_path, 'w', encoding='utf-8') as f:
                f.write(html_doc)
        except Exception as e:
            framework_logger.error(f"Failed writing HTML report: {e}")

    def _write_json(self):
        try:
            json_path = os.path.join(self.output_dir, 'report.json')
            console_output, meta = self._get_console_output()
            with open(json_path, 'w', encoding='utf-8') as jf:
                json.dump({
                    'flow': self.flow_name,
                    'run_id': self.run_id,
                    'generated_utc': datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z',
                    'steps': [s.to_row() for s in self.steps],
                    'console': {
                        'truncated': meta['truncated'],
                        'bytes': meta['bytes'],
                        'lines': meta['lines'],
                        'content': console_output,
                    }
                }, jf, indent=2)
        except Exception as e:
            framework_logger.warning(f"Failed to write JSON report: {e}")

    def _get_console_output(self):
        raw = self.console_buffer.getvalue()
        truncated = False
        raw_bytes = raw.encode('utf-8')
        if len(raw_bytes) > self.CONSOLE_MAX_BYTES:
            head = raw_bytes[: int(self.CONSOLE_MAX_BYTES * 0.7)]
            tail = raw_bytes[-int(self.CONSOLE_MAX_BYTES * 0.25):]
            raw = head.decode('utf-8', errors='ignore') + '\n...<TRUNCATED>...\n' + tail.decode('utf-8', errors='ignore')
            truncated = True
        lines = raw.count('\n') + (1 if raw and not raw.endswith('\n') else 0)
        return raw, {
            'truncated': truncated,
            'bytes': len(raw.encode('utf-8')),
            'lines': lines
        }
