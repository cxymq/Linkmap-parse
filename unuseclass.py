#!usr/bin/python
## -*- coding: UTF-8 -*-
#
#
#

import os
import re
import sys


def findAllClass(file):

	result = False

	returnResult = []
	
	for line in file.readlines():
		
		if line.find("architecture arm64") != -1:
			result = True
			continue
		if result:
			contents = line.split('	')
			addressArray = []
			if len(contents) > 1:
				addressArray.extend(contents[1].split(' '))
			for address in addressArray:
				if address == '00000001':
					continue
				if address != '\n':
					returnResult.append(address)
				
	return returnResult

def findUsedClass(file):
	
	result = False

	returnResult = []
	
	for line in file.readlines():
		
		if line.find("architecture arm64") != -1:
			result = True
			continue
		if result:
			contents = line.split('	')
			addressArray = []
			if len(contents) > 1:
				addressArray.extend(contents[1].split(' '))
			for address in addressArray:
				if address == '00000001':
					continue
				if address == '00000000':
					continue
				if address != '\n':
					returnResult.append(address)
				
	return returnResult


def findClassNameByAddress(addressArray, file):

	# file = open(addressMap,'r')
	addressNameArray = ['未使用类如下（有误差，一定要人工筛选）：']

	for address in addressArray:
		# file.seek(0)
		# find = False
		# for line in file.readlines():
		# 	if line.find(address) != -1:
		# 		find = True
		# 		continue
		# 	if find and line.find("name") != -1:
		# 		# print('binary: ', line)
		# 		lineArray = line.split(' ')
		# 		if len(lineArray) > 0:
		# 			name = lineArray[len(lineArray) - 1].replace('\n','')
		# 			print ("%s %s" %(address,name))
		# 			addressNameArray.append((address,name))
		# 		break
		if file.get(address):
			file_name = file[address]
			addressNameArray.append(file_name)
	return addressNameArray

def class_symbols(path):
  symbols = {}
  #class symbol format from nm: 0000000103113f68 (__DATA,__objc_data) external _OBJC_CLASS_$_EpisodeStatusDetailItemView
  re_class_name = re.compile('(\w{16}) .* _OBJC_CLASS_\$_(.+)')
  lines = os.popen('nm -nm %s' % path).readlines()
  for line in lines:
    result = re_class_name.findall(line)
    if result:
      (address, symbol) = result[0]
      symbols[address[8:]] = symbol
  return symbols

def checkAppBinary(argv):
	if len(argv) < 2:
		print('输入有效地址')
		return False

	path = argv
	print(f'path = {path}')

	if not os.path.isfile(path):
		print ('文件不存在')
		return False
	return True

def readAllClass(path):
	file = os.popen('otool -v -s __DATA	__objc_classlist %s' % (path))

	return file

def readUsedClass(path):
	file = os.popen('otool -v -s __DATA	__objc_classrefs %s' % (path))
	return file

def readAllMethods(path):
	file = os.popen('otool -v -s __DATA	__objc_selrefs %s' % (path))
	return file

def readClassName(path):
	file = os.popen('otool -o %s' % (path))

	content = file.read()
	file.close()

	fo = open('map.txt', "w")
	fo.write(content)
	fo.close()

	return open(os.path.abspath('map.txt'))

def analyzeBinary(args):
	print("********** 二进制文件 正在开始解析*********")
	address_name_array = []
	if checkAppBinary(args):
		path = args

		allClassFile = readAllClass(path)
		allClass = findAllClass(allClassFile)

		print(f'All class size:{len(allClass)}')
		address_name_array.append('All class size:{len(allClass)}')

		usedClassFile = readUsedClass(path)
		usedClass = findAllClass(usedClassFile)

		print ('Used class size:%d' % (len(usedClass)))
		address_name_array.append('Used class size:%d' % (len(usedClass)))

		unUsedClass = list(set(allClass).difference(set(usedClass)))

		print ('Unused class size:%d' % (len(unUsedClass)))
		address_name_array.append('Unused class size:%d' % (len(unUsedClass)))

		if len(unUsedClass) > 0:
			# classNameFile = readClassName(path)
			classNameFile = class_symbols(path)
			address_name_array.extend(findClassNameByAddress(unUsedClass, classNameFile))

	#Clean map file
	mapPath = os.path.abspath('map.txt')
	if os.path.isfile(mapPath):
		os.remove(mapPath)

	print("********** 二进制文件 解析结束*********")

	return address_name_array

# if __name__ == '__main__':



