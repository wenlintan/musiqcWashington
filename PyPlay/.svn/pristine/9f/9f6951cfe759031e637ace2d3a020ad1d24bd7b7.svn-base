
module Main where

--import System.IO
import Debug.Trace
import System.Environment (getArgs)

import System.Directory (doesFileExist)
import System.Directory.Tree
import System.FilePath

import GHC.Float
import GHC.Word
--import GHC.Int

import Data.Maybe (mapMaybe)
import Data.Map.Strict (Map)
import qualified Data.Map.Strict as Map

import Data.Set (Set)
import qualified Data.Set as Set

import Data.List
import qualified Data.ByteString.Lazy as B

--import Data.Vector (Vector)
--import qualified Data.Vector as Vector

--import Data.Matrix (Matrix)
--import qualified Data.Matrix as Matrix
import Data.Packed.Matrix (Matrix)
import qualified Data.Packed.Matrix as Matrix
import qualified Data.Packed.Vector as Vector
import qualified Numeric.LinearAlgebra.Data as HMData
import qualified Numeric.LinearAlgebra.HMatrix as HM

import Data.Binary.Get
import Data.Functor
import Control.Applicative
import Control.Monad
import Control.Arrow

--import Graphics.EasyPlot
import Features
import EM
import Predict

data WaveChunkHeader = WaveChunkHeader {
    chunkID :: B.ByteString,
    chunkSize :: Word32
    } deriving (Show, Eq)

data WaveFileHeader = WaveFileHeader {
    headerChunkHeader :: WaveChunkHeader,
    format :: B.ByteString
    } deriving (Show, Eq)

data WaveFileFormat = WaveFileFormat {
    formatChunkHeader :: WaveChunkHeader,
    audioFormat :: Word16,
    numChannels :: Word16,
    sampleRate :: Word32,
    byteRate :: Word32,
    blockAlign :: Word16,
    bitsPerSample :: Word16
    } deriving (Show, Eq)

data WaveFileData = WaveFileData {
    dataChunkHeader :: WaveChunkHeader,
    fileData :: [Float]
    }

getWaveChunkHeader :: Get WaveChunkHeader
getWaveChunkHeader = WaveChunkHeader <$> getLazyByteString 4 <*> getWord32le

getWaveFileHeader :: Get WaveFileHeader
getWaveFileHeader = WaveFileHeader <$> getWaveChunkHeader <*>
    getLazyByteString 4

getWaveFileFormat :: Get WaveFileFormat
getWaveFileFormat = WaveFileFormat <$> getWaveChunkHeader <*>
    getWord16le <*> getWord16le <*> getWord32le <*> getWord32le <*>
    getWord16le <*> getWord16le

getWaveFileData :: Get WaveFileData
getWaveFileData = do
    chunkHeader <- getWaveChunkHeader
    let nsamples = floor ((fromIntegral . chunkSize) 
            chunkHeader / 2 :: Double) --16 bit
    samples <- map fromIntegral <$> replicateM nsamples getWord16le
    let resign x 
            | x > 2**15 = x - 2**16
            | otherwise = x

    let samples' = map resign samples
    return $! WaveFileData chunkHeader samples'

getWaveFile :: Get (WaveFileHeader, WaveFileFormat, WaveFileData)
getWaveFile = (,,) <$> getWaveFileHeader <*> 
    getWaveFileFormat <*> getWaveFileData

readWaveFile :: FilePath -> IO (WaveFileHeader, WaveFileFormat, WaveFileData)
readWaveFile filename = do
    contents <- B.readFile filename
    return (runGet getWaveFile contents)

type Phoneme = String
readPhonemes :: String -> IO [Phoneme]
readPhonemes filename = lines <$> readFile filename

type Dictionary = Map String [Phoneme]
readDictionary :: String -> IO Dictionary
readDictionary filepath = do
    fdata <- lines <$> readFile filepath
    return $ foldl parseDictionaryLine Map.empty fdata

parseDictionaryLine :: Dictionary -> String -> Dictionary
parseDictionaryLine m s =
    if ";;;" `isPrefixOf` s then m
    else Map.insert (head $ words s) ((++) <$> (tail $ words s) <*>
        ["1", "2", "3"]) m

data Prompt = Prompt {
    promptFilename :: String,
    promptText :: String,
    promptPhonemes :: [Phoneme] }
    deriving (Show, Eq)

readPrompts :: Dictionary -> DirTree String -> [Prompt]
readPrompts m (Dir _ c) = foldr1 (++) (map (readPrompts m) c)
readPrompts m (File filename c) 
    | "PROMPTS" `isSuffixOf` filename = mapMaybe (parsePrompt m) (lines c)
    | otherwise = []
