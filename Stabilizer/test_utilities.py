
import utilities

def test_modular_mean():
	print( utilities.modular_mean([1,  9,  11]) == 11.0 )
	print( utilities.modular_mean([2,  10, 0])  == 0.0  )
	print( utilities.modular_mean([3,  11, 1])  == 1.0  )
	print( utilities.modular_mean([4,  0,  2])  == 2.0  )
	print( utilities.modular_mean([5,  1,  3])  == 3.0  )
	print( utilities.modular_mean([6,  2,  4])  == 4.0  )
	print( utilities.modular_mean([7,  3,  5])  == 5.0  )
	print( utilities.modular_mean([8,  4,  6])  == 6.0  )
	print( utilities.modular_mean([9,  5,  7])  == 7.0  )
	print( utilities.modular_mean([10, 6,  8])  == 8.0  )
	print( utilities.modular_mean([11, 7,  9])  == 9.0  )
	print( utilities.modular_mean([0,  8,  10]) == 10.0 )

	# Totally symmetrical case
	print( utilities.modular_mean([0, 6]) == 3.0 )
	print( utilities.modular_mean([1, 11, 5, 7]) == 6.0 )


if __name__ == '__main__':
	test_modular_mean()
