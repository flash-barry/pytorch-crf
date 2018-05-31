"""Implements a character-sequence LSTM to generate words features."""

from typing import List

import torch
import torch.nn as nn
from torch.nn import LSTM


class CharLSTM(nn.Module):
    """
    Character LSTM for generating word features from the final hidden state.

    Parameters
    ----------
    n_chars : int
        The number of characters in the vocabularly, i.e. the input size.

    hidden_size : int
        The number of features in the hidden state of the LSTM cells.

    bidirectional : bool, optional (default: True)
        If true, becomes a bidirectional LSTM.

    layers : int, optional (default: 1)
        The number of cell layers.

    dropout : float, optional (default: 0.)
        The dropout probability for the recurrent layer.

    Attributes
    ----------
    n_chars : int
        The number of characters in the vocabularly, i.e. the input size.

    output_size : int
        The dimension of the output, which is
        ``layers * hidden_size * directions``.

    rnn : torch.nn
        The LSTM layer.

    """

    def __init__(self,
                 n_chars: int,
                 hidden_size: int,
                 bidirectional: bool = True,
                 layers: int = 1,
                 dropout: float = 0.) -> None:
        super(CharLSTM, self).__init__()

        self.n_chars = n_chars
        self.output_size = layers * hidden_size
        if bidirectional:
            self.output_size *= 2

        self.rnn = LSTM(input_size=self.n_chars,
                        hidden_size=hidden_size,
                        num_layers=layers,
                        batch_first=True,
                        dropout=dropout,
                        bidirectional=bidirectional)

    def forward(self, inputs: List[torch.Tensor]) -> torch.Tensor:
        """
        Make a forward pass through the network.

        Parameters
        ----------
        inputs : List[torch.Tensor]
            List of tensors of shape ``[word_length x n_chars]``.

        Returns
        -------
        torch.Tensor
            The last hidden states:
            ``[len(inputs) x (layers * directions * hidden_size)]``

        """
        # pylint: disable=arguments-differ
        hiddens = []
        for word in inputs:
            _, state = self.rnn(word.unsqueeze(0))
            hidden = state[0]
            # hidden: ``[(layers * directions) x 1 x hidden_size]``

            # Get rid of batch_size dimension.
            hidden = hidden.squeeze()
            # hidden: ``[(layers * directions) x hidden_size]``

            # Concatenate forward/backward hidden states.
            hidden = hidden.view(-1).unsqueeze(0)
            # hidden: ``[1 x (layers * directions * hidden_size)]``.

            hiddens.append(hidden)

        # Concat list into tensor.
        hiddens = torch.cat(hiddens, dim=0)
        # hiddens: ``[words x (layers * directions * hidden_size)]``

        return hiddens