readPrompts _ _ = []

parsePrompt :: Dictionary -> String -> Maybe Prompt
parsePrompt dictionary contents = 
    let cwords = words contents
        filename = splitPath (head cwords)
        fixedname = normalise $ addExtension (
            joinPath (take (length filename-2) filename ++ "wav" : 
            drop (length filename-1) filename)) "wav"
        prompt = unwords (tail cwords)
        allphonemes = mapM (`Map.lookup` dictionary) (tail cwords)
        phonemes = liftM (("SIL" :) . (++ ["SIL"])) .  liftM (foldl1 
            (++)) $ allphonemes
    in liftM (Prompt fixedname prompt) phonemes

buildHMM :: [Phoneme] -> String -> HMM Int Phoneme
buildHMM all_phonemes phonemes = hmm
    where
        nphonemes = length all_phonemes
        nstates = length (words phonemes)
        st x 
            | x == 0 = 1
            | otherwise = 0

        trans i j 
            | i == nstates-1 && j /= nstates-1 = 0
            | j == i+1 = 0.1
            | i == j = 0.9
            | otherwise = 0

        emit i p 
            -- | (i == 0 || i == nstates-1) && p == "SIL" = 1.0
            -- | i > 0 && i < (nstates-1) && p == words phonemes !! (i-1) = 1.0
            | p == words phonemes !! i = 1.0
            -- | p == "SIL" = 0.1
            | otherwise = 0.0 -- 0.1 / fromIntegral nphonemes

        hmm = HMM [0..nstates-1] all_phonemes 
            (map st [0..nstates-1])
            (map (mapM (flip trans) 
                [0..nstates-1]) [0..nstates-1])
            (map (\s -> Map.fromList $ map (\o -> (o, emit s o))
                all_phonemes) [0..nstates-1])

buildGMM :: [Phoneme] -> Int -> GMM Phoneme
buildGMM all_phonemes nfilters = gmm
    where
        nphonemes = length all_phonemes
        ms = replicate nphonemes $ replicate nfilters 0.0
        ss = replicate nphonemes $ 
            HM.scale 1.0 (HM.ident nfilters) 
        gmm = gaussianMixture all_phonemes ms ss

saveGMM :: FilePath -> GMM Phoneme -> IO ()
saveGMM path gmm = do
    let disp = HM.dispf 6
        phones = components gmm
        mus = map (show . Vector.toList . mu) (nds gmm)
        ss = map (show . sigma) (nds gmm)
        dat = foldl1' (++) (zipWith3 (\phone m s -> unlines [phone, m, s]) 
            phones mus ss)
    writeFile path dat

loadGMM :: FilePath -> IO (GMM Phoneme)
loadGMM path = do
    contents <- liftM lines $ readFile path
    let fn :: [String] -> ([String], [[Double]], [Matrix Double])
        fn (phone:m:rest) = 
            let m' = read m :: [Double]
                s' = read $ unlines (take 13 rest) :: Matrix Double
                (ps, ms, ss) = fn (drop 13 rest)
            in (phone:ps, m':ms, s':ss)
        fn [] = ([], [], [])
        (phones, mus, ss) = fn contents
    return $ gaussianMixture phones mus ss

--type Dataset = [[Double]]
type Dataset = Matrix Double

wrapDataset :: [[Double]] -> Dataset
--wrapDataset = id
wrapDataset = Matrix.fromLists

combineDataset :: Dataset -> Dataset -> Dataset
--combineDataset = (++)
combineDataset = (HMData.——)

nfeaturesDataset :: Dataset -> Int
--nfeaturesDataset = length . (!! 0)
nfeaturesDataset = Matrix.cols

nobservationsDataset :: Dataset -> Int
--nobservationsDataset = length
nobservationsDataset = Matrix.rows

readFeatures :: String -> IO (Dataset) 
readFeatures filename = do
    contents <- trace filename $ readFile filename
    let dataset = wrapDataset (map (map read . words) . lines $ contents)
    dataset `seq` return dataset

