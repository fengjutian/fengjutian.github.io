import re
h = open(r'D:\github\fengjutian.github.io\_tmp\live_prompts.html', encoding='utf-8').read()
j = h.find('<script>')
k = h.find('</script>', j)
seg = h[j:k]
print(len(seg))
print(seg[:4000])
