#!usr/bin/python
## -*- coding: UTF-8 -*-

import os
import re
import shutil
import sys

# 0KB
THRESHOLD_SIZE = 0.0 

class SymbolModel:
    file = ""
    size = 0
    address = ''

def verify_linkmapfile(args):
    if len(args) < 2:
        print("请输入linkMap文件")
        return False

    path = args

    if not os.path.isfile(path):
        print("请输入文件")
        return False

    file = open(path, encoding='mac-roman')
    content = file.read()
    file.close()

    #查找是否存在# Object files:
    if content.find("# Object files:") == -1:
        print("输入linkmap文件非法")
        return False
    #查找是否存在# Sections:
    if content.find("# Sections:") == -1:
        print("输入linkmap文件非法")
        return False
    #查找是否存在# Symbols:
    if content.find("# Symbols:") == -1:
        print("输入linkmap文件非法")
        return False

    return True 

def symbolMapFromContent(path):
    symbolMap = {}
    reachFiles = False
    reachSections = False
    reachSymblos = False
    file = open(path, encoding='mac-roman')
    for line in file.readlines():
        if line.startswith("#"):
            if line.startswith("# Object files:"):
                reachFiles = True
            if line.startswith("# Sections:"):
                reachSections = True
            if line.startswith("# Symbols:"):
                reachSymblos = True
        else:
            if reachFiles == True and reachSections == False and reachSymblos == False:
                #查找 files 列表，找到所有.o文件
                location = line.find("]")
                if location != -1:
                    key = line[:location+1]
                    if  symbolMap.get(key) is not None:
                        continue
                    symbol = SymbolModel()
                    symbol.file = line[location + 1:]
                    symbolMap[key] = symbol
            elif reachFiles == True and reachSections == True and reachSymblos == True:
                #'\t'分割成三部分，分别对应的是Address，Size和 File  Name
                symbolsArray = line.split('\t')
                if len(symbolsArray) == 3:
                    fileKeyAndName = symbolsArray[2]
                    #16进制转10进制
                    size = int(symbolsArray[1],16)
                    location = fileKeyAndName.find(']')
                    if location != -1:
                        key = fileKeyAndName[:location + 1]
                        symbol = symbolMap.get(key)
                        if len(symbol.address) <= 0 and ('_OBJC_CLASS_$_' in fileKeyAndName):
                            symbol.address = symbolsArray[0]
                        if symbol is not None:
                            symbol.size = symbol.size + size
    file.close()
    return symbolMap

def sortSymbol(symbolList):
     return sorted(symbolList, key=lambda s: s.size,reverse = True)

def buildResultWithSymbols(symbols, args):
    results = ["文件大小\t文件名称\r\n"]
    totalSize = 0
    memory_limit = 0
    if args ==0 or len(args) > 0:
        memory_limit = float(args)
    for symbol in symbols:
        if (symbol.size/1024.0) > memory_limit:
            results.append(calSymbol(symbol))
            totalSize += symbol.size
    results.append("总大小: %.2fM" % (totalSize/1024.0/1024.0))
    return results

def buildCombinationResultWithSymbols(symbols, args):
    #统计不同模块大小
    results = ["库大小\t库名称\r\n"]
    totalSize = 0
    combinationMap = {}

    for symbol in symbols:
        names = symbol.file.split('/')
        name = names[len(names) - 1].strip('\n')
        location = name.find("(")
        if name.endswith(")") and location != -1:
            component = name[:location]
            combinationSymbol = combinationMap.get(component)
            if combinationSymbol is None:
                combinationSymbol = SymbolModel()
                combinationMap[component] = combinationSymbol

            combinationSymbol.file = component
            combinationSymbol.size = combinationSymbol.size + symbol.size
        else:
            #symbol可能来自app本身的目标文件或者系统的动态库
            combinationMap[symbol.file] = symbol
    sortedSymbols = sortSymbol(combinationMap.values())

    search_module = ''
    memory_limit = 0
    if len(args) > 1:
        search_module = args[1]
    if len(args) > 2:
        memory_limit = float(args[2])

    for symbol in sortedSymbols:
        if len(search_module) > 0 and search_module in symbol.file and (symbol.size/1024.0) > memory_limit:
            results.append(calSymbol(symbol))
            totalSize += symbol.size
    results.append("总大小: %.2fM" % (totalSize/1024.0/1024.0))

    return results

def calSymbol(symbol):
    size = ""
    if symbol.size / 1024.0 / 1024.0 > 1:
        size = "%.2fM" % (symbol.size / 1024.0 / 1024.0)
    else:
        size = "%.2fK" % (symbol.size / 1024.0)
    names = symbol.file.split('/')
    if len(names) > 0:
        size = "%s\t%s" % (size,names[len(names) - 1])
    return size

def analyzeLinkMap(args):
    if verify_linkmapfile(args[0]) == True:
        print("********** linkmap 正在开始解析*********")
        symbolDic = symbolMapFromContent(args[0])
        symbolList = sortSymbol(symbolDic.values())
        if len(args) >= 3 and args[1] == "-g":
            results = buildCombinationResultWithSymbols(symbolList)
        else:
            results = buildResultWithSymbols(symbolList)
        for result in results:
            print(result)
        print("***********linkmap 解析结束***********")
        print("***********打印 linkmap ***********")
        model = SymbolModel()
        for sym in symbolDic:
            print(sym)
            model = symbolDic.get(sym)
            names = model.file.split('/')
            if len(names) > 0:
                print(model.address, '***', names[len(names) - 1])
        print("***********打印 linkmap ***********")
        return  symbolList

def analyzeLinkMap2(args):
    if verify_linkmapfile(args[0]) == True:
        print("********** linkmap 正在开始解析*********")
        symbolDic = symbolMapFromContent(args[0])
        symbolList = sortSymbol(symbolDic.values())
        if len(args) >= 2 and args[1] == "-g":
            results = buildCombinationResultWithSymbols(symbolList, args[1:])
        else:
            if len(args) >= 2:
                results = buildResultWithSymbols(symbolList, args[1])
            else:
                results = buildResultWithSymbols(symbolList, 0)
        for result in results:
            print(result)
        return [1, results]
    else:
        return [0, '输入link map文件非法']
# if __name__ == "__main__":
#     analyzeLinkMap()
