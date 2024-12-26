import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerBase
import matplotlib.text as mtext
import os


def init_savefig(save_flag, base_folder):
    def savefig(fig, fn, **kwargs):
        if save_flag and base_folder is not None:
            fig.savefig(os.path.join(base_folder, fn), bbox_inches="tight", **kwargs)

    return savefig


class HandlerValue(HandlerBase):
    def __init__(self, text):
        self.text = text
        super().__init__()  # Ensure the base class is properly initialized

    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ):
        # Create a text object positioned at the center of the legend entry
        return [
            mtext.Text(
                x=width / 2,
                y=height / 2,
                text=self.text,
                fontsize=fontsize,
                ha="center",
                va="center",
                transform=trans,
            )
        ]
