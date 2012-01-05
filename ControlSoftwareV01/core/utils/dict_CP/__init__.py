import string

def convertSmartly(number_str):
    if number_str == "True":
        return True
    if number_str == "False":
        return False
    try :
        res = int(number_str)
    except ValueError:
        try:
            res = float(number_str)
        except ValueError:
            try:
                a=number_str.split(" ")
                value=float(a[0])
                temp=string.strip(a[1],"]")
                str_unit=string.strip(temp,"[")
                res=value*eval(str_unit)
            except ValueError:
                try:
                    a=number_str.split("*")
                    value=float(a[0])
                    str_unit=a[1]
                    res=value*eval(str_unit)
                except ValueError:
                    res = number_str
    return res



def saveDictToConfParser(d,c,section):
    c.add_section(section)
    for i in d:
        c.set(section,i,d[i])
        
        

def dictFromKwdsText(kwdsText):
    d = dict()
    kwdsText = str(kwdsText)
    if kwdsText == "" or kwdsText == None:
            return d
    args = kwdsText.split("\n")
    
    for i in args:
        (name,val) = i.split("=")
        val = val.strip()
        name = name.strip()
        d[name] = convertSmartly(val)
    return d


def configParserToDict(c,section):
    d = c._dict(c.items(section))
    for i in d:
       d[i] =  convertSmartly(d[i])
    return d

def mergeCPtoDict(cp):
    res = dict()
    for section in cp.sections():
        res.update(configParserToDict(cp,section))
    return res