h = open(r'D:\github\fengjutian.github.io\_tmp\live_prompts.html', encoding='utf-8').read()
j = h.find('const root = document.querySelector(".prompt-library")')
print(h[j:j + 5200])
