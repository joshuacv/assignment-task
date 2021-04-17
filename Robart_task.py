import numpy as np
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString
from shapely.geometry import box
import matplotlib.pyplot as plt
from naive import closest_among_lines,relative_measures,lines_in_distance_range

class Patch:
	#this is a class for the spatial tree
	def __init__(self,max_depth,level,bl,tr,obj= {}):
		self.max_depth = max_depth
		self.depth = level
		self.xmin,self.ymin,self.xmax,self.ymax = bl[0],bl[1],tr[0],tr[1]
		self.mybounds = box(bl[0],bl[1],tr[0],tr[1])
		self.objects = obj
		self.intersection_count = 0
		self.object_number = len(self.objects)
		self.myintersections() #check for intersections and delete unused objects
		if self.depth == max_depth or self.object_number <= 1:
			self.left = None
			self.right = None
		else:
			[b1,b2] = self.calculate_bisectors() #Calculate bisectors of the current box
			left_copy = self.objects.copy() #make a copy to avoid passing around original dictionary
			right_copy = self.objects.copy()
			self.left = Patch(self.max_depth,self.depth+1,b1[0],b1[1],left_copy) #create child node
			self.right = Patch(self.max_depth,self.depth+1,b2[0],b2[1],right_copy) #create child node
		
	def myintersections(self):
		#This function checks through all objects in the patch to see if any object intersects with boundaries
		#In case of intersections, the object is updated. If it is not contained in the new box, it is deleted.
		for element in list(self.objects):
			current_line = self.objects[element]
			if not self.mybounds.contains(current_line): 
				if self.mybounds.boundary.intersects(current_line):  
					self.objects[element] = self.mybounds.intersection(current_line)
				else:
					del self.objects[element]
		self.object_number = len(self.objects)
	

	def calculate_bisectors(self):
		#This function calcualtes the bisectors of the box. It returns the new boxes by halving the parent box
		if((self.xmax - self.xmin) >= (self.ymax - self.ymin)):
			split = (self.xmax - self.xmin)/2
			return [[(self.xmin,self.ymin),(self.xmin+ split,self.ymax)],[(self.xmin + split,self.ymin),(self.xmax,self.ymax)]]
		else:
			split = (self.ymax - self.ymin)/2
			return [[(self.xmin,self.ymin),(self.xmax,self.ymin+split)],[(self.xmin, self.ymin+split),(self.xmax,self.ymax)]]


	def closest_non_empty_tree(self,caller,x):
		#This function returns a box that is the smallest bounding box around the point x which has
		#atleast one element in it.
		if self.isinside(x) == False:
			return False
		if self.left == None or self.right == None:
			return self
		if self.object_number < 1:
			return caller
		if self.left.isinside(x) == True:
			return self.left.closest_non_empty_tree(self,x)
		if self.right.isinside(x) == True:
			return self.right.closest_non_empty_tree(self,x)

	def isinside(self,x):
		#This function returns True if point x is within the current box bounds.
		if self.mybounds.contains(x) == True:
			return True
		else:
			return False
		
	def trim_tree(self):
		#Since I implemented a fixed space partioning - some unnecessary boxes with no objects might be present. 
		#Removing them with this function.
		if self.left == None and self.right == None:
			return
		self.left.trim_tree()
		self.right.trim_tree()
		if self.left.object_number == 0 and self.right.object_number == 0:
			print("Trimming")
			self.left = None
			self.right = None
		return

	def ReturnObjectsAtLevel(self,level):
		left = []
		right = []
		if self.depth == level:
			return list(self.objects)
		if self.left and self.right == None:
			return left + right
		left = self.left.ReturnObjectsAtLevel(level)
		right = self.right.ReturnObjectsAtLevel(level)
		return left + right

	def ReturnGroundObjects(self):
		#Utility function to check if all objects are present at the ground boxes.
		if self.left == None and self.right == None:
			return list(self.objects)
		left = self.left.ReturnGroundObjects()
		right = self.right.ReturnGroundObjects()
		return left + right

	def box_neighbors(self,center_box):
		left = []
		right = []
		if self.left == None and self.right == None:
			if self.mybounds.boundary.intersects(center_box):
				return [self]
			return []
		left = self.left.box_neighbors(center_box)
		right = self.right.box_neighbors(center_box)
		return left  + right

	def closest_line_segment_correct(self,x):
		closest_containing_box = self.closest_non_empty_tree(self,x)
		close_tree_ends = self.box_neighbors(closest_containing_box.mybounds)
		min_dist = float('inf')
		closest_element_key = -1
		for mytree in close_tree_ends:
			for element in mytree.objects.keys():
				current_distance = mytree.objects[element].distance(x)
				if current_distance < min_dist:
					min_dist = current_distance
					closest_element_key = element
		#print(min_dist)
		if closest_element_key != -1:
			return [closest_element_key, self.objects[closest_element_key]]
		else:
			return [None,None]

	def leaves_at_distance_d(self,x,d):
		[(px,py)] = list(x.coords)
		box_of_interest = box(px-d,py-d,px+d,py+d) #box of interest is a square centered at point with sides = 2d
		boxes = self.box_neighbors(box_of_interest)
		return boxes


	def closest_line_segment(self,x):
		#If a point x is given function returns a list with closest line and its ID arranged according to the 
		#matrix provided
		if x.type != Point:
			x = Point(x)
		mytree = self.closest_non_empty_tree(self,x)
		min_dist = float('inf')
		closest_element_key = -1
		print(mytree.objects.keys()) 
		for element in mytree.objects.keys():
			current_distance = mytree.objects[element].distance(x)
			if current_distance < min_dist:
				min_dist = current_distance
				closest_element_key = element
		print(min_dist)
		if closest_element_key != -1:
			return [closest_element_key, self.objects[closest_element_key]]
		else:
			#print("No objects in the box")
			return [None,None]

	def lines_in_range_correct(self,x,dmin,dmax):
		#If a dmax and dmin are given, the function returns all the lines that are in 
		#range as a dictionary with the same line ids as columns in the matrix
		list_min_tree = self.leaves_at_distance_d(x,dmin)
		list_max_tree = self.leaves_at_distance_d(x,dmax)
		max_object_ids = []
		min_object_ids = [] # keys to avoid
		lines_of_interest = []
		for node in list_min_tree:
			for key in list(node.objects):
				if not key in min_object_ids:
					min_object_ids.append(key)
		for node in list_max_tree:
			for key in list(node.objects):
				if not key in min_object_ids:
					lines_of_interest.append(key)
		lines_of_interest = list( dict.fromkeys(lines_of_interest) ) ##removing duplicates possible in different boxes
		return {k:self.objects[k] for k in lines_of_interest if k in self.objects}

	
	def naively_check_relative_distances(self,dmin):
		result = {}
		keys = list(self.objects)
		len_keys = len(keys)
		for i in range(0,len_keys):
			current_close = []
			for j in range(0,len_keys):
				if (i != j) and (self.objects[keys[i]].distance(self.objects[keys[j]]) <= dmin):
					#print(f'{lines[keys[i]].distance(lines[keys[j]])}')
					current_close.append(keys[j])
			if len(current_close) > 0:
				current_close.sort()
				result[keys[i]] = current_close
		return result	
	
	def collect_pairs(self,dmin):
		#This function calculates relative measures on all lines present in the root node. 
		#The function then returns a dictionary of lines that are associated with each line ID
		left = []
		right = []
		if self.left == None and self.right == None:
			those_coming_close = {}
			diag_coords = list(self.mybounds.boundary.coords)
			diagonal = LineString([diag_coords[3],diag_coords[1]])
			if dmin < diagonal.length:
				those_coming_close = self.naively_check_relative_distances(dmin)
			else:
				for each in list(self.objects):
					those_coming_close[each] = list(self.objects).remove(each)
			return [those_coming_close]

		left = self.left.collect_pairs(dmin)
		right = self.right.collect_pairs(dmin)
		return left + right

	def isEmptylevel(self):
		if self.left == None and self.right == None:
			return
		self.left.isEmptylevel()
		self.right.isEmptylevel()
		if self.left.object_number == 0 and self.right.object_number == 0:
				print(f"Empty patch at level {self.depth}")
				return

