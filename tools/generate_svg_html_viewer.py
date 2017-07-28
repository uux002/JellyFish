import os

svglist = []

for x in os.listdir('.'):
	if os.path.isfile(x) and os.path.splitext(x)[1] == '.svg':
		#print(x)
		svglist.append(x)

for svg in svglist:
	print(svg)

with open('svg_viewer.html','w') as f:
	f.write("<html>\n")
	f.write("<body>\n")
	for svg in svglist:
		f.write("<div>")
		f.write('<img src="%s" width="100" height="100" name="%s"/>\n' % (svg, svg))
		f.write("<span>%s" % svg)
		f.write("</div>")
	f.write("</body>\n")
	f.write("</html>\n")