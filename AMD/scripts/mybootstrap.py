# Código slides - prof. Paulo Trigo

from sklearn.utils import resample
# we also need to “score” the model
from sklearn.metrics import accuracy_score, precision_score, recall_score
# abc = Abstract Base Classes
from abc import ABC, abstractmethod
# abstract class that defines general behavior:
# - split and score

class MyBootstrap( ABC ):
    @abstractmethod
    def get_seed(): pass
    
    def __init__( self, seed=None ):
        self.seed = seed
        self.reset_tt_split_indexes()

    def reset_tt_split_indexes( self ):
        self.tt_split_indexes = None


    def split( self, X, y=None ):
        # if train|test split already exists, then return
        if self.tt_split_indexes != None: return self.tt_split_indexes

        #_____________________________
        # build a new train|test split
        dim_dataset = len( X )
        indexes = list( range( dim_dataset ) )

        # training set is created from resamples (samples with reposition)
        # n_samples = number of samples to generate; None means “the size of dataset”
        seed = self.get_seed()
        train_indexes = resample( indexes, n_samples=None, random_state=seed )

        #testing set is created from individuals, i, not in training set
        test_indexes = [i for i in indexes if i not in train_indexes]
        self.tt_split_indexes = [ ( train_indexes, test_indexes ) ]
        return self.tt_split_indexes
    



class MyBootstrapSplitOnce( MyBootstrap ):
    def get_seed( self ):
        return self.seed
    
class MyBootstrapSplitRepeated( MyBootstrap ):
    def __init__( self, n_repeat, seed=None ):
        super().__init__( seed )
        self.n_repeat = n_repeat
        self.tt_split_repeated_indexes = None


    def get_seed( self ):
        seed_current = self.seed
        if self.seed != None: self.seed = self.seed + 1
        return seed_current
    

    def split( self, X, y=None ):
        # if train|test split-repeated already exists, then return
        if self.tt_split_repeated_indexes != None:
            return self.tt_split_repeated_indexes
    
        # build a new train|test split-repeated
        self.tt_split_repeated_indexes = list()
        for i in range( self.n_repeat ):
            self.reset_tt_split_indexes()
            self.tt_split_repeated_indexes = self.tt_split_repeated_indexes + \
            super().split( X )

        return self.tt_split_repeated_indexes