def import_matrix():
#Utiliy function to import the matrix
	mat = []
	f = open("map.mat",'r')
	out = f.readline()
	while(out != ''):
		if out[0] == '#' or out[0] == '\n':
			out = f.readline()
			continue
		out = out.lstrip(' ')
		out = out.rstrip(' ')
		out = out.rstrip('\n')
		out = out.split(' ')
		mat.append(list(map(float, out)))
		out = f.readline()
	mat = np.matrix(mat)
	#print(mat.shape)
	f.close()
	return mat

def isMissingObjects(d):
	ret_list = []
	for i in range(0,100):
		if not i in d:
			ret_list.append(i)
	if len(ret_list) == 0:
		return [False, []]
	else:
		return [True, ret_list]



def CreateTree(levels):
	#Calls various function to create the with the maximum bounding box.
	global mat
	mat = import_matrix()
	global all_line_strings
	all_objects = {}
	all_line_strings = {}
	for col in range(0,mat.shape[1]):
		current = np.transpose(mat[:,col]).tolist()[0]
		all_line_strings[col] = LineString([tuple(current[0:3:2]),tuple(current[1:4:2])])
		all_objects[col] = current
	
	all_obj = np.matrix(list(all_objects.values()))
	xmax = all_obj[:,0:2].max() + 5
	xmin = all_obj[:,0:2].min() - 5
	ymax = all_obj[:,2:4].max() + 5
	ymin = all_obj[:,2:4].min() -5

	spatialTree = Patch(levels,0,(xmin,ymin),(xmax,ymax),all_line_strings.copy())
	spatialTree.trim_tree()
	spatialTree.isEmptylevel()
	return spatialTree

