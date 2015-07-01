
import Numeric.LinearAlgebra.HMatrix

main = do
	let m1 = fromLists [[1e-2, 1e-3], [1e-3, 1e-2]]
	let m2 = fromLists [[1, 2], [2, 1]]
	print $ invlndet m1
	print $ fst (invlndet m1) `mul` m1
	print $ det m1
	let m = m1 * m2 :: Matrix Double
	let muld = m1 `mul` m2 :: Matrix Double
	print m
	print muld
