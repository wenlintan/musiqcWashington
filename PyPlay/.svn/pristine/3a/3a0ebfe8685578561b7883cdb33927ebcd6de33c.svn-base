--module Phone where 

import Data.List (elemIndex)

import Data.Array.Unboxed
import Data.Array.ST

import Control.Monad
import Control.Applicative

data Gaussian = Gaussian {
	gMean :: UArray Int Double,
	gSigma :: UArray Int Double,
    gNorm :: Double
	}

gaussianProbability :: Gaussian -> UArray Int Double -> Double
gaussianProbability gaussian feats = 
    let dx = zipWith (-) (elems $ gMean gaussian) (elems feats)
        dx2 = zipWith (*) dx dx
    in gNorm gaussian + sum (zipWith (/) dx2 (elems $ gSigma gaussian))

data Phone = Phone {
	pWeights :: [Double],
	pGaussians :: [Gaussian]
	}

phoneProbability :: Phone -> UArray Int Double -> Double
phoneProbability phone feats =
    let gs = map (flip gaussianProbability feats) (pGaussians phone)
        wgs = zipWith (*) gs (pWeights phone)
        m = maximum gs
    in log (sum $ map (exp . (`subtract` m)) wgs) + m

data Neighbor = Prev | Next deriving (Enum, Show, Eq)
data PhoneType = Vocative | SomethingElse deriving (Enum, Show, Eq)

data DecisionTree = Tree (Neighbor, PhoneType) DecisionTree DecisionTree |
    Leaf Phone
    
data Triphone = Triphone {
    tpName :: String,
    tpTypes :: [PhoneType],
	tpTransitions :: [Double],
	tpPhones :: [Phone]
	}

getPhone :: DecisionTree -> (Triphone, Triphone) -> Phone
getPhone (Tree (Prev, ptype) left right) args@(prev, _) =
    case (ptype `elemIndex` tpTypes prev) of
        Nothing -> getPhone left args
        Just _ -> getPhone right args
getPhone (Tree (Next, ptype) left right) args@(_, next) =
    case (ptype `elemIndex` tpTypes next) of
        Nothing -> getPhone left args
        Just _ -> getPhone right args
getPhone (Leaf phone) _ = phone

type DataArray = UArray (Int, Int) Double
data Workspace s = WS (STUArray s (Int, Int) Double) (STUArray s Int Double)
newWS nobs nphones = do
    let infinity = 1 / 0 :: Double
    result <- newArray ((0, 0), (nobs-1, nphones-1)) (-infinity)
    buffer <- newArray (0, nphones-1) (-infinity)
    return $ WS result buffer

forwardBackward :: DataArray -> [Triphone] -> DataArray
forwardBackward features triphones = runSTUArray $ do
    let (nobs, nfeatures) = (snd . bounds) features
    let infinity = 1 / 0 :: Double

    let phones = foldr ((++) . tpPhones) [] triphones
    let transitions = foldr ((++) . tpTransitions) [] triphones

    WS prob backbuffer <- newWS nobs (length phones)
    writeArray prob (0, 0) 0.0
    
    let feat i = ixmap (0, nobs-1) (\j -> (i, j)) features
    sequence $ (\row (col, trans, phone) -> do
        let p = phoneProbability phone (feat row)
        prev <- if col == 0 
            then return (-infinity)
            else (+ log trans) <$> readArray prob (row-1, col-1)
        same <- (+ log (1-trans)) <$> readArray prob (row-1, col)
        let m = max prev same
        writeArray prob (row, col) (log (exp (prev-m) + exp (same-m)) + m)) 
        <$> [0..nobs-1] <*> zip3 [0..] transitions phones

    writeArray backbuffer (length phones-1) 0.0
    forM_ [0..length phones-2] (\c -> writeArray prob (nobs-1, c) (-infinity))

    sequence $ (\row (col, trans, phone) -> do
        next <- if col == nfeatures-1
            then return (-infinity)
            else (+ log trans) <$> readArray backbuffer (col+1)
        same <- (+ log (1-trans)) <$> readArray backbuffer col

        let m = max next same
        let val = log (exp (next-m) + exp (same-m)) + m
        let p = phoneProbability phone (feat row)
    
        oldval <- readArray prob (row, col)
        writeArray prob (row, col) (oldval + val)
        writeArray backbuffer col (val + p))
        <$> [0..nobs-1] <*> zip3 [0..] transitions phones
    return $! prob 

updateTriphones :: [Triphone] -> DataArray -> DataArray -> [Triphone]
updateTriphones triphones features probs = 
    let (nobs, nfeatures) = (snd . bounds) features
        phones = foldr ((++) . tpPhones) [] triphones
        nphones = length phones
        ngaussians = length $ (pGaussians . head . tpPhones . head) triphones

        feat i = ixmap (0, nobs-1) (\j -> (i, j)) features

        prior :: Phone -> Int -> [Double]
        prior phone row =  
            let gaussians = pGaussians phone
                priors' = map (flip gaussianProbability (feat row)) gaussians
                m = maximum priors'
            in map (exp . (`subtract` m)) priors'

        phone_assocs :: Int -> (Int, Phone) -> 
            [((Int, Int, Int, Int), Double)]
        phone_assocs row (n, phone) =
            let x = feat row
                priors = prior phone row
                norm = sum priors
            in [((n, i, 0, 0), p/norm) | i <- [0..], p <- priors]

        triphone_assocs :: Int -> (Int, Triphone) -> 
            [((Int, Int, Int, Int), Double)]
        triphone_assocs row (n, triphone) = 
            foldl1 (++) $ map (phone_assocs row)
                (zip [n*3..] (tpPhones $ triphone))
            
        result = accumArray (+) 0 
            ((0, 0, 0, 0), (nphones, ngaussians, 3, nfeatures)) $
            foldl1 (++) (triphone_assocs <$> 
                [0..nobs-1] <*> zip [0..] triphones)
            :: UArray (Int,Int,Int,Int) Double

        extractPhone :: UArray (Int,Int,Int,Int) Double -> Int -> Phone
        extractPhone res p=
            Phone (map (\g -> res ! (p, g, 0, 0)) [0..ngaussians-1])
                (map (\g -> Gaussian 
                    (ixmap (0, nfeatures-1) (\i -> (p, g, 1, i)) res)
                    (ixmap (0, nfeatures-1) (\i -> (p, g, 2, i)) res) 0.0 )
                    [0..ngaussians-1])
    in map (\(i, phone) -> Triphone (tpName phone) (tpTypes phone)
        (tpTransitions phone)
        (extractPhone result <$> [i*3..i*3+2])) (zip [0..] triphones)
                    


main = print "yay"