if __name__ == '__main__':

	tree_levels = 10
	spatialTree = CreateTree(tree_levels)
	##Testpoint##
	[px, py] = [120,600]
	dmin = 10
	dmax = 200
	dlower = 10
	[lid, line_object] = spatialTree.closest_line_segment_correct(Point(px,py))
	[lid_naive, line_object_naive] = closest_among_lines(all_line_strings.copy(),Point(px,py))
	assert lid == lid_naive,"Test with naive implementation failed"
	if lid != None:
		print(f"####################Task 1###################################\n")
		print(f"Closest line segment to Point {px},{py} is {all_line_strings[lid]}")
		print(f"Closest distance is {line_object.distance(Point(px,py))}")
	line_objects = spatialTree.lines_in_range_correct(Point(px,py),dmin,dmax)
	line_objects_naive = lines_in_distance_range(all_line_strings.copy(),Point(px,py),dmin,dmax)
	assert list(line_objects).sort() == list(line_objects_naive).sort(), "Lines within range are different"
	if len(line_objects) != 0:
		print(f"####################Task 2###################################\n")
		print(f"Lines in a range: \nThere are {len(line_objects)} in between distance range {dmin} and {dmax} from Point ({px},{py})")
		print(f"These line ids are {list(line_objects)}")
	else:
		print(f"No lines in this range")
	#relative_measures = spatialTree.close_line_pairs(10)
	relative_measures = spatialTree.collect_pairs(10)
	relative_measures_ordered = {}
	for i in range(0,100):
		current_collection = []
		for each in relative_measures:
			if i in each:
				current_collection += each[i]
		relative_measures_ordered[i] = current_collection
	print(f"####################Task 3###################################\n")
	print(f"Relative Measures")
	print(relative_measures_ordered)

