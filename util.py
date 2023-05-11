
def to_camel_case(textStr: str, firstToLower: bool = False ):
    if textStr is None:
        return ""
    s = textStr.replace("-", " ").replace("_", " ")
    sp = s.split(" ")
    r = sp[0]+ ''.join(i.capitalize() for i in sp[1:])
    return r if firstToLower else r[:1].capitalize() + r[1:]


'''
Convert JavaScript LAC to ALS Python
'''
def fixup(str):
    if str is None:
        return str
    newStr =  str.replace("oldRow","old_row",20)
    newStr = newStr.replace("logicContext","logic_row",20)
    newStr = newStr.replace("log.","logic_row.log.",20)
    newStr = newStr.replace("var","",20)
    newStr = newStr.replace("//","#",200)
    newStr = newStr.replace("createPersistentBean","logic_row.new_logic_row")
    newStr = newStr.replace(";","",200)
    newStr = newStr.replace("?"," if ",400)
    newStr = newStr.replace(":"," else ",400)
    newStr = newStr.replace("} else {","else:", 100)
    newStr = newStr.replace("}else {","else:", 100)
    newStr = newStr.replace(") {","):",40)
    newStr = newStr.replace("){","):",40)
    newStr = newStr.replace("function ","def ",40)
    newStr = newStr.replace("} else if","elif ")
    newStr = newStr.replace("}else if","elif ",20)
    newStr = newStr.replace("||","or",20)
    newStr = newStr.replace("&&","and",20)
    newStr = newStr.replace("}else{","else:", 20)
    newStr = newStr.replace("null","None",40)
    newStr = newStr.replace("===","==",40)
    newStr = newStr.replace("}","",40)
    newStr = newStr.replace("else  if ","elif", 20)
    newStr = newStr.replace("true","True", 30)
    newStr = newStr.replace("false","False", 30)
    newStr = newStr.replace("if (","if ", 30)
    newStr = newStr.replace("if(","if ",30)
    #newStr = newStr.replace("):",":", 30)
    newStr = newStr.replace("logic_row.verb == \"INSERT\"","logic_row.is_inserted() ")
    newStr = newStr.replace("logic_row.verb == \"UPDATE\"","logic_row.is_updated()")
    newStr = newStr.replace("logic_row.verb == \"DELETE\"","logic_row.is_deleted()")
    newStr = newStr.replace("JSON.stringify","jsonify",20)
    newStr = newStr.replace("JSON.parse","json.loads",20)
    newStr = newStr.replace("/*","'''", 20)
    newStr = newStr.replace("*/", "'''",20)
    newStr = newStr.replace("try {","try:", 10)
    newStr = newStr.replace("catch(e):","except Exception:", 5)
    newStr = newStr.replace("try{","try:", 10)
    newStr = newStr.replace("catch(","except Exception:", 5)
    # SysUtility ???
    return newStr.replace("log.debug(","log(",20)

