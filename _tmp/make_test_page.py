import re, pathlib

root = pathlib.Path(r"D:\github\fengjutian.github.io")
live = (root / "_tmp" / "live_prompts.html").read_text(encoding="utf-8")
md = (root / "_pages" / "prompts.md").read_text(encoding="utf-8")

# new script block from the markdown source
start_md = md.index("<script>")
new_script = md[start_md:].strip()

# replace the old modal markup + old script in the built page
start = live.index('<div class="prompt-modal" role="dialog"')
end_marker = "</script>"
end = live.index(end_marker, start) + len(end_marker)
patched = live[:start] + new_script + live[end:]

probe = """
<script>
  setTimeout(function () {
    var detail = document.querySelector(".prompt-detail");
    if (detail) detail.click();
    var m = document.querySelector(".prompt-modal");
    var shown = !!m && !m.hidden && getComputedStyle(m).display !== "none";
    document.body.setAttribute("data-modal-open", String(shown));
    document.body.setAttribute("data-modal-title", (m && m.querySelector(".prompt-modal-title").textContent) || "");
    document.body.setAttribute("data-modal-prompt-len", String((m && m.querySelector(".prompt-modal-prompt").textContent || "").length));
  }, 400);
</script>
"""
patched = patched.replace("</body>", probe + "</body>")
out = root / "_tmp" / "test_prompts.html"
out.write_text(patched, encoding="utf-8")
print(out, len(patched))
