import os
import textwrap
import html
import sys

DATA_DIR = "/output/data"
OUT_DIR = "/output"
WAYBACK_LINES_PER_PAGE = 10
OTHER_LINES_PER_PAGE = 10
WAYBACK = "waybackurls.txt"
SUBZY_RESULTS = "subzy.txt"

SECTION_ORDER = [
    ("live_2xx_3xx_hosts.txt", "🌐 Live Subdomains (2xx/3xx Hosts)"),
    ("dns_info.txt",           "📡 DNS Records"),
    (SUBZY_RESULTS,            "🧪 Subdomain Takeover"),
    (WAYBACK,                  "📜 Wayback URLs"),
    ("whatweb.txt",            "🔍 Tech Stack"),
    ("waybackurls_filtered.txt", "🕵️ Filtered Sensitive Wayback URLs"),
]

HTML_HEADER = textwrap.dedent("""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} - Recon Report</title>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/static/style.css" />
</head>
<body>

  <div id="overlay-loader" class="loader-overlay" style="display: none;">
    <div class="loader"></div>
  </div>

  <canvas id="matrix-bg"></canvas>

  <header class="app-header">
    <div class="header-inner">
      <div class="header-left">
        <img src="https://bilishim.com/images/logo.png" class="logo-img" alt="Logo" />
        <span class="logo-text">Web Application Reconnaissance Portal</span>
      </div>

      <nav class="nav-links">
        <a href="/live_2xx_3xx_hosts">🌐 Subdomains</a>
        <a href="/dns_info">📡 DNS</a>
        <a href="/subzy">🧠 Takeovers</a>
        <a href="/waybackurls">📜 Wayback</a>
        <a href="/waybackurls_filtered">🕵️ Sensitive URLs</a>
        <a href="/whatweb">🔍 Tech Stack</a>
      </nav>

      <div class="header-right">
        <button class="btn btn-logout">Logout</button>
      </div>
    </div>
  </header>

  <main class="main-content container report-container">
    <div class="panel dashboard-content-box">
      <h2>{title}</h2>
""")

HTML_FOOTER = textwrap.dedent("""\
    </div>
  </main>

  <script src="/static/auth_flask.js"></script>
  <script src="/static/pagination.js"></script>
  {script_block}
</body>
</html>
""")

def process_and_write_file_content(input_path: str, outfile, is_subzy: bool):
    try:
        with open(input_path, "r", encoding="utf-8", errors="ignore") as infile:
            for line in infile:
                stripped_line = line.rstrip('\n')
                escaped_line = html.escape(stripped_line)
                if is_subzy and "[ VULNERABLE ]" in stripped_line:
                    outfile.write(f'<span class="vulnerable">{escaped_line}</span>\n')
                else:
                    outfile.write(escaped_line + '\n')
        return True
    except FileNotFoundError:
        print(f"[!] Missing data file: {input_path}", file=sys.stderr)
        outfile.write(html.escape(f"Data file not found: {os.path.basename(input_path)}"))
        return False
    except IOError as e:
        print(f"[!] Error reading file {input_path}: {e}", file=sys.stderr)
        outfile.write(html.escape(f"Error reading data file: {os.path.basename(input_path)}"))
        return False

def main():
    print("[*] Starting report generation...")
    processed_files = 0
    failed_files = 0

    for fname, title in SECTION_ORDER:
        input_path = os.path.join(DATA_DIR, fname)
        section_id = fname.removesuffix(".txt")
        output_html_path = os.path.join(OUT_DIR, f"{section_id}.html")

        try:
            os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
        except OSError as e:
            print(f"[!] Could not create output directory: {e}", file=sys.stderr)
            failed_files += 1
            continue

        is_wayback = (fname == WAYBACK)
        is_subzy = (fname == SUBZY_RESULTS)
        block_id = f"{section_id}-content"
        lines_per_page = WAYBACK_LINES_PER_PAGE if is_wayback else OTHER_LINES_PER_PAGE
        script_block = f'<script>document.addEventListener("DOMContentLoaded", () => paginatePreTabs("{block_id}", {lines_per_page}));</script>'

        print(f"[*] Processing: {fname} -> {os.path.basename(output_html_path)}")

        try:
            with open(output_html_path, "w", encoding="utf-8") as outfile:
                outfile.write(HTML_HEADER.format(title=title))

                if fname in [WAYBACK, "waybackurls_filtered.txt"]:
                    # Sadece download butonu
                    download_button_html = f'''
                    <div style="text-align: center; margin-top: 2rem;">
                        <a href="/{fname}" download class="btn btn-download">
                            📥 Download {title}
                        </a>
                    </div>
                    '''
                    outfile.write(download_button_html)
                    script_block = ''  # Sayfa script bloğu gerekmez
                else:
                    # Normal içerik + arama kutusu + filtre
                    outfile.write(f'''
                    <div class="search-container" style="text-align: center; margin: 1rem 0;">
                      <input type="text" id="searchInput-{block_id}" oninput="filterLines('{block_id}')" placeholder="🔍 Search...">
                    </div>
                    ''')
                    outfile.write(f'<pre id="{block_id}" class="wrapped-output hidden-block">\n')

                    success = process_and_write_file_content(input_path, outfile, is_subzy)
                    if not success:
                        failed_files += 1

                    outfile.write('\n</pre>\n')

                outfile.write(HTML_FOOTER.format(script_block=script_block))

            print(f"[+] Generated: {output_html_path}")
            processed_files += 1

        except IOError as e:
            print(f"[!] Error writing output file {output_html_path}: {e}", file=sys.stderr)
            failed_files += 1
        except Exception as e:
            print(f"[!] Unexpected error processing {fname}: {e}", file=sys.stderr)
            failed_files += 1

    print("-" * 30)
    print(f"[*] Report generation finished.")
    print(f"[*] Successfully processed: {processed_files} files.")
    if failed_files > 0:
        print(f"[!] Failed/Skipped: {failed_files} files (check logs above).")
    print("-" * 30)

if __name__ == "__main__":
    main()
    sys.exit(0)
