from BeautifulSoup import BeautifulSoup
soup = BeautifulSoup('''<ul>
 <li>An unrelated list
</ul>

<h1>Heading</h1>
<p>This is <b>the list you want</b>:</p>
<ul><li>The data you want</ul>''')

text_els = soup.findAll(text=True)
for text_el in text_els:
    print "========"
    text = str(text_el)
    newtext = text.replace('e', '_x_')
    text_el.replaceWith(newtext)
    print text_el
    print "========"
print type(soup.prettify())
