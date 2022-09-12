from typing import Optional, Union, List
from torch.optim import Adam
import pytorch_lightning as pl

from enhancer.data.dataset import Dataset
from enhancer.utils.loss import Avergeloss


class Model(pl.LightningModule):

    def __init__(
        self,
        num_channels:int=1,
        sampling_rate:int=16000,
        lr:float=1e-3,
        dataset:Optional[Dataset]=None,
        loss: Union[str, List] = "mse"
    ):
        super().__init__()
        assert num_channels ==1 , "Enhancer only support for mono channel models"
        self.save_hyperparameters("num_channels","sampling_rate","lr","loss")
        self.dataset = dataset
        
    
    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self,dataset):
        self._dataset = dataset

    def setup(self,stage:Optional[str]=None):
        if stage == "fit":
            self.dataset.setup(stage)
            self.dataset.model = self
            self.setup_loss() 
        
    def setup_loss(self):

        loss = self.hparams.loss
        if isinstance(loss,str):
            losses = [loss]
        
        self.loss =  Avergeloss(losses)

    def train_dataloader(self):
        return self.dataset.train_dataloader()

    def val_dataloader(self):
        return self.dataset.val_dataloader()

    def configure_optimizers(self):
        return Adam(self.parameters(), lr = self.hparams.lr)

    def training_step(self,batch, batch_idx:int):

        mixed_waveform = batch["noisy"]
        target = batch["clean"]
        prediction = self(mixed_waveform)

        loss = self.loss(prediction, target)

        return {"loss":loss}


    @classmethod
    def from_pretrained(cls,):
        pass