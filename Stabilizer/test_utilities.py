
import utilities

def test_modular_mean():
	print( utilities.modular_mean([1,  9,  11]) == 11.0 )
	print( utilities.modular_mean([2,  10, 0])	== 0.0	)
	print( utilities.modular_mean([3,  11, 1])	== 1.0	)
	print( utilities.modular_mean([4,  0,  2])	== 2.0	)
	print( utilities.modular_mean([5,  1,  3])	== 3.0	)
	print( utilities.modular_mean([6,  2,  4])	== 4.0	)
	print( utilities.modular_mean([7,  3,  5])	== 5.0	)
	print( utilities.modular_mean([8,  4,  6])	== 6.0	)
	print( utilities.modular_mean([9,  5,  7])	== 7.0	)
	print( utilities.modular_mean([10, 6,  8])	== 8.0	)
	print( utilities.modular_mean([11, 7,  9])	== 9.0	)
	print( utilities.modular_mean([0,  8,  10]) == 10.0 )
	# Totally symmetrical case
	print( utilities.modular_mean([0, 6]) == 3.0 )
	print( utilities.modular_mean([1, 11, 5, 7]) == 6.0 )
	# Negative mean angle
	print( utilities.modular_mean([-0.2], 1.0) == 0.8 )

def floats_are_equal(a, b):
	return abs(a - b) < 0.00001

def test_modular_distance():
	print( utilities.modular_distance(2, 7, 12) == 5 )
	print( utilities.modular_distance(7, 2, 12) == -5 )
	print( utilities.modular_distance(2, 9, 12) == -5 )
	print( utilities.modular_distance(9, 2, 12) == 5 )
	print( utilities.modular_distance(2, 8, 12) == 6 or utilities.modular_distance(2, 8, 12) == -6 )
	print( floats_are_equal(utilities.modular_distance(0.2, 0.69, 1.0), 0.49) )
	print( floats_are_equal(utilities.modular_distance(0.69, 0.2, 1.0), -0.49) )
	print( floats_are_equal(utilities.modular_distance(0.2, 0.71, 1.0), -0.49) )
	print( floats_are_equal(utilities.modular_distance(0.71, 0.2, 1.0), 0.49) )
	print( floats_are_equal(utilities.modular_distance(0.7, 0.2, 1.0), 0.5) or floats_are_equal(utilities.modular_distance(0.7, 0.2, 1.0), -0.5) )


if __name__ == '__main__':
	test_modular_mean()
	test_modular_distance()
