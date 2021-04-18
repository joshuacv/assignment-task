# assignment-task
############-----------Robart: Task to be solved---------###############################


My approach:
Approach is based on partitioning space into smaller chunks and organising it
into a binary tree. This will enable adding and deleting lines easily. The
grid remains the same unlike approaches where the tree is built according to the
given line segments. 

Note: 
Solution is contained in Robart_task.py. It depends on naive.py to test the result against the 
obtained result.

Question 1: Finding the closest line segment to point p

	Step 1: Recursively traverse to the last leaf node containing the point and return it.
	Step 2: Recursively check which leaf nodes come in contact with the above box and return them too.
	Step 3: For those line segments in the relevant boxes, check distances naively.

Question 2: Finding the line segments in a distance range [dmin,dmax] from point p

	Step 1: Draw a box around the point with distance dmin.
	Step 2: Recursively check which leaf nodes come in contact with the above box and return them.
	Step 3: For those objects in the above boxes, check which ones are in range.
	Step 4: Repeat the same process for dmax
	Step 5: Delete the objects found with dmin from the objects found with dmax.

Question 3: Finding relative measures for lines coming within range d_lower

	Step 1: Traverse down the tree until d_lower is greater than the diagonal of the current box. 
	Step 2: Return all pairs in the box.
	Step 3: Traverse to the root node of the end node. Find the bisector of the root node box. Extend the bisector on both sides with distance d_lower/2.
	Step 4: Check which lines within this last root node intersects with the drawn box.
	Step 5: Return all lines pairs thus found.
	Step 6: While traversing, if the end of the tree is reached, check each object naively and return pairs that come closer than d_lower.