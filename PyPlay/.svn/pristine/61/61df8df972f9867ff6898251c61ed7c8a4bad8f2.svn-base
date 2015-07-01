
module EM where

import Debug.Trace
import Data.Random.Normal

import Data.List
import Data.Map.Strict (Map)
import qualified Data.Map.Strict as Map

--import Data.Matrix (Matrix)
--import qualified Data.Matrix as Matrix

import Data.Packed.Matrix (Matrix)
import qualified Data.Packed.Matrix as Matrix
import Data.Packed.Vector (Vector)
import qualified Data.Packed.Vector as Vector
import qualified Data.Packed.ST as MatrixST

import qualified Numeric.LinearAlgebra.Data as HMData
import qualified Numeric.LinearAlgebra.HMatrix as HM

import Data.List.Extras.Argmax (argmax, argmaxWithMax)
--import Data.Maybe

import Control.Monad
import Control.Monad.ST (runST)
import Control.Applicative
import Control.Parallel

type Observation = [Double]

data HMM a b = HMM {
    states :: [a],
    observations :: [b],
    start :: ![Double], --a -> Double,
    transitions :: ![[Double]], --a -> a -> Double,
    emissions :: ![Map b Double] --a -> b -> Double
    }

viterbi :: Ord b => HMM a b -> [b] -> [[Double]] --[a->Double]
viterbi hmm obs = viterbi' hmm (tail obs) [prob]
    where prob = zipWith (\s m -> s * (m Map.! head obs)) 
            (start hmm) (emissions hmm)

