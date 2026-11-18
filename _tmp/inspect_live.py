import re
h = open(r'D:\github\fengjutian.github.io\_tmp\live_prompts.html', encoding='utf-8').read()
i = h.find('class="prompt-grid"')
print(h[i - 100:i + 300])
print('=====MODAL=====')
j = h.find('prompt-modal" role')
print(h[j - 500:j + 1500])
