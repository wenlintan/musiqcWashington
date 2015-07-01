
module Features where 

import Debug.Trace
import Data.Complex 
import Control.Applicative ()


fft :: [Float] -> [Complex Float]
fft samples = map (sum . sequence freq_component) [0 .. nsamples-1]
	where 	
		nsamples = length samples
		w = 0 :+ (-2) * pi / fromIntegral nsamples
		fft' n x k = (x:+0) * exp (w * (n * fromIntegral k :+ 0))
		freq_component = zipWith fft' [0..] samples 

dct :: [Float] -> [Float]
dct samples = map (sum . sequence freq_component) [0 .. nsamples-1]
	where 	
		nsamples = length samples
		w = pi / fromIntegral nsamples
		dct' n x k = x * cos (w * (n + 0.5) * fromIntegral k)
		freq_component = zipWith dct' [0..] samples 

mel :: Float -> Float
mel x = 1125 * log (1 + x / 700)

imel :: Float -> Float
imel x = 700 * (exp (x / 1125) - 1)

triangleWindow :: Float -> Float -> Float -> Float -> Float
triangleWindow fmin fcent fmax k 
		| k < fmin = 0
		| k < fcent = (k - fmin) / (fcent - fmin)
		| k < fmax = (fmax - k) / (fmax - fcent)
		| otherwise = 0

hammingWindow :: Float -> Float -> Float
hammingWindow nsamples x = 
	0.54 - 0.46 * cos (2*pi * x / (nsamples-1))

melFilters :: Int -> Int -> Float -> Float -> Float -> [[Float]]
melFilters n nffts sample_rate min_freq max_freq =
	let	min_mel = mel min_freq
		max_mel = mel max_freq
		step_size = (max_mel - min_mel) / (fromIntegral n + 1)
		mels = [min_mel + step_size * fromIntegral x | x <- [0 .. n+1]]
		fs = map imel mels
		bin = (fromIntegral nffts+1) / sample_rate
		fbins = map ((fromIntegral :: Int->Float) . floor . (*bin)) fs
		filters = zipWith3 triangleWindow fbins (drop 1 fbins) (drop 2 fbins)
	in map (flip map $ map fromIntegral [0 .. nffts-1]) filters	

mfcc :: [Float] -> [[Float]] -> (Float, [Float])
mfcc samples filters = 
	let	nsamples = (fromIntegral . length) samples
		sfilter = map (hammingWindow nsamples) [0..nsamples-1]
		freqs = fft $ zipWith (*) sfilter samples
		powers = map ((/nsamples) . (**2) . magnitude) freqs
		logbanks = map (log . sum . zipWith (*) powers) filters 
		lifter_coeff = 22.0
		lifter n = 1 + (lifter_coeff / 2) * sin (pi * n / lifter_coeff) 
		lifters = map lifter [0 .. fromIntegral $ length filters]
	in (sum logbanks, zipWith (*) (dct logbanks) lifters)
		
--main =
	--plot' [Interactive] Windows $
		--map (Data2D [Style Lines] [] . zip [0..129]) 
		--(mel_filters 10 256 8000 30 4000)