viterbi' :: Ord b => HMM a b -> [b] -> [[Double]] -> [[Double]]
viterbi' _ [] probs = probs
viterbi' _ _ [] = error "Do not call viterbi' directly"
viterbi' hmm (obs:rest) allprobs@(probs:_) = 
    let prevprob = zipWith (\ts p -> map (*p) ts) 
            (transitions hmm) probs
        maxprev = map maximum (transpose prevprob)
        prob' = zipWith (\p m -> p * (m Map.! obs))
            maxprev (emissions hmm)
        prob = map (/ sum prob') prob'
    in viterbi' hmm rest (prob : allprobs)

logSum :: [Double] -> Double
logSum l = 
    let m = max (maximum l) (-1e100)
    in (log . sum . map (exp . (subtract m))) l + m

approxLogSum :: [Double] -> Double
approxLogSum = maximum

viterbi'' :: Ord b => HMM a b -> [[Double]] -> ([a], Double)
viterbi'' hmm obs = 
    let output' emis o = logSum $ zipWith (\p c -> p + log (emis Map.! c))
            o (observations hmm)
        output = map (mapM output' (emissions hmm)) obs ::[[Double]]

        initial = zipWith (\st emis -> log st + emis) 
                (start hmm) (head output)
        v prob emis = zipWith (+) emis
            (map maximum (transpose $
                zipWith (\ts p -> map ((+p) .log) ts) 
            (transitions hmm) prob))
        probs = scanl v initial (tail output)

        nstates = length (states hmm)
        final = argmax (last probs !!) [0..nstates-1]
        x prob t = argmax (\s -> log (transitions hmm !! s !! t) + prob !! s)
            [0..nstates-1]
    in (map (states hmm !!) (scanr x final (init probs)),maximum $ last probs)

viterbiST :: Ord b => HMM a b -> Matrix Double -> ([a], Double)
viterbiST hmm obs = obs `seq`
    let nobs = Matrix.rows obs
        ncomps = length $ observations hmm
        nstates = length $ states hmm

        probs = MatrixST.runSTMatrix (do
            prob <- MatrixST.newMatrix (0.0 :: Double) nobs nstates
            let initial col (st, emis) = do
                    let outp = logSum $ zipWith (\i c ->
                            (obs Matrix.@@> (0, i))+ log (emis Map.! c))
                            [0..] (observations hmm)
                    MatrixST.writeMatrix prob 0 col (log st + outp)
            zipWithM_ initial [0 ..] $ zip (start hmm) (emissions hmm)
            let v row (col, ts, emis) = do
                    let outp = logSum $ zipWith (\i c ->
                            (obs Matrix.@@> (row, i))+ log (emis Map.! c))
                            [0..] (observations hmm)
                    val <- maximum <$> zipWithM (\col' t -> (+ log t) <$> 
                        MatrixST.readMatrix prob (row-1) col')
                        [0..] ts
                    MatrixST.writeMatrix prob row col (val + outp)
            sequence $ v <$> [1 .. nobs-1] <*> zip3 [0..] 
                (transpose $ transitions hmm) (emissions hmm)
            return $! prob
            )

        (final, totalprob) = argmaxWithMax 
            (\s -> probs Matrix.@@> (nobs-1, s)) [0..nstates-1]
        x row t = argmax (\s -> log (transitions hmm !! s !! t) + 
            probs Matrix.@@> (row, s)) [0..nstates-1]
    in (map (states hmm !!) (scanr x final [0..nobs-2]), totalprob)

hmmProbabilities :: Ord b => HMM a b -> [[Double]] -> [[Double]]
hmmProbabilities hmm obs =
    let output' emis o = logSum $ zipWith (\p c -> p + log (emis Map.! c))
            o (observations hmm)
        output = map (mapM output' (emissions hmm)) obs ::[[Double]]
 
        initial = zipWith (\st emis -> log st + emis) 
            (start hmm) (head output)
        alpha prob emis = zipWith (+) emis
            (map logSum (transpose $
                zipWith (\ts p -> map ((+p) . log) ts) 
                (transitions hmm) prob))
        forward = scanl alpha initial (tail output) :: [[Double]]

        nstates = length (states hmm)
        final = replicate (nstates-1) (log 0) ++ [0.0]
        beta o prob = map (\ts -> logSum (zipWith3 
            (\p t emis -> p + emis + log t)
            prob ts o)) (transitions hmm)
        backward = scanr beta final (tail output) :: [[Double]]

        outputs = zipWith (\fs bs ->
            map (\c -> logSum $ zipWith3 (\f b emis -> 
                f + b + log (emis Map.! c)) fs bs (emissions hmm))
            (observations hmm)) forward backward
    in outputs --zipWith (zipWith (+)) forward backward 

hmmProbabilitiesST :: Ord b => HMM a b -> Matrix Double -> Matrix Double
hmmProbabilitiesST hmm obs = obs `seq`
    let nobs = Matrix.rows obs
        ncomps = length $ observations hmm
        nstates = length $ states hmm

        probs = MatrixST.runSTMatrix (do
            output <- MatrixST.newMatrix (0.0 :: Double) nobs nstates
            let output' row (col, emis) = do
                    let val = logSum $ zipWith (\i c ->
                            (obs Matrix.@@> (row, i)) + log (emis Map.! c))
                            [0..] (observations hmm)
                    MatrixST.writeMatrix output row col val
            sequence $ output' <$> [0 .. nobs-1] <*> zip [0..] (emissions hmm)

            prob <- MatrixST.newMatrix (0.0 :: Double) nobs nstates
            let initial col st = do
                    outp <- MatrixST.readMatrix output 0 col
                    MatrixST.writeMatrix prob 0 col (log st + outp)
            zipWithM_ initial [0 ..] (start hmm)
            let alpha row (col, ts) = do
                    outp <- MatrixST.readMatrix output row col
                    val <- logSum <$> zipWithM (\col' t -> (+ log t) <$> 
                        MatrixST.readMatrix prob (row-1) col')
                        [0..] ts
                    MatrixST.writeMatrix prob row col (val + outp)
            sequence $ alpha <$> [1 .. nobs-1] <*> zip [0..] 
                (transpose $ transitions hmm)

            backward <- MatrixST.newMatrix (log 0 :: Double) nobs nstates
            MatrixST.writeMatrix backward (nobs-1) (nstates-1) 0.0
            forM_ [0..nstates-2] (\c -> MatrixST.modifyMatrix prob
                (nobs-1) c (+log 0))
            let beta row (col, ts) = do
                    val <- logSum <$> zipWithM (\col' t -> (+log t) <$>
                        ((+) <$> MatrixST.readMatrix output (row+1) col' <*>
                        MatrixST.readMatrix backward (row+1) col'))
                        [0..] ts
                    MatrixST.writeMatrix backward row col val
                    MatrixST.modifyMatrix prob row col (+val)
            sequence $ beta <$> [nobs-2, nobs-3 ..0] <*> zip [0..]
                (transitions hmm)

            emis <- MatrixST.newMatrix (0.0 :: Double) nobs ncomps
            let emis' row (col, comp) = do
                    val <- logSum <$> zipWithM (\col' emis'' ->
                        (+ log (emis'' Map.! comp)) <$>
                        MatrixST.readMatrix prob row col') 
                        [0..] (emissions hmm)
                    MatrixST.writeMatrix emis row col val
                    
            sequence $ emis' <$> [0..nobs-1] <*> zip [0..] (observations hmm)
            return $! emis
            )
    in probs

viterbiList :: (Show a, Ord b) => [(HMM a b, Int)] -> 
    [[Double]] -> ([[Double]], Double)
viterbiList [] _ = ([], 0.0)
viterbiList [(hmm1, nobs1)] obs =
    let p1 = hmmProbabilities hmm1 (take nobs1 obs)
        v1 = viterbi'' hmm1 (take nobs1 obs)
    in (p1, snd v1)
viterbiList ((hmm1, nobs1): (hmm2, nobs2): rest) obs =
    let p1 = hmmProbabilities hmm1 (take nobs1 obs)
        v1 = viterbi'' hmm1 (take nobs1 obs)
        p2 = hmmProbabilities hmm2 (take nobs2 (drop nobs1 obs))
        v2 = viterbi'' hmm2 (take nobs2 (drop nobs1 obs))
        d = viterbiList rest (drop (nobs1 + nobs2) obs)
    in par p1 (pseq p2 (p1 ++ p2 ++ fst d, snd v1 + snd v2 + snd d))

viterbiListST :: (Show a, Ord b) => [(HMM a b, Int)] -> 
    Matrix Double -> ([[Matrix Double]], Double)
viterbiListST [] _ = ([], 0.0)
viterbiListST ((hmm1, nobs1): rest) obs =
    let p1 = hmmProbabilitiesST hmm1 (Matrix.takeRows nobs1 obs)
        v1 = viterbiST hmm1 (Matrix.takeRows nobs1 obs)
        d = viterbiListST rest (Matrix.dropRows nobs1 obs)
    in par p1 (pseq d ([p1] : fst d, snd v1 + snd d))

data NormalDistribution = ND {
    mu :: !(Vector Double),
    sigma :: !(Matrix Double),
    invSigma :: !(Matrix Double),
    logDetSigma :: Double,
    norm :: Double } deriving (Show)

normalDistr :: [Double] -> Matrix Double -> NormalDistribution
normalDistr mean covariance = ND {
    mu = Vector.fromList mean,
    sigma = covariance,
    invSigma = inverse,
    logDetSigma = logdet,
    norm = (-0.5) * log (2 * pi) * nfeats - 0.5 * logdet }
    where (inverse, (logdet, _)) = HM.invlndet covariance
          nfeats = fromIntegral . length $ mean

ndLogDensity :: NormalDistribution -> [Double] -> Double
ndLogDensity nd xs = -0.5 * e + norm nd
    where xm = Vector.fromList xs - mu nd
          e = xm `HM.dot` (invSigma nd HM.#> xm)

ndLogDensityST :: NormalDistribution -> Vector Double -> Double
ndLogDensityST nd xs = -0.5 * e + norm nd
    where xm = xs - mu nd
          e = xm `HM.dot` (invSigma nd HM.#> xm)
    
data GMM a = GMM {
    components :: [a],
    nds :: ![NormalDistribution] }

gaussianMixture :: [a] -> [[Double]] -> [Matrix Double] -> GMM a
gaussianMixture cs ms ss = GMM {
    components = cs,
    nds = zipWith normalDistr ms ss }

gmmLogProb :: GMM a -> [Double] -> [Double]
gmmLogProb gmm xs = map (`ndLogDensity` xs) $ nds gmm

gmmLogProbST :: GMM a -> Vector Double -> Vector Double
gmmLogProbST gmm xs = Vector.fromList (map (`ndLogDensityST` xs) $ nds gmm)

gmmUpdate :: GMM a -> [[Double]] -> [[Double]] -> GMM a
gmmUpdate gmm obs probs = gaussianMixture (components gmm) means' sigmas'
    where small_norm l = 
            let m = negate $ maximum l
                d = sum $ map (exp . (+m)) l
            in map ((/d) . exp . (+m)) l

          ts = map small_norm probs
          totals = foldl1' (zipWith (+)) ts
          xc = zipWith (\tc x -> map (\t -> map (*t) x) tc) ts obs

          means' :: [[Double]]
          means' = zipWith (\x t -> map (/t) x) 
            (foldl1' (zipWith (zipWith (+))) xc) totals

          sigmas' :: [Matrix Double]
          ss tc x = zipWith (\t u -> HM.scale t
            (HM.col x - HM.col u) HM.<> (HM.row x - HM.row u))
            tc means'

          sigmas'' = foldl1' (zipWith (+)) (zipWith ss ts obs)
          sigmas' = zipWith (\t m -> HM.scale (1/t) m) totals sigmas''

gmmUpdateST :: GMM a -> Matrix Double -> Matrix Double -> GMM a
gmmUpdateST gmm obs probs = 
    let nobs = Matrix.rows obs
        nfeats = Matrix.cols obs
        ncomps = Matrix.cols probs

        smallNorm l =
            let m = negate $ HMData.maxElement l
                expd = Vector.mapVector (exp . (+m)) l
                d = Vector.foldVector (+) 0.0 expd
            in Vector.mapVector (/d) expd

        probs' = (Matrix.fromRows . map smallNorm . Matrix.toRows) probs
        totals = foldl1' (Vector.zipVectorWith (+)) (Matrix.toRows probs')

        accumMean comp = MatrixST.runSTVector (do
            mean' <- MatrixST.newVector (0.0 :: Double) nfeats 
            let accum o p = do
                    forM_ [0 .. nfeats-1] (\col ->
                        MatrixST.modifyVector mean' col 
                        (+ ((o Vector.@> col) * p / (totals Vector.@> comp))))
            forM_ (zip [0..] $ Matrix.toRows obs) (\(i, row) ->
                accum row (probs' Matrix.@@> (i, comp))) 
            return $! mean'
            )

        accumSigma comp mu = MatrixST.runSTMatrix (do
            sigma' <- MatrixST.newMatrix (0.0 :: Double) nfeats nfeats
            let accum o p = do
                    let s = o - mu --o `HM.outer` o
                    sequence $ (\r c -> MatrixST.modifyMatrix sigma' r c
                        (+ (s Vector.@> r * s Vector.@> c * p / 
                        totals Vector.@> comp)))
                        <$> [0 .. nfeats-1] <*> [0 .. nfeats-1] 
                    
            forM_ (zip [0..] $ Matrix.toRows obs) (\(i, row) ->
                accum row (probs' Matrix.@@> (i, comp))) 
            return $! sigma'
            )

        buildMeans [] = []
        buildMeans (c: rest) = 
            let mine = accumMean c
                theirs = buildMeans rest
            in par mine (pseq theirs (mine : theirs))
        means = buildMeans [0 .. ncomps-1]

        buildSigmas [] _  = []
        buildSigmas (c: rest) (mu: mus) = 
            let mine = accumSigma c mu
                theirs = buildSigmas rest mus
            in par mine (pseq theirs (mine : theirs))
        sigmas = buildSigmas [0 .. ncomps-1] means
    in gaussianMixture (components gmm) (map Vector.toList means) sigmas
            
    
em :: (Show a, Show b, Ord b) => Int -> [(HMM a b, Int)] -> GMM b -> 
    [[Double]] -> GMM b
em 0 _ gmm _ = gmm
em n hmm gmm obs =
    let phones =  map (gmmLogProb gmm) obs
        --phones = map (\o -> snd . maximum $ 
            --zip (gmmLogProb gmm o) (components gmm)) obs
        (newphones, totalprob) = viterbiList hmm phones
        --allemissions = trace (show totalprob) $ foldl1' (++) (map 
            --(\(h, i) -> replicate i (emissions h)) hmm)
        --newphones = -- trace ("phone " ++ show phones) $ 
            --zipWith (\ss emis -> map (\o -> logSum $ 
            --zipWith (\m s -> s + log (m Map.! o)) emis ss) 
            --(components gmm)) hmmstates allemissions
    in em (n-1) hmm (gmmUpdate gmm obs newphones) obs

emST :: (Show a, Show b, Ord b) => Int -> [(HMM a b, Int)] -> GMM b -> 
    Matrix Double -> GMM b
emST 0 _ gmm _ = gmm
emST n hmm gmm obs = gmm `seq`
    let phones =  Matrix.fromRows (map (gmmLogProbST gmm) (Matrix.toRows obs))
        --phones = map (\o -> snd . maximum $ 
            --zip (gmmLogProb gmm o) (components gmm)) obs
        (newphones', totalprob) = viterbiListST hmm phones
        newphones = trace (show n) $ Matrix.fromBlocks newphones'
        --allemissions = trace (show totalprob) $ foldl1' (++) (map 
            --(\(h, i) -> replicate i (emissions h)) hmm)
        --newphones = -- trace ("phone " ++ show phones) $ 
            --zipWith (\ss emis -> map (\o -> logSum $ 
            --zipWith (\m s -> s + log (m Map.! o)) emis ss) 
            --(components gmm)) hmmstates allemissions
    in emST (n-1) hmm (gmmUpdateST gmm obs newphones) obs


data Health = Healthy | Fever deriving (Show, Eq, Enum)
data Symptoms = Normal | Cold | Dizzy deriving (Show, Eq, Enum, Ord)

--st :: Health -> Double
--st Healthy = 0.6
--st Fever = 0.4

--trans :: Health -> Health -> Double
--trans Healthy Healthy = 0.7
--trans Healthy Fever = 0.3
--trans Fever Healthy = 0.4
--trans Fever Fever = 0.6

--emit :: Health -> Symptoms -> Double
--emit Healthy Normal = 0.5
--emit Healthy Cold = 0.4
--emit Healthy Dizzy = 0.1
--emit Fever Normal = 0.1
--emit Fever Cold = 0.3
--emit Fever Dizzy = 0.6

test :: IO ()
test = do
    --let hmm = HMM [Healthy, Fever] [Normal, Cold, Dizzy] st trans emit
    --let v = viterbi hmm [Normal, Cold, Dizzy]
    --print $ map (sequence v) [Healthy, Fever]
    
    let st x 
            | x == 0 = 1
            | otherwise = 0

    let nsamples = 3
    let trans i j 
            | i == nsamples-1 && j /= nsamples-1 = 0
            | j == i+1 = 0.1
            | i == j = 0.9
            | otherwise = 0

    let allemissions = [Normal, Cold, Dizzy]
    let emit i p 
            | p == allemissions !! i = 1.0--0.9
           | otherwise = 0.0 --0.05

    let hmm = HMM [0..nsamples-1] allemissions 
            (map st [0..nsamples-1])
            (map (mapM (flip trans) [0..nsamples-1]) [0..nsamples-1])
            (map (\s -> Map.fromList $ map (\o -> (o, emit s o))
                allemissions) [0..nsamples-1])

    let allemissions2 = [Dizzy, Cold, Normal]
    let emit2 i p 
            | p == allemissions2 !! i = 1.0--0.9
            | otherwise = 0.0--0.05

    let hmm2 = HMM [0..nsamples-1] allemissions 
            (map st [0..nsamples-1])
            (map (mapM (flip trans) [0..nsamples-1]) [0..nsamples-1])
            (map (\s -> Map.fromList $ map (\o -> (o, emit2 s o))
                allemissions) [0..nsamples-1])

    let ms = replicate nsamples $ replicate 2 5
    let ss = replicate nsamples $ HM.ident 2
    let gmm = gaussianMixture allemissions ms ss

    let perstate = 300
    obs1 <- replicateM perstate $ normalIO' (4, 2.1 ::Double)
    obs2 <- replicateM perstate $ normalIO' (6, 2.1)
    obs3 <- replicateM perstate $ normalIO' (8, 2.1)
    obs4 <- replicateM perstate $ normalIO' (10, 2.1)
    obs5 <- replicateM perstate $ normalIO' (12, 2.1)
    obs6 <- replicateM perstate $ normalIO' (14, 2.1)
    let listify x y = [x, y]
    let obs = zipWith listify obs1 obs4 ++ zipWith listify obs2 obs5 ++ zipWith listify obs3 obs6
    --let obs = map (:[]) obs'

    --let gmm2 = em 10 [(hmm,900), (hmm2,900)] gmm (obs ++ reverse obs)
    --let gmm2 = em 10 [(hmm,300)] gmm obs
    --print $ nds gmm2
    return ()



