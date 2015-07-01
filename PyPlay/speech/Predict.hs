
module Predict (predictSimple) where

import Control.Monad
import Control.Applicative

import Data.Map (Map)
import qualified Data.Map as Map
import Data.Tuple (swap)

import Data.Packed.Matrix (Matrix)
import qualified Data.Packed.Matrix as Matrix
import Data.Packed.Vector (Vector)
import qualified Data.Packed.Vector as Vector
import qualified Data.Packed.ST as MatrixST

import qualified Numeric.LinearAlgebra.Data as HMData
import qualified Numeric.LinearAlgebra.HMatrix as HM

import EM (GMM, components, gmmLogProbST)

type Phoneme = String
type Successor = [Phoneme] -> Phoneme -> Double

--buildSuccessors :: [Phoneme] -> Successor
--buildSuccessors words = 

predict :: GMM Phoneme -> Matrix Double -> Successor -> [Phoneme]
predict gmm obs succ = []

predictSimple :: GMM Phoneme -> Matrix Double -> [Phoneme]
predictSimple gmm obs =
	let	probs = map (gmmLogProbST gmm) (Matrix.toRows obs)
		phones = map ((components gmm !!) . HMData.maxIndex) probs
	in phones

data Trie a = Trie {
    value :: Maybe a,
    children :: Map Phoneme (Trie a)
    }

empty :: Trie a
empty = Trie Nothing Map.empty

insert :: Trie a -> ([Phoneme], a) -> Trie a
insert trie ((key:rest), val) = Trie (value trie) $
    Map.insert key (insert (children trie Map.! key) (rest, val)) 
		(children trie) 
insert trie ([], val) = Trie (Just val) (children trie)

maptrie :: (a -> b) -> Trie a -> Trie b
maptrie fn (Trie val map) = Trie (fn <$> val) (fmap (fn <$>) map)

instance Functor Trie where
    fmap = maptrie

buildPhonemeTrie :: Map String [Phoneme] -> Trie String
buildPhonemeTrie dictionary = foldl insert Predict.empty 
	(map swap $ Map.assocs dictionary)

predictTrie :: GMM Phoneme -> Map String [Phoneme] -> Matrix Double -> [Phoneme]
predictTrie gmm dict obs =
    let probs = map (gmmLogProbST gmm) (Matrix.toRows obs)
        trie = buildPhonemeTrie dict
	in []