buildFeatures :: String -> String -> IO (Dataset)
buildFeatures filename cachename = do
    print ("Processing file " ++ filename)

    (_, file_format, file_data) <- readWaveFile filename
    let window = 0.025  --in seconds
    let step = 0.010

    let nsamples = length $ fileData file_data
    let sample_rate = fromIntegral $ sampleRate file_format
    let samples_window = floor $ sample_rate * window
    let samples_step = floor $ sample_rate * step
    let nwindows = floor $ 
            (fromIntegral (nsamples - samples_window) :: Double) / 
            fromIntegral samples_step

    let nfilters = 26
    let filters = melFilters nfilters samples_window sample_rate 300 8000

    let samples i = take samples_window . drop (i*samples_step) . fileData
    let alldata = map (\n -> mfcc (samples n file_data) filters) [0..nwindows-1]
        
    --writeFile "powers.txt" $ unlines (map (show . fst) alldata)
    --let alldata' = filter (\(p, _) -> p > 225) alldata
    let doubledata = map (take 12 . map float2Double . snd) alldata
    let dataset = wrapDataset (take (nwindows-40) (drop 20 doubledata))
    let mean = HM.scale (-1.0 / 10) $ 
            foldl1' (+) (take 10 $ Matrix.toRows dataset)
    let dataset' = Matrix.fromRows (map (+mean) $ Matrix.toRows dataset)
    writeFile cachename $ (unlines . map (unwords . map show)) 
        (Matrix.toLists dataset')
    return dataset'

getFeatures :: String -> IO (Dataset)
getFeatures filename = do
    let cache = replaceExtension filename "bin"
    let cache' = replaceBaseName cache (foldl1' (++) 
            (splitDirectories cache) ++ takeBaseName cache)
    let cache'' = replaceDirectory cache' "cache" 
    fileexists <- doesFileExist cache''
    if fileexists 
        then readFeatures cache''
        else buildFeatures filename cache''

buildHMMList :: [Phoneme] -> [Prompt] -> 
    IO ([(HMM Int Phoneme, Int)], [Dataset])
buildHMMList phonemes (prompt: rest) = do
    let hmm = buildHMM phonemes (unwords $ promptPhonemes prompt)
    obs <- getFeatures (promptFilename prompt)
    let new_item = (hmm, nobservationsDataset obs) 
    (rest_items, all_obs) <- buildHMMList phonemes rest
    return (new_item:rest_items, obs : all_obs)
buildHMMList phonemes [] = return ([], [])

main :: IO()
main = do
    args <- getArgs
    let dir = head args --"..\\..\\Data\\"
    let dict = combine dir "dictionary" --dir ++ "dictionary\\"
    let speech = dir `combine` "speech" `combine` "voxforge-snapshot" --dir ++ "speech\\voxforge-snapshot\\"

    phonemes <- readPhonemes (dict `combine` "cmudict.0.7a.symbols")
    dictionary <- readDictionary (dict `combine` "cmudict.0.7a")

    let rebase (Prompt filename prompt phonemes) =
            Prompt (speech `combine` filename) prompt phonemes
    speech_tree <- readDirectoryWithL readFile speech
    let prompts = map rebase (readPrompts dictionary $ dirTree speech_tree)
    
    let nprompts = read (args !! 1) :: Int
    let prompts' = take nprompts prompts
    let phones = Set.toList $ foldr1 Set.union ((map (Set.fromList . 
            promptPhonemes))  prompts')
    let counts = map (\p -> length $ filter (==p) (foldr1 (++) $
            map promptPhonemes prompts')) phones
    print $ zip phones counts

    (hmms, obs') <- buildHMMList phones prompts'
    let obs = foldl1' combineDataset obs'
    
    print $ nobservationsDataset obs
    let gmm' = buildGMM phones (nfeaturesDataset obs)

    let gmm = emST 2 hmms gmm' obs
    saveGMM "data.txt" gmm

    --gmm'' <- loadGMM "data.txt"
    --print $ (\(Prompt _ _ ps) -> ps) (head prompts')
    --print $ predictSimple gmm'' (head obs')
    --print $ ((!! 0) . Matrix.toColumns) (head obs')
    
    --let gmm2 = em 3 hmms gmm obs
    --writeFile "data2.txt" $ unlines (zipWith4 (\i j k l ->
        --unlines [i, j, k, l]) phones (map show counts)
            --((map 
                --(unlines . tail . lines . HM.dispf 6 . mu)) (nds gmm2))
            --((map
                --(unlines . tail . lines . HM.dispf 6 . sigma)) (nds gmm2)))
        
    --let gmm3 = em 3 hmms gmm2 obs
    --writeFile "data3.txt" $ unlines (zipWith4 (\i j k l ->
        --unlines [i, j, k, l]) phones (map show counts)
            --((map 
                --(unlines . tail . lines . HM.dispf 6 . mu)) (nds gmm3))
            --((map
                --(unlines . tail . lines . HM.dispf 6 . sigma)) (nds gmm3)))
        

    
