from urllib.request import urlopen
from urllib.parse import quote

s_diffs = ["GSP", "BSP", "DSP", "ESP", "CSP"]
d_diffs = ["BDP", "DDP", "EDP", "CDP"] 

class Song:
    def __init__(self, line, online = False):
        split = line.split("\t")
        # [id, -, GSP, BSP, DSP, ESP, CSP, BDP, DDP, EDP, CDP, title, artist]
        #  0   1  2    3    4    5    6    7    8    9    10   11     12
        self.id = split[0]
        self.singles = list(map(lambda x: int(x), split[2:7]))
        self.doubles = list(map(lambda x: int(x), split[7:11]))

        if online:
            try:
                self.title = fixtitle(split[11])
            except:
                self.title = "ERROR ERROR ERROR OH NO"
        else:
            self.title = translit(self.id)

        self.artist = split[12].strip()

    def charts_csv(self):
        result = ""
        for i in range(len(self.singles)):
            if self.singles[i] != -1:
                result += "%s [%s],, %s\n"%(self.title, s_diffs[i], str(self.singles[i]))
        for i in range(len(self.doubles)):
            if self.doubles[i] != -1:
                result += "%s [%s],, %s\n"%(self.title, d_diffs[i], str(self.doubles[i]))
        return result

    def __repr__(self):
        disp  = "Title: %s\n"%(self.title)
        disp += "Artist: %s\n"%(self.artist)

        #convert to strings
        singles = list(map(lambda x: str(x) if x > 0 else "-", self.singles))

        #difficulty labels
        for i in range(len(s_diffs)):
            disp += "{}: {:>2}  ".format(s_diffs[i],singles[i])
        
        disp += "\n" + " "*9 #offset for next line

        #convert to strings
        doubles = list(map(lambda x: str(x) if x > 0 else "-", self.doubles))

        #difficulty labels
        for i in range(len(d_diffs)):
            disp += "{}: {:>2}  ".format(d_diffs[i],doubles[i])

        return disp

def getfirststring(html):
    result = ""
    head = 0
    
    inquote = False
    #find opening quote
    while True:
        if html[head] == "\\": #escape char
            if inquote:
                result += html[head+1]
            head += 2
            continue
        elif html[head] == "\"":
            if not inquote: #opening quote
                inquote = True
                head += 1
                continue
            else: #closing quote
                break
        
        if inquote:
            result += html[head]
        head += 1
    return result

def fixtitle(title):
    url = "https://remywiki.com/index.php?search=" + title
    url = quote(url.encode('utf8'), ':/?=') #percent-encode the unicode characters
    html = urlopen(url).read()
    pagetitle = str(html).split("<title>")[1].split("</title>")[0]

    if "Search results" not in pagetitle:
        result = getfirststring('"' + pagetitle[:-11] + '"') #escape char handling
    else:
        searchheading = str(html).split("mw-search-result-heading")[1]
        searchheading = searchheading.split("title=")[1]
        result = getfirststring(searchheading)

    return result.replace("&amp;","&").replace("&#039;","'")

translitDict = {}

def translit(id):
    if translitDict == {}:
        f = open("song_list_fixed.csv")
        for line in f.readlines():
            if line[0] == "\ufeff":
                line = line[1:]
            line = line.strip()
            firstcomma = line.find(",") #only separate at first comma
            translitDict[line[:firstcomma]] = line[firstcomma+1:]
    return translitDict[str(id)] #they're strings, probably not good


def make_chart_list():
    f = open("master_music.txt")
    musiclines = f.readlines()
    f.close()
    f = open("chart_list.csv","w")
    for i in range(len(musiclines)):
        print("[%s/%s]"%(str(i),str(len(musiclines))))
        f.write(Song(musiclines[i]).charts_csv())

def make_song_list():
    f = open("master_music.txt")
    musiclines = f.readlines()
    f.close()
    f = open("song_list.csv","w")
    for i in range(len(musiclines)):
        print("[%s/%s]"%(str(i),str(len(musiclines))))
        f.write("%s,,%s\n"%(str(i),Song(musiclines[i]).title))