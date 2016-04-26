pageTitle = "Bill"
page = open(pageTitle, 'r+')
links = []

for line in page.readlines(80):
  line = line[:-1]
  print(line.split(":"))
  links.append(line.split(": "))

page.close()
page = open(pageTitle, 'w')

#links = [ ["Brother", "Ben"], ["Age", "42 years"], ["Favourite colour", "octarine"] ]

for link in links:
    targetFile = open(link[1], 'w+')
    targetFile.write(link[0])
    targetFile.write(" of: ")
    targetFile.write(pageTitle)
    targetFile.write('\n')
    page.write(link[0]),
    page.write(": "),
    page.write(link[1])
    page.write('\n')
    
	       
page.close()