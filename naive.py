from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import LineString
import numpy as np
import matplotlib.pyplot as plt

def return_plot(myobjects):
	for each in myobjects.values():
		x,y = each.xy
		plt.plot(x,y,)
	
	plt.show()

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

def closest_among_lines(lines,point):
	min_dist = float('inf')
	closest_element_key = -1 
	for element in lines.keys():
		current_distance = lines[element].distance(point)
		if current_distance < min_dist:
			min_dist = current_distance
			closest_element_key = element
	#print(min_dist)
	if closest_element_key != -1:
		return [closest_element_key, lines[closest_element_key]]
	else:
		print("No objects in the box")
		return [None,None]

def lines_in_distance_range(lines,point,dmin,dmax):
	lines_coming_close = {}
	for element in lines.keys():
		current_distance = lines[element].distance(point)
		if current_distance <= dmax and current_distance >=dmin:
			lines_coming_close[element] = lines[element]
	return lines_coming_close

def relative_measures(lines,dmin):
	keys = list(lines)
	len_keys = len(keys)
	those_coming_close = {}
	for i in range(0,len_keys):
		current_close = []
		for j in range(0,len_keys):
			if (i != j) and (lines[keys[i]].distance(lines[keys[j]]) <= dmin):
				#print(f'{lines[keys[i]].distance(lines[keys[j]])}')
				current_close.append(keys[j])
		those_coming_close[i] = current_close	
	return those_coming_close


if __name__ == '__main__':
	global mat
	mat = import_matrix()
	global all_objects
	all_objects = {}
	for col in range(0,mat.shape[1]):
		all_objects[col] = np.transpose(mat[:,col]).tolist()[0]
	for element in all_objects.keys():
		if all_objects[element] != "LineString":
			current_line = LineString([tuple(all_objects[element][0:3:2]),tuple(all_objects[element][1:4:2])])
			all_objects[element] = current_line
	[px, py] = [120,600]
	dmin = 10
	dmax = 200
	dlower = 10
	[lid, line_object] = closest_among_lines(all_objects.copy(),Point(px,py))
	if lid != None:
		print(f"Closest line segment to Point {px},{py} is {lid}\n\n")
	line_objects = lines_in_distance_range(all_objects.copy(),Point(px,py),dmin,dmax)
	if len(line_objects) != 0:
		print(f"Lines in a range: \n There are {len(line_objects)} in between distance range {dmin} and {dmax} from Point ({px},{py})")
		print(f"Line ids are {list(line_objects)}")
	else:
		print(f"No lines in this range")

	rms = relative_measures(all_objects.copy(),10)
	print(rms)
	#return_plot(all_objects.copy())

