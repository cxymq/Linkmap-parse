#!usr/bin/python
## -*- coding: UTF-8 -*-
#
#
#

import os
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


def findClassNameByAddress(addressArray,file):

	# file = open(addressMap,'r')
	addressNameArray = []

	for address in addressArray:
		file.seek(0)
		find = False
		for line in file.readlines():
			if line.find(address) != -1:
				find = True
				continue
			if find and line.find("name") != -1:
				# print('binary: ', line)
				lineArray = line.split(' ')
				if len(lineArray) > 0:
					name = lineArray[len(lineArray) - 1].replace('\n','')
					print ("%s %s" %(address,name))
					addressNameArray.append((address,name))
				break
	return addressNameArray


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
	if checkAppBinary(args[0]):
		path = args[0]

		allClassFile = readAllClass(path)
		allClass = findAllClass(allClassFile)

		print(f'All class size:{len(allClass)}')

		usedClassFile = readUsedClass(path)
		usedClass = findAllClass(usedClassFile)

		print ('Used class size:%d' % (len(usedClass)))

		unUsedClass = list(set(allClass).difference(set(usedClass)))

		print ('Unused class size:%d' % (len(unUsedClass)))

		if len(unUsedClass) > 0:
			classNameFile = readClassName(path)
			address_name_array = findClassNameByAddress(unUsedClass,classNameFile)

	#Clean map file
	mapPath = os.path.abspath('map.txt')
	if os.path.isfile(mapPath):
		os.remove(mapPath)

	print("********** 二进制文件 解析结束*********")

	return address_name_array

# if __name__ == '__main__':



